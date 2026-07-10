"""音频波形显示."""

from __future__ import annotations

from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QPainter, QPen, QFont
from PySide6.QtWidgets import QWidget

from .theme import palette_colors, PIXELS_PER_TICK_DEFAULT, TRACK_LABEL_WIDTH

class _WaveformWidget(QWidget):
	def __init__(self, parent=None) -> None:
		super().__init__(parent)
		self._samples: list[float] = []
		self._total_ticks: int = 0
		self._pixels_per_tick: float = PIXELS_PER_TICK_DEFAULT
		self._scroll_offset: float = 0.0
		self._update_colors()
		self._update_colors()

	def _update_colors(self):
		c = palette_colors()
		self._bg = c["bg_dark"].darker(110)
		self._placeholder = c["mid"]
		self._wave_color = c["highlight_alpha"]

	def changeEvent(self, event):
		if event.type() == QEvent.PaletteChange:
			self._update_colors()
			self.update()
		super().changeEvent(event)

	def set_samples(self, samples: list[float] | None, sample_rate: int = 44100, bpm: float = 120.0) -> None:
		self._samples = samples or []
		if self._samples:
			seconds = len(self._samples) / sample_rate
			self._total_ticks = int(seconds * bpm / 60.0 * 20)
		else:
			self._total_ticks = 0
		self.update()

	def set_view(self, ppt: float, scroll: float) -> None:
		self._pixels_per_tick = ppt
		self._scroll_offset = scroll
		self.update()

	def paintEvent(self, event) -> None:
		p = QPainter(self)
		p.fillRect(self.rect(), self._bg)
		if not self._samples:
			p.setPen(QPen(self._placeholder, 1))
			f = QFont();
			f.setPointSize(9);
			p.setFont(f)
			p.drawText(self.rect(), Qt.AlignCenter, "音频波形 - 导入音乐后显示")
			p.end();
			return
		mid = self.height() // 2
		max_h = max(1, self.height() // 2 - 2)
		w = self.width() - TRACK_LABEL_WIDTH
		n = len(self._samples)
		ppt = self._pixels_per_tick
		scroll = self._scroll_offset
		tick_rate = max(1, self._total_ticks) if self._total_ticks else 1
		p.setPen(QPen(self._wave_color, 1))
		for i in range(0, w, 2):
			tick = int((i + scroll) / ppt)
			idx = int(tick * n / tick_rate) if tick >= 0 else 0
			if idx >= n: break
			step = max(1, int(n / tick_rate / ppt))
			chunk = self._samples[idx:min(idx + step, n)]
			amp = max(abs(min(chunk)), abs(max(chunk))) if chunk else 0
			h = int(min(amp, 1.0) * max_h)
			x = TRACK_LABEL_WIDTH + i
			p.drawLine(x, mid - h, x, mid + h)
		p.end()
