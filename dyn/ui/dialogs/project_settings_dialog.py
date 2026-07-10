"""项目设置对话框."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QDoubleSpinBox, QComboBox, QDialogButtonBox,
)


class ProjectSettingsDialog(QDialog):
    """编辑项目名称、BPM 和 Minecraft 版本."""

    def __init__(self, name: str = "Untitled", bpm: float = 120.0,
                 mc_version: str = "1.20.1", parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("项目设置")
        form = QFormLayout(self)

        self.edit_name = QLineEdit(name)
        form.addRow("项目名称:", self.edit_name)

        self.spin_bpm = QDoubleSpinBox()
        self.spin_bpm.setRange(20, 300)
        self.spin_bpm.setValue(bpm)
        form.addRow("BPM:", self.spin_bpm)

        self.combo_mc_version = QComboBox()
        self.combo_mc_version.addItems([
            "1.12.2", "1.16.5", "1.20.1", "1.20.4", "1.21",
        ])
        idx = self.combo_mc_version.findText(mc_version)
        if idx >= 0:
            self.combo_mc_version.setCurrentIndex(idx)
        self.combo_mc_version.setToolTip(
            "选择目标Minecraft版本\n"
            "1.12.2/1.16.5: ParticleEx (Colorblock模组)\n"
            "1.20.1/1.20.4/1.21: DynFirework Particles模组"
        )
        form.addRow("Minecraft 版本:", self.combo_mc_version)

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        form.addRow(btns)

    @property
    def project_name(self) -> str: return self.edit_name.text().strip()
    @property
    def bpm(self) -> float: return self.spin_bpm.value()
    @property
    def mc_version(self) -> str: return self.combo_mc_version.currentText()
