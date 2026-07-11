"""轨道区域 单个轨道的布局、绘制和交互 (df, second-based)."""
from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import Qt, Signal, QRect, QPoint, QEvent
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QFont, QPainterPath, QMouseEvent, QWheelEvent
from PySide6.QtWidgets import QWidget

from dyn.logging_config import get_logger

log = get_logger(__name__)

from dyn.models.particleex.fireworks import FireworkElement
from dyn.models.particleex.trajectories import TrajectoryElement
from dyn.models.particleex.values import ColorRGB
from .proxy import _ElementView
from .theme import (
	palette_colors,
	TRACK_LABEL_WIDTH, TRACK_HEIGHT, BLOCK_MIN_WIDTH,
	PIXELS_PER_SECOND_DEFAULT, SNAP_INTERVAL,
)

@dataclass
class _BlockLayout:
	element: _ElementView
	rect: QRect

class _TrackArea(QWidget):
	"""单个轨道区域，支持独立垂直滚动."""

	element_selected = Signal(str)
	element_moved = Signal(str, float, float)
	element_resized = Signal(str, float, float)
	drag_update = Signal()
	drag_undo_begin = Signal()
	drag_undo_end = Signal()

	def __init__(self, label: str, parent=None) -> None:
		super().__init__(parent)
		self._label = label
		self._blocks: list[_BlockLayout] = []
		self._views: list[_ElementView] = []
		self._selected_id: str = ""
		self._pixels_per_second: float = PIXELS_PER_SECOND_DEFAULT
		self._scroll_offset: float = 0.0
		self._dragging: _BlockLayout | None = None
		self._dragging_edge: str = ""
		self._drag_start_pos: QPoint | None = None
		self._drag_start_time: float = 0.0
		self._drag_start_duration: float = 0.0
		self._drag_parent_start_time: float = 0.0
		self._content_height: int = 100

		self._update_colors()
		self.setMouseTracking(True)
		self.setMinimumHeight(60)

	def _update_colors(self):
		c = palette_colors()
		self._bg = c["bg"]
		self._sel_color = c["sel"]
		self._label_bg = c["bg_dark"]
		self._text_color = c["text"]

	def changeEvent(self, event):
		if event.type() == QEvent.PaletteChange:
			self._update_colors()
			self.update()
		super().changeEvent(event)

	def set_data(self, views: list[_ElementView], pps: float, scroll: float) -> None:
		self._views = views
		self._pixels_per_second = pps
		self._scroll_offset = scroll
		self._compute()

	def set_selection(self, element_id: str) -> None:
		self._selected_id = element_id
		self.update()

	@staticmethod
	def _match_selection(view: _ElementView, sel_id: str) -> bool:
		if not sel_id:
			return False
		if view.id == sel_id:
			return True
		if view.is_composite_part and sel_id + "::fw" == view.id:
			return True
		if view.is_composite_part and sel_id + "::traj" == view.id:
			return True
		return False

	def set_view(self, pps: float, scroll: float) -> None:
		self._pixels_per_second = pps
		self._scroll_offset = scroll
		self._compute()

	def compute_and_update(self) -> None:
		self._compute()
		self.update()

	@property
	def content_height(self) -> int:
		return self._content_height

	def _time_to_x(self, t: float) -> float:
		return TRACK_LABEL_WIDTH + t * self._pixels_per_second - self._scroll_offset

	def _x_to_time(self, x: float) -> float:
		return max(0.0, (x - TRACK_LABEL_WIDTH + self._scroll_offset) / self._pixels_per_second)

	def _compute(self) -> None:
		self._blocks.clear()
		if not self._views:
			self._content_height = 60
			self.update()
			return
		rows = self._assign_rows(self._views)
		max_row = max(rows.values()) if rows else 0
		for view in self._views:
			row = rows.get(view.id, 0)
			x = int(self._time_to_x(view.start_time))
			w = max(BLOCK_MIN_WIDTH, int(view.duration * self._pixels_per_second))
			y = 4 + row * TRACK_HEIGHT
			self._blocks.append(_BlockLayout(element=view, rect=QRect(x, y, w, TRACK_HEIGHT - 4)))
		self._content_height = 4 + (max_row + 1) * TRACK_HEIGHT + 8
		self.update()

	@staticmethod
	def _assign_rows(views: list[_ElementView]) -> dict[str, int]:
		sorted_views = sorted(views, key=lambda v: v.start_time)
		row_ends: list[float] = []
		result: dict[str, int] = {}
		for view in sorted_views:
			placed = False
			for row_idx, row_end in enumerate(row_ends):
				if view.start_time >= row_end:
					row_ends[row_idx] = view.end_time
					result[view.id] = row_idx
					placed = True
					break
			if not placed:
				result[view.id] = len(row_ends)
				row_ends.append(view.end_time)
		return result

	def paintEvent(self, event) -> None:
		p = QPainter(self)
		p.setRenderHint(QPainter.Antialiasing)
		try:
			p.fillRect(self.rect(), self._bg)
			p.fillRect(QRect(0, 0, TRACK_LABEL_WIDTH, self.height()), self._label_bg)
			p.setClipRect(QRect(TRACK_LABEL_WIDTH, 0, self.width() - TRACK_LABEL_WIDTH, self.height()))
			for blk in self._blocks:
				self._paint_block(p, blk)
			p.setClipping(False)
		finally:
			p.end()

	def _paint_block(self, p: QPainter, blk: _BlockLayout) -> None:
		view = blk.element
		r = blk.rect
		sel = self._match_selection(view, self._selected_id)
		self._paint_block_gradient(p, view, r, sel)
		if sel:
			p.setPen(QPen(self._sel_color, 2))
			p.drawRoundedRect(r.adjusted(1, 1, -1, -1), 3, 3)
		if r.width() > 20:
			p.setPen(QPen(QColor(255, 255, 255), 1))
			f = QFont()
			f.setPointSize(7)
			p.setFont(f)
			p.drawText(r.adjusted(4, 0, -4, 0), Qt.AlignVCenter | Qt.AlignLeft, view.name)
		if r.width() > 36:
			p.setPen(QPen(QColor(255, 255, 255, 150), 1))
			f2 = QFont()
			f2.setPointSize(6)
			p.setFont(f2)
			p.drawText(QRect(r.right() - 18, r.top() + 2, 14, r.height() - 4), Qt.AlignCenter, self._icon(view))

	@staticmethod
	def _paint_block_gradient(p: QPainter, view: _ElementView, r: QRect, sel: bool) -> None:
		disabled = not view.enabled
		elem = view.elem
		if view.is_composite_part and view.is_tf():
			parent = elem
			if view.part == "traj":
				c_start, c_end = parent.traj_color.start, parent.traj_color.end
				use_grad = parent.traj_color.use_gradient
				layers = 1
			else:
				use_grad = parent.inner_color.use_gradient
				layers = 2 if parent.fw_type == "double_layer" else 1
				c_start = parent.inner_color.start
				c_end = parent.inner_color.end
				c_outer_start = parent.outer_color.start
				c_outer_end = parent.outer_color.end
		elif isinstance(elem, TrajectoryElement):
			c_start, c_end = elem.traj_color.start, elem.traj_color.end
			use_grad = elem.traj_color.use_gradient
			layers = 1
		elif isinstance(elem, FireworkElement):
			use_grad = elem.inner_color.use_gradient
			layers = 2 if elem.fw_type == "double_layer" else 1
			c_start = elem.inner_color.start
			c_end = elem.inner_color.end
			c_outer_start = elem.outer_color.start
			c_outer_end = elem.outer_color.end
		else:
			c_start = c_end = ColorRGB(128, 128, 128)
			use_grad = False
			layers = 1

		def qc(c, alpha=200):
			return QColor(max(c.r // 6, 15) if disabled else c.r,
			              max(c.g // 6, 15) if disabled else c.g,
			              max(c.b // 6, 15) if disabled else c.b, alpha)

		p.setClipRect(r)
		if layers == 2:
			half_w = r.width() // 2
			half_h = r.height() // 2
			in_grad = None
			out_grad = None
			if view.is_composite_part and view.is_tf():
				parent = elem
				in_grad = parent.inner_color.use_gradient
				out_grad = parent.outer_color.use_gradient
			elif isinstance(elem, FireworkElement):
				in_grad = elem.inner_color.use_gradient
				out_grad = elem.outer_color.use_gradient
			if in_grad:
				p.fillRect(QRect(r.x(), r.y(), half_w, half_h), QBrush(qc(c_start)))
				p.fillRect(QRect(r.x() + half_w, r.y(), r.width() - half_w, half_h), QBrush(qc(c_end)))
			else:
				p.fillRect(QRect(r.x(), r.y(), r.width(), half_h), QBrush(qc(c_start)))
			if out_grad:
				p.fillRect(QRect(r.x(), r.y() + half_h, half_w, r.height() - half_h), QBrush(qc(c_outer_start)))
				p.fillRect(QRect(r.x() + half_w, r.y() + half_h, r.width() - half_w, r.height() - half_h),
				           QBrush(qc(c_outer_end)))
			else:
				p.fillRect(QRect(r.x(), r.y() + half_h, r.width(), r.height() - half_h), QBrush(qc(c_outer_start)))
		elif use_grad:
			half_w = r.width() // 2
			p.fillRect(QRect(r.x(), r.y(), half_w, r.height()), QBrush(qc(c_start)))
			p.fillRect(QRect(r.x() + half_w, r.y(), r.width() - half_w, r.height()), QBrush(qc(c_end)))
		else:
			path = QPainterPath()
			path.addRoundedRect(r, 3, 3)
			p.fillPath(path, QBrush(qc(c_start)))
		p.setClipping(False)

	@staticmethod
	def _block_color(view: _ElementView) -> QColor:
		elem = view.elem
		if view.is_composite_part and view.is_tf():
			parent = elem
			if view.part == "traj":
				c = parent.traj_color.start
			else:
				c = parent.inner_color.start
			return QColor(c.r, c.g, c.b, 200)
		if isinstance(elem, TrajectoryElement):
			c = elem.traj_color.start
			return QColor(c.r, c.g, c.b, 200)
		elif isinstance(elem, FireworkElement):
			c = elem.inner_color.start
			return QColor(c.r, c.g, c.b, 200)
		return QColor(128, 128, 128, 200)

	@staticmethod
	def _icon(view: _ElementView) -> str:
		elem = view.elem
		if view.is_composite_part and view.is_tf():
			parent = elem
			if view.part == "traj":
				return {"launch": "↗", "spark": "✳", "offset": "↝", "thick": "≣", "expanding": "⬍"}.get(parent.traj_type, "⇢")
			else:
				return {
					"single_layer": "✦",
					"double_layer": "✶",
					"directional": "➳",
					"clustered": "❈",
					"expanding_sphere": "◉"}.get(parent.fw_type, "★")
		if isinstance(elem, FireworkElement):
			return {"single_layer": "✦", "double_layer": "✶",
			        "directional": "➳", "clustered": "❈", "expanding_sphere": "◉"}.get(elem.fw_type, "★")
		if isinstance(elem, TrajectoryElement):
			return {"launch": "↗", "spark": "✳",
			        "offset": "↝", "thick": "≣", "expanding": "⬍"}.get(elem.traj_type, "->")
		return "?"

	def mousePressEvent(self, event: QMouseEvent) -> None:
		if event.button() != Qt.LeftButton:
			return
		x, y = event.position().x(), event.position().y()
		for blk in reversed(self._blocks):
			if blk.rect.contains(int(x), int(y)):
				self._dragging = blk
				self._drag_start_pos = QPoint(int(x), int(y))
				self._drag_start_time = blk.element.start_time
				self._drag_start_duration = blk.element.duration
				if blk.element.is_composite_part:
					self._drag_parent_start_time = _ElementView.tick_to_second(blk.element.elem.start_tick)
					log.debug(
						f"拖拽开始(复合): id={blk.element.id}, part={blk.element.part}, "
						f"start={blk.element.start_time:.2f}s, dur={blk.element.duration:.2f}s"
					)
				else:
					self._drag_parent_start_time = blk.element.start_time
					log.debug(
						f"拖拽开始: id={blk.element.id[:8]}, name={blk.element.name}, "
						f"start={blk.element.start_time:.2f}s, dur={blk.element.duration:.2f}s"
					)
				margin = 6
				if x <= blk.rect.left() + margin and blk.rect.width() > BLOCK_MIN_WIDTH * 2:
					self._dragging_edge = "left"
				elif x >= blk.rect.right() - margin and blk.rect.width() > BLOCK_MIN_WIDTH * 2:
					self._dragging_edge = "right"
				else:
					self._dragging_edge = "move"
				log.debug(f"  边缘={self._dragging_edge}")
				self._selected_id = blk.element.id
				self.element_selected.emit(blk.element.id)
				self.update()
				return
		self._selected_id = ""
		self.element_selected.emit("")
		self.update()

	def mouseMoveEvent(self, event: QMouseEvent) -> None:
		if self._dragging and self._drag_start_pos:
			dx = event.position().x() - self._drag_start_pos.x()
			dt_raw = dx / self._pixels_per_second
			dt = round(dt_raw / SNAP_INTERVAL) * SNAP_INTERVAL
			view = self._dragging.element
			if self._dragging_edge == "move":
				if view.is_composite_part:
					view.elem.start_tick = max(0, _ElementView.second_to_tick(self._drag_parent_start_time + dt))
				else:
					view.start_time = max(0.0, self._drag_start_time + dt)
			elif self._dragging_edge == "left":
				ns = max(0.0, self._drag_start_time + dt)
				nd = self._drag_start_duration + (self._drag_start_time - ns)
				if nd >= SNAP_INTERVAL:
					view.start_time = ns
					view.duration = nd
			elif self._dragging_edge == "right":
				view.duration = max(SNAP_INTERVAL, self._drag_start_duration + dt)
			self._compute()
			self.update()
			self.drag_update.emit()
			return
		x, y = event.position().x(), event.position().y()
		for blk in self._blocks:
			r = blk.rect
			if r.contains(int(x), int(y)):
				margin = 6
				if x <= r.left() + margin:
					self.setCursor(Qt.SizeHorCursor)
					return
				if x >= r.right() - margin:
					self.setCursor(Qt.SizeHorCursor)
					return
				self.setCursor(Qt.PointingHandCursor)
				return
		if x > TRACK_LABEL_WIDTH:
			self.setCursor(Qt.ArrowCursor)

	def mouseReleaseEvent(self, event: QMouseEvent) -> None:
		if self._dragging:
			self.drag_undo_begin.emit()
			view = self._dragging.element
			if self._dragging_edge == "move" and view.is_composite_part:
				parent = view.elem
				new_parent_start = _ElementView.tick_to_second(parent.start_tick)
				if new_parent_start != self._drag_parent_start_time:
					self.element_moved.emit(view.id, new_parent_start, self._drag_parent_start_time)
			elif not view.is_composite_part or view.part == "traj":
				if view.start_time != self._drag_start_time:
					self.element_moved.emit(view.id, view.start_time, self._drag_start_time)
			if view.duration != self._drag_start_duration:
				self.element_resized.emit(view.id, view.duration, self._drag_start_duration)
			if view.is_composite_part and view.part == "fw" and self._dragging_edge == "left":
				parent = view.elem
				old_traj_dur_tick = _ElementView.second_to_tick(self._drag_start_time - self._drag_parent_start_time)
				old_traj_dur_sec = _ElementView.tick_to_second(old_traj_dur_tick)
				if parent.traj_duration_ticks != old_traj_dur_tick:
					self.element_resized.emit(parent.id + "::traj",
					                          _ElementView.tick_to_second(parent.traj_duration_ticks),
					                          old_traj_dur_sec)
			self.drag_undo_end.emit()
			if view.is_composite_part:
				p = view.elem
				log.debug(
					f"拖拽结束(复合): id={p.id[:8]}, part={view.part}, "
					f"start={p.start_tick}, traj_dur={p.traj_duration_ticks}, fw_dur={p.fw_duration_ticks}"
				)
			else:
				log.debug(
					f"拖拽结束: id={view.id[:8]}, name={view.name}, "
					f"start={view.start_time:.2f}s, dur={view.duration:.2f}s, end={view.end_time:.2f}s"
				)
		self._dragging = None
		self._dragging_edge = ""
		self._drag_start_pos = None

	def wheelEvent(self, event: QWheelEvent) -> None:
		event.ignore()
