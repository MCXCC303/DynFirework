"""项目设置对话框 按后端过滤可选 MC 版本."""
from __future__ import annotations

import logging

from PySide6.QtWidgets import (
	QDialog, QFormLayout, QLineEdit, QDoubleSpinBox, QComboBox, QDialogButtonBox, QLabel,
)

from dyn.ui.dialogs.project_creation_dialog import BACKEND_MC_VERSIONS

log = logging.getLogger(__name__)

class ProjectSettingsDialog(QDialog):
	"""编辑项目名称、BPM 和 Minecraft 版本 版本列表按后端过滤."""

	def __init__(self, name: str = "Untitled", bpm: float = 120.0,
	             mc_version: str = "1.20.1", backend: str = "df", parent=None) -> None:
		super().__init__(parent)
		self.setWindowTitle("项目设置")
		form = QFormLayout(self)

		self.edit_name = QLineEdit(name)
		form.addRow("项目名称:", self.edit_name)

		self.spin_bpm = QDoubleSpinBox()
		self.spin_bpm.setRange(20, 300)
		self.spin_bpm.setValue(bpm)
		form.addRow("BPM:", self.spin_bpm)

		form.addRow("模组后端:", QLabel("ColorBlock (ParticleEx)" if backend == "cb" else "DynFireworkMod v2.0"))

		self.combo_mc_version = QComboBox()
		versions = BACKEND_MC_VERSIONS.get(backend, BACKEND_MC_VERSIONS["df"])
		self.combo_mc_version.addItems(versions)
		idx = self.combo_mc_version.findText(mc_version)
		if idx >= 0:
			self.combo_mc_version.setCurrentIndex(idx)
		elif versions:
			self.combo_mc_version.setCurrentIndex(0)
		form.addRow("Minecraft 版本:", self.combo_mc_version)

		btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
		btns.accepted.connect(self.accept)
		btns.rejected.connect(self.reject)
		form.addRow(btns)

		log.debug(f"打开项目设置: name={name}, bpm={bpm}")

	def accept(self) -> None:
		log.debug("项目设置对话框: 用户确认")
		super().accept()

	def reject(self) -> None:
		log.debug("项目设置对话框: 用户取消")
		super().reject()

	@property
	def project_name(self) -> str:
		return self.edit_name.text().strip()

	@property
	def bpm(self) -> float:
		return self.spin_bpm.value()

	@property
	def mc_version(self) -> str:
		return self.combo_mc_version.currentText()
