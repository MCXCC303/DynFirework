"""光标覆盖层 播放头、刻度线、BPM辅助线、轨道分隔线 (tick-based)."""
from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QPainter, QPen
from PySide6.QtWidgets import QWidget

from dyn.logging_config import get_logger
from .theme import palette_colors, TRACK_LABEL_WIDTH

log = get_logger(__name__)

if TYPE_CHECKING:
	from .timeline_widget import ParticleexTimelineWidget

class _CursorOverlayWidget(QWidget):
	def __init__(self, parent=None) -> None:
		super().__init__(parent)
		self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
		self._timeline: ParticleexTimelineWidget | None = None
		self._update_colors()

	def _update_colors(self):
		c = palette_colors()
		self._divider_color = c["mid"]

	def changeEvent(self, event):
		if event.type() == QEvent.PaletteChange:
			self._update_colors()
			self.update()
		super().changeEvent(event)

	def paintEvent(self, event) -> None:
		if not self._timeline:
			log.warning("覆盖层: 时间线引用为空, 跳过绘制")
			return
		tl = self._timeline
		p = QPainter(self)
		p.setRenderHint(QPainter.Antialiasing)
		try:
			if tl._show_time_marks:
				tl._paint_tick_marks(p)
			tl._paint_beat_lines(p)
			mid_y = tl._fw_track.geometry().bottom()
			p.setPen(QPen(self._divider_color, 3))
			p.drawLine(TRACK_LABEL_WIDTH + 2, mid_y, self.width() - 2, mid_y)
			tl._paint_cursor(p)
		finally:
			p.end()
