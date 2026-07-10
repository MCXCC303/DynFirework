"""位置选择器独立撤销/重做命令."""

from __future__ import annotations

from PySide6.QtGui import QUndoCommand

from dyn.lib.units import MinecraftPosition

class AddPointCommand(QUndoCommand):
	"""添加点."""

	def __init__(
			self,
			point_list: list[MinecraftPosition],
			fastsearch: set,
			point: MinecraftPosition,
			parent: QUndoCommand | None = None,
	) -> None:
		super().__init__("添加位置点", parent)
		self._point_list = point_list
		self._fastsearch = fastsearch
		self._point = point

	def undo(self) -> None:
		self._point_list.remove(self._point)
		self._fastsearch.discard((self._point.x, self._point.z))

	def redo(self) -> None:
		self._point_list.append(self._point)
		self._fastsearch.add((self._point.x, self._point.z))

class RemovePointCommand(QUndoCommand):
	"""删除点."""

	def __init__(
			self,
			point_list: list[MinecraftPosition],
			fastsearch: set,
			point: MinecraftPosition,
			parent: QUndoCommand | None = None,
	) -> None:
		super().__init__("删除位置点", parent)
		self._point_list = point_list
		self._fastsearch = fastsearch
		self._point = point

	def undo(self) -> None:
		self._point_list.append(self._point)
		self._fastsearch.add((self._point.x, self._point.z))

	def redo(self) -> None:
		self._point_list.remove(self._point)
		self._fastsearch.discard((self._point.x, self._point.z))

class EditPointCommand(QUndoCommand):
	"""编辑点属性."""

	def __init__(
			self,
			point: MinecraftPosition,
			old_vals: dict,
			new_vals: dict,
			fastsearch: set | None = None,
			parent: QUndoCommand | None = None,
	) -> None:
		super().__init__("编辑位置点", parent)
		self._point = point
		self._old_vals = old_vals
		self._new_vals = new_vals
		self._fastsearch = fastsearch

	def undo(self) -> None:
		self._apply(self._old_vals)

	def redo(self) -> None:
		self._apply(self._new_vals)

	def _apply(self, vals: dict) -> None:
		if self._fastsearch is not None:
			self._fastsearch.discard((int(self._point.x), int(self._point.z)))
		if "x" in vals:
			self._point.x = vals["x"]
		if "y" in vals:
			self._point.y = vals["y"]
		if "z" in vals:
			self._point.z = vals["z"]
		if "label" in vals:
			self._point.label = vals["label"]
		if "color" in vals:
			self._point._main_color = vals["color"]
		if self._fastsearch is not None:
			self._fastsearch.add((int(self._point.x), int(self._point.z)))
