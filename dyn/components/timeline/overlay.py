"""光标覆盖层 播放头、刻度线、轨道标签."""
from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, QRect, QEvent
from PySide6.QtGui import QPainter, QPen
from PySide6.QtWidgets import QWidget

from .theme import palette_colors, TRACK_LABEL_WIDTH

if TYPE_CHECKING:
	from .timeline_widget import TimelineWidget

class _CursorOverlayWidget(QWidget):
	"""透明覆盖层 播放头（在轨道上方）."""

	def __init__(self, parent=None) -> None:
		super().__init__(parent)
		self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
		self._timeline: TimelineWidget | None = None
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
		if not self._timeline: return
		tl = self._timeline
		p = QPainter(self)
		p.setRenderHint(QPainter.Antialiasing)
		try:
			tl._paint_tick_marks(p)
			# 烟花/轨迹分隔线
			mid_y = tl._fw_track.geometry().bottom()
			p.setPen(QPen(self._divider_color, 3))
			p.drawLine(TRACK_LABEL_WIDTH + 2, mid_y, self.width() - 2, mid_y)
			f = p.font();
			f.setPointSize(9);
			p.setFont(f)
			p.setPen(QPen(self._label_color, 1))
			fw_center = (tl._fw_track.geometry().top() + mid_y) // 2
			traj_center = (mid_y + tl._traj_track.geometry().bottom()) // 2
			p.drawText(QRect(0, fw_center - 10, TRACK_LABEL_WIDTH, 20), Qt.AlignCenter, "烟花")
			p.drawText(QRect(0, traj_center - 10, TRACK_LABEL_WIDTH, 20), Qt.AlignCenter, "轨迹")
			tl._paint_cursor(p)
		finally:
			p.end()
