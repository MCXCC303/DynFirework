"""光标覆盖层 播放头、秒刻度线、四轨道标签 (df)."""
from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, QRect, QEvent
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
		self._label_color = c["text_dim"]

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
			f = p.font()
			f.setPointSize(9)
			p.setFont(f)
			p.setPen(QPen(self._label_color, 1))
			for i, (track_name, track) in enumerate(zip(
					["烟花", "轨迹", "效果", "复合"],
					[tl.fw_track, tl.traj_track, tl.effect_track, tl.composite_track],
			)):
				geo = track.geometry()
				if i > 0:
					p.setPen(QPen(self._divider_color, 1))
					p.drawLine(TRACK_LABEL_WIDTH + 2, geo.top(), self.width() - 2, geo.top())
				center_y = geo.top() + geo.height() // 2
				p.drawText(QRect(0, center_y - 10, TRACK_LABEL_WIDTH, 20), Qt.AlignCenter, track_name)
			tl.paint_cursor(p)
		finally:
			p.end()
