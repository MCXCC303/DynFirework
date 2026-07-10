"""颜色选择组件."""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
	QWidget, QHBoxLayout, QLabel, QSpinBox, QPushButton, QColorDialog,
)

from dyn.models.elements import ColorRGB

class ColorPicker(QWidget):
	"""颜色选择组件."""
	color_changed = Signal(ColorRGB)

	def __init__(self, label: str = "", parent: QWidget | None = None) -> None:
		super().__init__(parent)
		self._color = ColorRGB()
		self._setup_ui(label)

	def _setup_ui(self, label: str) -> None:
		layout = QHBoxLayout(self)
		layout.setContentsMargins(0, 0, 0, 0)
		layout.setSpacing(4)
		if label:
			lbl = QLabel(label)
			lbl.setFixedWidth(40)
			layout.addWidget(lbl)
		self._btn = QPushButton()
		self._btn.setFixedSize(52, 28)
		self._btn.setToolTip("点击选择颜色")
		self._btn.clicked.connect(self._on_pick_color)
		layout.addWidget(self._btn)
		for ch in ("R", "G", "B"):
			lbl = QLabel(ch)
			lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
			lbl.setFixedWidth(14)
			layout.addWidget(lbl)
			spin = QSpinBox()
			spin.setRange(0, 255)
			spin.setFixedWidth(48)
			layout.addWidget(spin)
			if ch == "R":
				self._spin_r = spin
			elif ch == "G":
				self._spin_g = spin
			else:
				self._spin_b = spin
		self._spin_r.valueChanged.connect(self._on_spin_changed)
		self._spin_g.valueChanged.connect(self._on_spin_changed)
		self._spin_b.valueChanged.connect(self._on_spin_changed)
		self._update_button()

	def _on_pick_color(self) -> None:
		init = QColor(self._color.r, self._color.g, self._color.b)
		qcolor = QColorDialog.getColor(init, self, "选择颜色")
		if qcolor.isValid():
			self._color = ColorRGB(r=qcolor.red(), g=qcolor.green(), b=qcolor.blue())
			self._spin_r.setValue(qcolor.red())
			self._spin_g.setValue(qcolor.green())
			self._spin_b.setValue(qcolor.blue())

	def _on_spin_changed(self) -> None:
		self._color = ColorRGB(r=self._spin_r.value(), g=self._spin_g.value(), b=self._spin_b.value())
		self._update_button()
		self.color_changed.emit(self._color)

	def _update_button(self) -> None:
		c = self._color
		self._btn.setStyleSheet(f"QPushButton {{ background-color: rgb({c.r},{c.g},{c.b}); border: 1px solid #888; border-radius: 3px; }}")

	def set_color(self, color: ColorRGB) -> None:
		self._color = color
		self._spin_r.setValue(color.r)
		self._spin_g.setValue(color.g)
		self._spin_b.setValue(color.b)
		self._update_button()

	@property
	def color(self) -> ColorRGB:
		return self._color
