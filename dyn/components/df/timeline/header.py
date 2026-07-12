"""时间线刻度头 秒单位 (df)."""
from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, QRect, QEvent
from PySide6.QtGui import QPainter, QPen, QFont
from PySide6.QtWidgets import QWidget

from dyn.logging_config import get_logger
from .theme import palette_colors, HEADER_HEIGHT, TRACK_LABEL_WIDTH, _nice_interval

log = get_logger(__name__)

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
		if not self._timeline:
			log.warning("header paintEvent: timeline 未设置")
			return
		p = QPainter(self)
		p.setRenderHint(QPainter.Antialiasing)
		try:
			p.fillRect(self.rect(), self._bg)
			tl = self._timeline
			p.setPen(QPen(self._text_color, 1))
			f = QFont()
			f.setPointSize(8)
			p.setFont(f)
			major = _nice_interval(50.0 / tl.pixels_per_second)
			start_time = max(0.0, int(tl.x_to_time(float(TRACK_LABEL_WIDTH)) / major) * major)
			end_time = tl.x_to_time(float(self.width())) + major
			t = float(start_time)
			while t <= end_time:
				x = int(tl.time_to_x(t))
				label = f"{t:.0f}" if major >= 1.0 else f"{t:.1f}"
				p.drawText(QRect(x - 20, 2, 40, HEADER_HEIGHT - 4), Qt.AlignCenter, label)
				t += major
		finally:
			p.end()
