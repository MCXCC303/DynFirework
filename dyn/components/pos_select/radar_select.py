"""雷达图组件 - 极坐标位置选择器."""
from __future__ import annotations

import math

from PySide6.QtCore import QPoint
from PySide6.QtGui import (
	QColor,
	QPainter,
	QPen,
)
from PySide6.QtWidgets import QWidget

from dyn.components.pos_select.grid_select import _BaseGraphWidget

class RadarWidget(_BaseGraphWidget):
	"""雷达图(极坐标)位置选择器."""

	RING_INTERVAL = 16
	ANGLE_INTERVAL = 30

	def __init__(self, parent: QWidget | None = None) -> None:
		super().__init__(parent)
		self.ring_color = QColor(180, 180, 190)
		self.ring_major_color = QColor(140, 140, 155)
		self.radial_color = QColor(180, 180, 190, 120)
		self.bg_color = QColor(248, 248, 250)

	def _paint_bg(self, p: QPainter) -> None:
		p.fillRect(self.rect(), self.bg_color)

	def _paint_grid(self, p: QPainter) -> None:
		self._paint_rings(p)
		self._paint_radial_lines(p)
		self._paint_axes(p)

	def _paint_rings(self, p: QPainter) -> None:
		cx, cy = int(self._grid_to_widget(0, 0)[0]), int(self._grid_to_widget(0, 0)[1])
		center = QPoint(cx, cy)
		max_px = int(max(self.width(), self.height()) * 1.5)
		for r in range(self.RING_INTERVAL * self.pix_size, max_px, self.RING_INTERVAL * self.pix_size):
			is_major = (r // self.pix_size) % (self.RING_INTERVAL * 4) == 0
			p.setPen(QPen(self.ring_major_color if is_major else self.ring_color, 2 if is_major else 1))
			p.drawEllipse(center, r, r)

	def _paint_radial_lines(self, p: QPainter) -> None:
		cx, cy = int(self._grid_to_widget(0, 0)[0]), int(self._grid_to_widget(0, 0)[1])
		max_r = max(self.width(), self.height()) * 1.5
		p.setPen(QPen(self.radial_color, 1))
		for angle in range(0, 360, self.ANGLE_INTERVAL):
			rad = math.radians(angle)
			ex, ey = int(cx + math.cos(rad) * max_r), int(cy + math.sin(rad) * max_r)
			p.drawLine(cx, cy, ex, ey)
		p.setPen(QPen(self.ring_major_color, 2))
		for angle in (0, 90, 180, 270):
			rad = math.radians(angle)
			ex, ey = int(cx + math.cos(rad) * max_r), int(cy + math.sin(rad) * max_r)
			p.drawLine(cx, cy, ex, ey)

	def _paint_axes(self, p: QPainter) -> None:
		"""绘制 X/Z 轴箭头和标签，与网格图风格一致."""
		w, h = self.width(), self.height()
		cx, cy = int(self._grid_to_widget(0, 0)[0]), int(self._grid_to_widget(0, 0)[1])
		if cx < 0 or cy < 0 or cx > w or cy > h:
			return
		ps = max(self.pix_size, 8)
		ax_color = QColor(140, 140, 155)

		# X 轴 -> 右边缘箭头
		p.setPen(QPen(ax_color, 2))
		p.drawLine(cx, cy, w, cy)
		p.drawLine(w, cy, w - ps, cy - ps // 2)
		p.drawLine(w, cy, w - ps, cy + ps // 2)

		# Z 轴 -> 底部箭头
		p.drawLine(cx, cy, cx, h)
		p.drawLine(cx, h, cx - ps // 2, h - ps)
		p.drawLine(cx, h, cx + ps // 2, h - ps)

		# 标签 (与网格图位置一致)
		font = p.font()
		font.setPixelSize(ps)
		p.setFont(font)
		p.setPen(QPen(QColor(100, 100, 110), 1))
		p.drawText(w - ps, cy - ps, "X")
		p.drawText(cx + ps, h - ps, "Z")
