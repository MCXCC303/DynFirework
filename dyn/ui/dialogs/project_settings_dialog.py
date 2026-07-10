"""项目设置对话框."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QDoubleSpinBox, QDialogButtonBox,
)


class ProjectSettingsDialog(QDialog):
    """编辑项目 BPM 和名称."""

    def __init__(self, name: str = "Untitled", bpm: float = 120.0, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("项目设置")
        form = QFormLayout(self)

        self.edit_name = QLineEdit(name)
        form.addRow("项目名称:", self.edit_name)

        self.spin_bpm = QDoubleSpinBox()
        self.spin_bpm.setRange(20, 300)
        self.spin_bpm.setValue(bpm)
        form.addRow("BPM:", self.spin_bpm)

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        form.addRow(btns)

    @property
    def project_name(self) -> str: return self.edit_name.text().strip()
    @property
    def bpm(self) -> float: return self.spin_bpm.value()
