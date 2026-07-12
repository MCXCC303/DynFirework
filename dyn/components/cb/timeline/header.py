"""时间线刻度头 (tick-based)."""
from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, QRect, QEvent
from PySide6.QtGui import QPainter, QPen, QFont
from PySide6.QtWidgets import QWidget

from dyn.logging_config import get_logger
from .theme import palette_colors, HEADER_HEIGHT, TRACK_LABEL_WIDTH

log = get_logger(__name__)

if TYPE_CHECKING:
	from .timeline_widget import ParticleexTimelineWidget

class _HeaderWidget(QWidget):
	def __init__(self, parent=None) -> None:
		super().__init__(parent)
		self._timeline: ParticleexTimelineWidget | None = None
		self._update_colors()

	def _update_colors(self):
		c = palette_colors()
		self._bg = c["bg_dark"]
		self._text_color = c["text"]

	def changeEvent(self, event):
		if event.type() == QEvent.PaletteChange:
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
				start_tick = max(0, (tl.x_to_tick(TRACK_LABEL_WIDTH) // 20) * 20)
				end_tick = tl.x_to_tick(self.width()) + 1
				tick = start_tick
				while tick <= end_tick:
					if tick % 20 == 0:
						x = int(tl.tick_to_x(tick))
						p.drawText(QRect(x - 20, 2, 40, HEADER_HEIGHT - 4), Qt.AlignCenter, str(tick))
					tick += 20
			else:
				log.warning("时间线头: 时间线引用为空, 跳过绘制")
		finally:
			p.end()
