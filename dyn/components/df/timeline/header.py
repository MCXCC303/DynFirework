"""时间线刻度头 秒单位 (df)."""
from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, QRect, QEvent
from PySide6.QtGui import QPainter, QPen, QFont
from PySide6.QtWidgets import QWidget

from .theme import palette_colors, HEADER_HEIGHT, TRACK_LABEL_WIDTH, MAJOR_TICK_INTERVAL

if TYPE_CHECKING:
	from .timeline_widget import DFTimelineWidget

class _HeaderWidget(QWidget):
	def __init__(self, parent=None) -> None:
		super().__init__(parent)
		self._timeline: DFTimelineWidget | None = None
		self._update_colors()

	def _update_colors(self):
		c = palette_colors()
		self._bg = c["bg_dark"]
		self._text_color = c["text"]

	def changeEvent(self, event):
		if event.type() == QEvent.PaletteChange:
			self._update_colors()
			self.update()
		super().changeEvent(event)

	def paintEvent(self, event) -> None:
		p = QPainter(self)
		p.setRenderHint(QPainter.Antialiasing)
		try:
			p.fillRect(self.rect(), self._bg)
			if self._timeline:
				tl = self._timeline
				p.setPen(QPen(self._text_color, 1))
				f = QFont()
				f.setPointSize(8)
				p.setFont(f)
				start_time = max(0.0, int(tl.x_to_time(float(TRACK_LABEL_WIDTH))))
				end_time = tl.x_to_time(float(self.width())) + MAJOR_TICK_INTERVAL
				t = float(start_time)
				while t <= end_time:
					x = int(tl.time_to_x(t))
					p.drawText(QRect(x - 20, 2, 40, HEADER_HEIGHT - 4), Qt.AlignCenter, f"{t:.1f}s")
					t += MAJOR_TICK_INTERVAL
		finally:
			p.end()
