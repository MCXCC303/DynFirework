"""导出数据包对话框."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QSpinBox, QLabel, QDialogButtonBox,
)


class ExportDialog(QDialog):
    """收集数据包导出参数."""

    def __init__(self, default_name: str = "DynFirework", parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("导出数据包")
        self.setMinimumWidth(420)
        form = QFormLayout(self)

        self.edit_name = QLineEdit(default_name)
        form.addRow("数据包名称:", self.edit_name)

        self.edit_ns = QLineEdit("fireworks1")
        form.addRow("命名空间:", self.edit_ns)
        hint = QLabel("仅限小写字母、数字、下划线和点")
        hint.setStyleSheet("color: #888; font-size: 11px;")
        form.addRow("", hint)

        self.edit_desc = QLineEdit("DynFirework generated datapack")
        form.addRow("描述:", self.edit_desc)

        self.spin_format = QSpinBox()
        self.spin_format.setRange(1, 61)
        self.spin_format.setValue(15)
        self.spin_format.setToolTip(
            "数据包格式号（根据MC版本自动设置）\n"
            "1.12.2=4, 1.16.5=6, 1.20.1=15, 1.20.4=18, 1.21=48"
        )
        form.addRow("Pack Format:", self.spin_format)

        self.label_backend = QLabel("DynFirework Particles (/dfp)")
        self.label_backend.setStyleSheet("color: #888; font-size: 11px;")
        form.addRow("命令后端:", self.label_backend)

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        form.addRow(btns)

    def set_pack_format(self, value: int) -> None:
        """预设 pack_format 值（根据MC版本推导）."""
        self.spin_format.setValue(value)

    def set_backend_info(self, text: str) -> None:
        """显示当前后端信息."""
        self.label_backend.setText(text)

    @property
    def pack_name(self) -> str: return self.edit_name.text().strip()
    @property
    def namespace(self) -> str: return self.edit_ns.text().strip()
    @property
    def description(self) -> str: return self.edit_desc.text().strip()
    @property
    def pack_format(self) -> int: return self.spin_format.value()
