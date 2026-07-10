"""检查器面板 — 以只读 JSON 显示当前选中元素."""

from __future__ import annotations

import json
import logging

from PySide6.QtWidgets import QWidget, QVBoxLayout, QPlainTextEdit, QLabel
from PySide6.QtCore import Qt

from dyn.models.elements import Element

log = logging.getLogger("dyn.components.inspector")


class Inspector(QWidget):
    """只读 JSON 检查器，显示选中元素的完整属性."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        self._label = QLabel("检查器")
        layout.addWidget(self._label)

        self._editor = QPlainTextEdit()
        self._editor.setReadOnly(True)
        self._editor.setPlaceholderText("未选中任何元素")
        font = self._editor.font()
        font.setPointSize(11)
        self._editor.setFont(font)
        layout.addWidget(self._editor)

    def show_element(self, element: Element | None) -> None:
        if element is None:
            log.debug("检查器: 清空")
            self._editor.setPlainText("")
            self._editor.setPlaceholderText("未选中任何元素")
            self._label.setText("检查器")
            return

        log.debug(f"检查器: 显示元素 id={element.id}, name={element.name}, type={element.element_type.name}, tick={element.start_tick}")
        json_str = element.to_json()
        formatted = json.dumps(json_str, ensure_ascii=False, indent=2)
        log.debug(f"  数据大小: {len(formatted)} 字符")
        self._editor.setPlainText(formatted)
        self._label.setText(f"检查器 — {element.name}")

    def refresh(self, element: Element | None) -> None:
        """与 show_element 相同，用于外部刷新."""
        self.show_element(element)

    def clear(self) -> None:
        self.show_element(None)
