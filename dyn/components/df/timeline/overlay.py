"""光标覆盖层 播放头、秒刻度线、轨道分隔线 (df)."""
from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QPainter, QPen
from PySide6.QtWidgets import QWidget

from .theme import palette_colors, TRACK_LABEL_WIDTH

if TYPE_CHECKING:
	from .timeline_widget import DFTimelineWidget

class _CursorOverlayWidget(QWidget):
	def __init__(self, parent=None) -> None:
		super().__init__(parent)
		self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
		self._timeline: DFTimelineWidget | None = None
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
			return
		tl = self._timeline
		p = QPainter(self)
		p.setRenderHint(QPainter.Antialiasing)
		try:
			tl.paint_time_marks(p)
			for i, track in enumerate([
					tl.fw_track, tl.traj_track, tl.effect_track, tl.composite_track,
			]):
				if i > 0:
					geo = track.geometry()
					p.setPen(QPen(self._divider_color, 1))
					p.drawLine(TRACK_LABEL_WIDTH + 2, geo.top(), self.width() - 2, geo.top())
			tl.paint_cursor(p)
		finally:
			p.end()
