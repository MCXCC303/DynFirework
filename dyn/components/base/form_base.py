"""属性表单共享基类, DynFirework Mod 适配秒单位."""
from __future__ import annotations

import logging

from PySide6.QtWidgets import (
	QWidget, QHBoxLayout, QLabel, QSpinBox, QDoubleSpinBox,
	QComboBox, QPushButton, QFormLayout, QDial, QCheckBox, QLineEdit,
	QGroupBox,
)

log = logging.getLogger(__name__)

class FormBase(QWidget):
	"""提供 _add_row / reset / block 等共享工具的表单基类."""

	def __init__(self, parent: QWidget | None = None) -> None:
		super().__init__(parent)
		self._w: dict[str, tuple[QWidget, QWidget, QPushButton | None, object]] = {}
		self._defaults: dict[str, object] = {}

	def _add_row(self, form: QFormLayout, key: str, label: str, widget: QWidget, default: object = None) -> None:
		lbl = QLabel(label)
		row = QHBoxLayout()
		row.setContentsMargins(0, 0, 0, 0)
		row.setSpacing(2)
		row.addWidget(widget)
		btn = None
		if default is not None:
			self._defaults[key] = default
			btn = QPushButton("↺")
			btn.setFixedSize(20, 20)
			btn.setToolTip("重置为默认值")
			btn.clicked.connect(lambda checked, k=key, d=default, w=widget: self._reset_value(k, d, w))
			btn.hide()
			row.addWidget(btn)
			if isinstance(widget, QSpinBox):
				widget.valueChanged.connect(lambda v: self._update_reset_buttons())
			elif isinstance(widget, QDoubleSpinBox):
				widget.valueChanged.connect(lambda v: self._update_reset_buttons())
		form.addRow(lbl, row)
		self._w[key] = (lbl, widget, btn, default)

	def _add_pos_group(self, key: str, title: str, with_select_btn: bool = True,
	                   y_range: tuple = (-64, 320), decimals: int = 2) -> tuple[
		QGroupBox, QDoubleSpinBox, QDoubleSpinBox, QDoubleSpinBox, QPushButton | None]:
		"""创建位置 XYZ 组 返回 (group, spin_x, spin_y, spin_z, select_btn)."""
		group = QGroupBox(title)
		form = QFormLayout(group)
		sx = QDoubleSpinBox()
		sx.setRange(-100000, 100000)
		sx.setDecimals(decimals)
		self._add_row(form, f"{key}_x", "X:", sx)
		sy = QDoubleSpinBox()
		sy.setRange(*y_range)
		sy.setDecimals(decimals)
		self._add_row(form, f"{key}_y", "Y:", sy)
		sz = QDoubleSpinBox()
		sz.setRange(-100000, 100000)
		sz.setDecimals(decimals)
		self._add_row(form, f"{key}_z", "Z:", sz)
		btn = None
		if with_select_btn:
			btn = QPushButton("在地图上选择...")
			form.addRow("", btn)
		self.layout().addWidget(group)
		return group, sx, sy, sz, btn

	@staticmethod
	def _reset_value(key: str, default: object, widget: QWidget) -> None:
		if isinstance(widget, (QSpinBox, QDoubleSpinBox)):
			widget.setValue(default)
		elif isinstance(widget, QComboBox):
			idx = widget.findData(default)
			if idx >= 0:
				widget.setCurrentIndex(idx)
		else:
			log.debug(f"不支持的重置控件类型: {type(widget)}")

	def _update_reset_buttons(self) -> None:
		for key, (lbl, widget, btn, default) in self._w.items():
			if btn is None or default is None:
				continue
			if isinstance(widget, QSpinBox):
				show = widget.value() != int(default)
			elif isinstance(widget, QDoubleSpinBox):
				show = abs(widget.value() - float(default)) > 0.001
			elif isinstance(widget, QComboBox):
				show = widget.currentData() != default
			else:
				continue
			btn.setVisible(show)

	def _show_w(self, key: str) -> None:
		if key in self._w:
			self._w[key][0].show()
			self._w[key][1].show()
			if self._w[key][2]:
				self._w[key][2].show()

	def _hide_w(self, key: str) -> None:
		if key in self._w:
			self._w[key][0].hide()
			self._w[key][1].hide()
			if self._w[key][2]:
				self._w[key][2].hide()

	def block_signals(self, block: bool) -> None:
		for typ in (QSpinBox, QDoubleSpinBox, QComboBox, QCheckBox, QLineEdit, QDial):
			for widget in self.findChildren(typ):
				widget.blockSignals(block)
