"""颜色选择组件 与模型解耦 适用于 df 和 cb."""
from __future__ import annotations

import logging

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
	QWidget, QHBoxLayout, QLabel, QSpinBox, QPushButton, QColorDialog,
)

log = logging.getLogger("dyn.components.color_picker")

class _ColorVal:
	"""与 V1/V2 ColorRGB 接口兼容的颜色值 支持 .r/.g/.b/.to_json()/.as_tuple()."""
	__slots__ = ('r', 'g', 'b')

	def __init__(self, r: int, g: int, b: int) -> None:
		self.r, self.g, self.b = r, g, b

	def as_tuple(self) -> tuple[int, int, int]:
		return self.r, self.g, self.b

	def to_json(self) -> dict:
		return {"r": self.r, "g": self.g, "b": self.b}

	@classmethod
	def from_json(cls, data: dict) -> _ColorVal:
		return cls(r=data["r"], g=data["g"], b=data["b"])

	def __iter__(self):
		return iter((self.r, self.g, self.b))

class ColorPicker(QWidget):
	"""颜色选择组件 color_changed 发射 _ColorVal (兼容 V1/V2 ColorRGB)."""

	color_changed = Signal(_ColorVal)

	def __init__(self, label: str = "", parent: QWidget | None = None) -> None:
		super().__init__(parent)
		self._r, self._g, self._b = 255, 165, 0
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
		log.debug(f"打开颜色对话框, 当前: ({self._r},{self._g},{self._b})")
		qcolor = QColorDialog.getColor(QColor(self._r, self._g, self._b), self, "选择颜色")
		if qcolor.isValid():
			nr, ng, nb = qcolor.red(), qcolor.green(), qcolor.blue()
			log.debug(f"对话框返回: ({nr},{ng},{nb})")
			self._r, self._g, self._b = nr, ng, nb
			self._spin_r.blockSignals(True)
			self._spin_g.blockSignals(True)
			self._spin_b.blockSignals(True)
			self._spin_r.setValue(nr)
			self._spin_g.setValue(ng)
			self._spin_b.setValue(nb)
			self._spin_r.blockSignals(False)
			self._spin_g.blockSignals(False)
			self._spin_b.blockSignals(False)
			self._update_button()
			cv = _ColorVal(nr, ng, nb)
			log.debug(f"ColorPicker emit: _ColorVal(r={cv.r}, g={cv.g}, b={cv.b})")
			self.color_changed.emit(cv)

	def _on_spin_changed(self) -> None:
		self._r = self._spin_r.value()
		self._g = self._spin_g.value()
		self._b = self._spin_b.value()
		self._update_button()
		cv = _ColorVal(self._r, self._g, self._b)
		log.debug(f"ColorPicker emit: _ColorVal(r={cv.r}, g={cv.g}, b={cv.b})")
		self.color_changed.emit(cv)

	def _update_button(self) -> None:
		self._btn.setStyleSheet(
			f"QPushButton {{ background-color: rgb({self._r},{self._g},{self._b}); "
			f"border: 1px solid #888; border-radius: 3px; }}"
		)

	def set_color(self, r: int, g: int = None, b: int = None) -> None:
		"""设置颜色 r/g/b 或传入任意有 .r/.g/.b 属性的对象."""
		if g is None:
			obj = r
			self._r, self._g, self._b = obj.r, obj.g, obj.b
		else:
			self._r, self._g, self._b = r, g, b
		self._spin_r.setValue(self._r)
		self._spin_g.setValue(self._g)
		self._spin_b.setValue(self._b)
		self._update_button()

	@property
	def rgb(self) -> tuple[int, int, int]:
		return self._r, self._g, self._b

	@property
	def color(self) -> _ColorVal:
		return _ColorVal(self._r, self._g, self._b)
