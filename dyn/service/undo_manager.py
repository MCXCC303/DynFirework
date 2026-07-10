"""全局撤销/重做管理器 — 基于 QUndoStack."""

from __future__ import annotations

import logging
from typing import Any

from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QUndoCommand, QUndoStack

from dyn.logging_config import get_logger
from dyn.models.elements import Element

log = get_logger(__name__)


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
        self._controller.set_property(self._element_id, self._key, self._old_value)

    def redo(self) -> None:
        self._controller.set_property(self._element_id, self._key, self._new_value)


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
        self._stack.push(ElementPropertyCommand(
            self._controller, element_id, key, old_value, new_value,
            description=f"修改 {key}"))

    def push_add_element(self, element: Element) -> None:
        self._stack.push(AddElementCommand(self._controller, element))

    def push_remove_element(self, element: Element) -> None:
        self._stack.push(RemoveElementCommand(self._controller, element))

    def undo(self) -> None:
        log.debug(f"撤销: {self._stack.undoText()}")
        self._stack.undo()
    def redo(self) -> None:
        log.debug(f"重做: {self._stack.redoText()}")
        self._stack.redo()
    def clear(self) -> None:
        log.debug("清空撤销栈")
        self._stack.clear()
