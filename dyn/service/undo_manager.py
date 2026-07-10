"""全局撤销/重做管理器   基于 QUndoStack."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QUndoCommand, QUndoStack

from dyn.logging_config import get_logger
from dyn.models.elements import Element

log = get_logger(__name__)

def _elem_tick_state(elem: Element | None) -> str:
	"""返回元素的关键 tick 状态字符串，用于 undo/redo 日志."""
	if elem is None:
		return "elem=None"
	parts = [f"id={elem.id[:8]}", f"name={elem.name}", f"start={elem.start_tick}"]
	if hasattr(elem, 'traj_duration_ticks') and hasattr(elem, 'fw_duration_ticks'):
		# TrajFireworkElement
		parts.append(f"traj_dur={elem.traj_duration_ticks}")
		parts.append(f"fw_dur={elem.fw_duration_ticks}")
		parts.append(f"traj_end={elem.start_tick + elem.traj_duration_ticks}")
		parts.append(f"fw_end={elem.start_tick + elem.traj_duration_ticks + elem.fw_duration_ticks}")
	else:
		parts.append(f"dur={elem.duration_ticks}")
		parts.append(f"end={elem.end_tick}")
	return " ".join(parts)

class ElementPropertyCommand(QUndoCommand):
	def __init__(self, controller, element_id: str, key: str,
	             old_value: Any, new_value: Any, description: str = "",
	             parent: QUndoCommand | None = None) -> None:
		super().__init__(description, parent)
		self._controller = controller
		self._element_id = element_id
		self._key = key
		self._old_value = old_value
		self._new_value = new_value

	def undo(self) -> None:
		elem_before = self._controller.get_element(self._element_id)
		log.debug(f"UNDO 执行: {self._key}={self._old_value} (当前值={getattr(elem_before, self._key, '?') if elem_before else '?'}) | 执行前: {_elem_tick_state(elem_before)}")
		self._controller.set_property(self._element_id, self._key, self._old_value)
		elem_after = self._controller.get_element(self._element_id)
		log.debug(f"UNDO 完成: {self._key}={self._old_value} | 执行后: {_elem_tick_state(elem_after)}")

	def redo(self) -> None:
		elem_before = self._controller.get_element(self._element_id)
		log.debug(f"REDO 执行: {self._key}={self._new_value} (当前值={getattr(elem_before, self._key, '?') if elem_before else '?'}) | 执行前: {_elem_tick_state(elem_before)}")
		self._controller.set_property(self._element_id, self._key, self._new_value)
		elem_after = self._controller.get_element(self._element_id)
		log.debug(f"REDO 完成: {self._key}={self._new_value} | 执行后: {_elem_tick_state(elem_after)}")

class AddElementCommand(QUndoCommand):
	def __init__(self, controller, element: Element,
	             parent: QUndoCommand | None = None) -> None:
		super().__init__("添加元素", parent)
		self._controller = controller
		self._element = element

	def undo(self) -> None:
		self._controller.remove_element(self._element.id)

	def redo(self) -> None:
		self._controller.add_element(self._element)

class RemoveElementCommand(QUndoCommand):
	def __init__(self, controller, element: Element,
	             parent: QUndoCommand | None = None) -> None:
		super().__init__("删除元素", parent)
		self._controller = controller
		self._element = element

	def undo(self) -> None:
		self._controller.add_element(self._element)

	def redo(self) -> None:
		self._controller.remove_element(self._element.id)

class UndoManager(QObject):
	can_undo_changed = Signal(bool)
	can_redo_changed = Signal(bool)
	undo_text_changed = Signal(str)
	redo_text_changed = Signal(str)

	def __init__(self, controller, parent: QObject | None = None) -> None:
		super().__init__(parent)
		self._controller = controller
		self._stack = QUndoStack(self)
		self._stack.canUndoChanged.connect(self.can_undo_changed)
		self._stack.canRedoChanged.connect(self.can_redo_changed)
		self._stack.undoTextChanged.connect(self.undo_text_changed)
		self._stack.redoTextChanged.connect(self.redo_text_changed)

	@property
	def can_undo(self) -> bool: return self._stack.canUndo()

	@property
	def can_redo(self) -> bool: return self._stack.canRedo()

	@property
	def undo_text(self) -> str: return self._stack.undoText()

	@property
	def redo_text(self) -> str: return self._stack.redoText()

	def push_property_change(self, element_id: str, key: str,
	                         old_value: Any, new_value: Any) -> None:
		log.debug(f"undo push: id={element_id}, {key}: {old_value} → {new_value}")
		self._stack.push(ElementPropertyCommand(
			self._controller, element_id, key, old_value, new_value,
			description=f"修改 {key}"))

	def push_add_element(self, element: Element) -> None:
		self._stack.push(AddElementCommand(self._controller, element))

	def push_remove_element(self, element: Element) -> None:
		self._stack.push(RemoveElementCommand(self._controller, element))

	def begin_macro(self, name: str) -> None:
		"""开始宏   后续 push 操作合并为一个撤销步骤."""
		log.debug(f"undo 宏开始: '{name}' (栈深度: {self._stack.count()})")
		self._stack.beginMacro(name)

	def end_macro(self) -> None:
		"""结束宏   提交合并的撤销步骤."""
		self._stack.endMacro()
		# 宏提交后输出当前所有元素的 tick 状态，便于对比撤销前后的值
		states = [_elem_tick_state(self._controller.get_element(eid))
		          for eid in self._controller._elements]
		log.debug(f"undo 宏结束: count={self._stack.count()} | 元素状态: {states}")

	def undo(self) -> None:
		text = self._stack.undoText()
		# 在执行前采集所有元素的 tick 状态
		elems_before = {eid: _elem_tick_state(self._controller.get_element(eid))
		                for eid in self._controller._elements}
		log.debug(f"撤销: '{text}' | 执行前元素状态: {list(elems_before.values())}")
		self._stack.undo()
		elems_after = {eid: _elem_tick_state(self._controller.get_element(eid))
		               for eid in self._controller._elements}
		log.debug(f"撤销完成: '{text}' | 执行后元素状态: {list(elems_after.values())}")

	def redo(self) -> None:
		text = self._stack.redoText()
		elems_before = {eid: _elem_tick_state(self._controller.get_element(eid))
		                for eid in self._controller._elements}
		log.debug(f"重做: '{text}' | 执行前元素状态: {list(elems_before.values())}")
		self._stack.redo()
		elems_after = {eid: _elem_tick_state(self._controller.get_element(eid))
		               for eid in self._controller._elements}
		log.debug(f"重做完成: '{text}' | 执行后元素状态: {list(elems_after.values())}")

	def clear(self) -> None:
		log.debug("清空撤销栈")
		self._stack.clear()
