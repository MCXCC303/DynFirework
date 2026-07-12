"""导出数据包对话框 按 MC 版本自动选择 pack_format."""
from __future__ import annotations

from PySide6.QtWidgets import (
	QDialog, QFormLayout, QLineEdit, QSpinBox, QLabel, QDialogButtonBox,
)

_MC_TO_PACK_FORMAT: dict[str, int] = {
	# 数据包格式号参考 minecraft.wiki/w/Pack_format
	"1.12.2": 3,    # 1.11-1.12.2 函数系统 (预数据包)
	"1.16.5": 6,    # 1.16.2-1.16.5
	"1.20.1": 15,   # 1.20-1.20.1
	"1.20.4": 22,   # 1.20.3-1.20.4
	"1.21": 48,     # 1.21-1.21.1
	"1.21.8": 57,   # 1.21.2+ (Fabric 1.21.8 兼容)
}

def _resolve_pack_format(mc_version: str) -> int:
	return _MC_TO_PACK_FORMAT.get(mc_version, 48)

class ExportDialog(QDialog):
	"""收集数据包导出参数."""

	def __init__(self, default_name: str = "DynFirework", mc_version: str = "1.21.8", parent=None) -> None:
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

		form.addRow("Minecraft 版本:", QLabel(f"MC {mc_version}"))

		self.spin_format = QSpinBox()
		self.spin_format.setRange(1, 61)
		self.spin_format.setValue(_resolve_pack_format(mc_version))
		self.spin_format.setToolTip(
			"数据包格式号\n"
			"1.12.2=3, 1.16.5=6, 1.20.1=15, 1.20.4=22, 1.21.x=48~57"
		)
		form.addRow("Pack Format:", self.spin_format)

		btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
		btns.accepted.connect(self.accept)
		btns.rejected.connect(self.reject)
		form.addRow(btns)

	@property
	def pack_name(self) -> str: return self.edit_name.text().strip()

	@property
	def namespace(self) -> str: return self.edit_ns.text().strip()

	@property
	def description(self) -> str: return self.edit_desc.text().strip()

	@property
	def pack_format(self) -> int: return self.spin_format.value()
