"""光标覆盖层 播放头、轨道分隔线 (tick-based)."""
from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QPainter, QPen, QBrush, QPainterPath, QColor
from PySide6.QtWidgets import QWidget

from dyn.logging_config import get_logger
from dyn.components.timeline.guide_lines import GuideLineRenderer
from .theme import palette_colors, TRACK_LABEL_WIDTH

log = get_logger(__name__)

if TYPE_CHECKING:
	from .timeline_widget import ParticleexTimelineWidget

class _CursorOverlayWidget(QWidget):
	def __init__(self, parent=None) -> None:
		super().__init__(parent)
		self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
		self._timeline: ParticleexTimelineWidget | None = None
		self._beat_major = QColor(255, 150, 50)
		self._beat_minor = QColor(255, 150, 50)
		self._guide_lines: GuideLineRenderer | None = None
		self._update_colors()

	def _init_guide_lines(self) -> None:
		self._guide_lines = GuideLineRenderer(
			to_x=lambda x: self._timeline.tick_to_x(x),
			from_x=lambda x: self._timeline.x_to_tick(x),
			px_per_native=lambda: self._timeline._pixels_per_tick,
			native_per_second=20,
			tick_major_color=self._tick_major,
			tick_minor_color=self._tick_minor,
			beat_major_color=self._beat_major,
			beat_minor_color=self._beat_minor,
		)

	def _update_colors(self):
		c = palette_colors()
		self._divider_color = c["mid"]
		self._tick_major = c["dark"]
		self._tick_minor = c["mid"]
		self._cursor_color = c["cursor"]
		if self._guide_lines:
			self._guide_lines._tick_major = self._tick_major
			self._guide_lines._tick_minor = self._tick_minor

	def changeEvent(self, event):
		if event.type() == QEvent.PaletteChange:
			self._update_colors()
			self.update()
		super().changeEvent(event)

	def paintEvent(self, event) -> None:
		if not self._timeline:
			log.warning("覆盖层: 时间线引用为空, 跳过绘制")
			return
		if not self._guide_lines:
			self._init_guide_lines()
		tl = self._timeline
		p = QPainter(self)
		p.setRenderHint(QPainter.Antialiasing)
		try:
			if tl._show_time_marks:
				self._guide_lines.paint_tick_marks(
					p, tl._waveform.geometry().bottom() + 2,
					self.height(), self.width())
			self._guide_lines.paint_beat_lines(
				p, tl._waveform.geometry().bottom() + 2,
				self.height(), self.width(),
				bpm=tl._bpm, audio_offset_ms=tl._audio_offset_ms,
				time_signature=tl._time_signature, show=tl._show_beat_lines)
			mid_y = tl._fw_track.geometry().bottom()
			p.setPen(QPen(self._divider_color, 3))
			p.drawLine(TRACK_LABEL_WIDTH + 2, mid_y, self.width() - 2, mid_y)
			self._paint_cursor(p)
		finally:
			p.end()

	def _paint_cursor(self, p: QPainter) -> None:
		tl = self._timeline
		cx = int(tl.tick_to_x(tl._playback_tick))
		if TRACK_LABEL_WIDTH <= cx <= self.width():
			p.setPen(QPen(self._cursor_color, 3))
			p.drawLine(cx, 0, cx, self.height())
			path = QPainterPath()
			path.moveTo(cx - 6, 0)
			path.lineTo(cx + 6, 0)
			path.lineTo(cx, 8)
			path.closeSubpath()
			p.fillPath(path, QBrush(self._cursor_color))
