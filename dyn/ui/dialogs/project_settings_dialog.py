"""项目设置对话框 按后端过滤可选 MC 版本."""
from __future__ import annotations

import logging

from PySide6.QtWidgets import (
	QDialog, QFormLayout, QLineEdit, QDoubleSpinBox, QSpinBox,
	QComboBox, QDialogButtonBox, QLabel, QHBoxLayout, QWidget,
)

from dyn.ui.dialogs.project_creation_dialog import BACKEND_MC_VERSIONS

log = logging.getLogger(__name__)

class ProjectSettingsDialog(QDialog):
	"""编辑项目名称、BPM、音频偏移、拍号和 Minecraft 版本 版本列表按后端过滤."""

	def __init__(self, name: str = "Untitled", bpm: float = 120.0,
	             mc_version: str = "1.20.1", backend: str = "df",
	             audio_offset_ms: float = 0.0, time_signature: tuple = (4, 4),
	             parent=None) -> None:
		super().__init__(parent)
		self.setWindowTitle("项目设置")
		form = QFormLayout(self)

		self.edit_name = QLineEdit(name)
		form.addRow("项目名称:", self.edit_name)

		self.spin_bpm = QDoubleSpinBox()
		self.spin_bpm.setRange(20, 300)
		self.spin_bpm.setValue(bpm)
		form.addRow("BPM:", self.spin_bpm)

		# 拍号: 分子/分母
		ts_widget = QWidget()
		ts_layout = QHBoxLayout(ts_widget)
		ts_layout.setContentsMargins(0, 0, 0, 0)
		ts_layout.setSpacing(4)
		self.spin_ts_num = QSpinBox()
		self.spin_ts_num.setRange(1, 32)
		self.spin_ts_num.setValue(time_signature[0])
		self.spin_ts_num.setToolTip("每小节拍数")
		self.spin_ts_den = QSpinBox()
		self.spin_ts_den.setRange(1, 32)
		self.spin_ts_den.setValue(time_signature[1])
		self.spin_ts_den.setToolTip("以几分音符为一拍")
		ts_layout.addWidget(self.spin_ts_num)
		ts_layout.addWidget(QLabel("/"))
		ts_layout.addWidget(self.spin_ts_den)
		ts_layout.addStretch()
		form.addRow("拍号:", ts_widget)

		self.spin_audio_offset = QDoubleSpinBox()
		self.spin_audio_offset.setRange(-500.0, 500.0)
		self.spin_audio_offset.setValue(audio_offset_ms)
		self.spin_audio_offset.setSuffix(" ms")
		self.spin_audio_offset.setDecimals(0)
		self.spin_audio_offset.setToolTip("正值向前偏移，负值向后偏移")
		form.addRow("音频偏移:", self.spin_audio_offset)

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

		log.debug(f"打开项目设置: name={name}, bpm={bpm}, offset={audio_offset_ms}ms")

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
	def audio_offset_ms(self) -> float:
		return self.spin_audio_offset.value()

	@property
	def time_signature(self) -> tuple:
		return (self.spin_ts_num.value(), self.spin_ts_den.value())

	@property
	def mc_version(self) -> str:
		return self.combo_mc_version.currentText()
