"""新建项目对话框 收集名称、后端、MC版本、BPM."""
from __future__ import annotations

import logging

from PySide6.QtWidgets import (
	QDialog, QFormLayout, QLineEdit, QDoubleSpinBox, QComboBox, QDialogButtonBox,
)

log = logging.getLogger(__name__)

# 后端 -> 可选 MC 版本列表
BACKEND_MC_VERSIONS: dict[str, list[str]] = {
	"cb": ["1.12.2", "1.16.5"],
	"df": ["1.20.1", "1.20.4", "1.21", "1.21.8"],
}

BACKEND_LABELS: dict[str, str] = {
	"cb": "ColorBlock (ParticleEx)",
	"df": "DynFireworkMod v2.0",
}

class ProjectCreationDialog(QDialog):
	"""收集新建项目参数 后端锁定后不可更改."""

	def __init__(self, parent=None) -> None:
		super().__init__(parent)
		self.setWindowTitle("新建项目")
		self.setMinimumWidth(420)
		form = QFormLayout(self)

		self.edit_name = QLineEdit("Untitled")
		form.addRow("项目名称:", self.edit_name)

		self.combo_backend = QComboBox()
		self.combo_backend.addItem(BACKEND_LABELS["df"], "df")
		self.combo_backend.addItem(BACKEND_LABELS["cb"], "cb")
		self.combo_backend.currentIndexChanged.connect(self._on_backend_changed)
		form.addRow("模组后端:", self.combo_backend)

		self.combo_mc = QComboBox()
		form.addRow("Minecraft 版本:", self.combo_mc)

		self.spin_bpm = QDoubleSpinBox()
		self.spin_bpm.setRange(20, 300)
		self.spin_bpm.setValue(120.0)
		self.spin_bpm.setDecimals(0)
		form.addRow("BPM:", self.spin_bpm)

		self._on_backend_changed()

		btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
		btns.accepted.connect(self.accept)
		btns.rejected.connect(self.reject)
		form.addRow(btns)

		log.debug("打开新建项目对话框")

	def _on_backend_changed(self) -> None:
		backend = self.combo_backend.currentData()
		log.debug(f"后端切换: {backend}")
		versions = BACKEND_MC_VERSIONS.get(backend, [])
		self.combo_mc.clear()
		self.combo_mc.addItems(versions)
		if backend == "df":
			idx = self.combo_mc.findText("1.21.8")
			if idx >= 0:
				self.combo_mc.setCurrentIndex(idx)

	def accept(self) -> None:
		log.debug("新建项目对话框: 用户确认")
		super().accept()

	def reject(self) -> None:
		log.debug("新建项目对话框: 用户取消")
		super().reject()

	@property
	def project_name(self) -> str:
		return self.edit_name.text().strip()

	@property
	def backend(self) -> str:
		return self.combo_backend.currentData()

	@property
	def mc_version(self) -> str:
		return self.combo_mc.currentText()

	@property
	def bpm(self) -> float:
		return self.spin_bpm.value()
