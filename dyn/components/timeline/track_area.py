"""轨道区域 单个轨道的布局、绘制和交互."""
from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import Qt, Signal, QRect, QPoint, QEvent
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QFont, QPainterPath, QMouseEvent, QWheelEvent
from PySide6.QtWidgets import QWidget

from dyn.logging_config import get_logger

log = get_logger(__name__)

from dyn.models.elements import Element, ElementType, TrajectoryElement, FireworkElement, TrajFireworkElement, ColorRGB
from .theme import (
	palette_colors,
	TRACK_LABEL_WIDTH, TRACK_HEIGHT, BLOCK_MIN_WIDTH, PIXELS_PER_TICK_DEFAULT,
)

@dataclass
class _BlockLayout:
	element: Element
	rect: QRect

class _TFProxy(Element):
	"""代理 将 TrajFireworkElement 包装为独立轨迹或烟花.
	对 start_tick / duration_ticks 的读写直接操作父元素对应字段。
	"""

	def __init__(self, parent: TrajFireworkElement, part: str) -> None:
		self._parent = parent
		self._part = part  # "traj" | "fw"
		self.id = parent.id + ("::traj" if part == "traj" else "::fw")
		self.name = parent.name
		self.enabled = parent.enabled

	@property
	def element_type(self) -> ElementType:
		return ElementType.TRAJECTORY if self._part == "traj" else ElementType.FIREWORK

	@property
	def start_tick(self) -> int:
		if self._part == "traj":
			return self._parent.start_tick
		return self._parent.fw_start_tick

	@start_tick.setter
	def start_tick(self, v: int) -> None:
		if self._part == "traj":
			delta = v - self._parent.start_tick
			self._parent.start_tick = v
		else:
			self._parent.traj_duration_ticks = max(1, v - self._parent.start_tick)

	@property
	def duration_ticks(self) -> int:
		if self._part == "traj":
			return self._parent.traj_duration_ticks
		return self._parent.fw_duration_ticks

	@duration_ticks.setter
	def duration_ticks(self, v: int) -> None:
		if self._part == "traj":
			self._parent.traj_duration_ticks = max(1, v)
		else:
			self._parent.fw_duration_ticks = max(1, v)

	def to_json(self) -> dict:
		return self._parent.to_json()

class _TrackArea(QWidget):
	"""单个轨道区域（烟花或轨迹），支持独立垂直滚动."""

	element_selected = Signal(str)
	element_moved = Signal(str, int, int)
	element_resized = Signal(str, int, int)
	drag_update = Signal()
	drag_undo_begin = Signal()  # 拖拽开始 -> undo 宏开始
	drag_undo_end = Signal()  # 拖拽结束 -> undo 宏提交

	def __init__(self, label: str, parent=None) -> None:
		super().__init__(parent)
		self._label = label
		self._blocks: list[_BlockLayout] = []
		self._elements: list[Element] = []
		self._selected_id: str = ""
		self._pixels_per_tick: float = PIXELS_PER_TICK_DEFAULT
		self._scroll_offset: float = 0.0
		self._dragging: _BlockLayout | None = None
		self._dragging_edge: str = ""
		self._drag_start_pos: QPoint | None = None
		self._drag_start_tick: int = 0
		self._drag_start_duration: int = 0
		self._drag_parent_start: int = 0
		self._content_height: int = 100
		self._hovered_edge: str = ""
		self._hovered_block: _BlockLayout | None = None

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

	# 公共接口

	def set_data(self, elements: list[Element], ppt: float, scroll: float) -> None:
		self._elements = elements
		self._pixels_per_tick = ppt
		self._scroll_offset = scroll
		self._compute()

	def set_selection(self, element_id: str) -> None:
		self._selected_id = element_id
		self.update()

	def _match_selection(self, elem: Element, sel_id: str) -> bool:
		"""匹配选中 id，_TFProxy 支持父 id 反查."""
		if not sel_id:
			return False
		if elem.id == sel_id:
			return True
		if isinstance(elem, _TFProxy) and sel_id + "::fw" == elem.id:
			return True
		return False

	def set_view(self, ppt: float, scroll: float) -> None:
		self._pixels_per_tick = ppt
		self._scroll_offset = scroll
		self._compute()

	def _compute_and_update(self) -> None:
		"""重新计算布局并刷新（供另一轨道拖拽时调用）."""
		self._compute()
		self.update()

	@property
	def content_height(self) -> int:
		return self._content_height

	# 布局

	def _tick_to_x(self, tick: int) -> float:
		return TRACK_LABEL_WIDTH + tick * self._pixels_per_tick - self._scroll_offset

	def _x_to_tick(self, x: float) -> int:
		return max(0, int((x - TRACK_LABEL_WIDTH + self._scroll_offset) / self._pixels_per_tick))

	def _compute(self) -> None:
		self._blocks.clear()
		if not self._elements:
			self._content_height = 60
			self.update()
			return
		rows = self._assign_rows(self._elements)
		max_row = max(rows.values()) if rows else 0
		for elem in self._elements:
			row = rows.get(elem.id, 0)
			x = int(self._tick_to_x(elem.start_tick))
			w = max(BLOCK_MIN_WIDTH, int(elem.duration_ticks * self._pixels_per_tick))
			y = 4 + row * TRACK_HEIGHT
			self._blocks.append(_BlockLayout(element=elem, rect=QRect(x, y, w, TRACK_HEIGHT - 4)))
		self._content_height = 4 + (max_row + 1) * TRACK_HEIGHT + 8
		self.update()

	@staticmethod
	def _assign_rows(elements: list[Element]) -> dict[str, int]:
		sorted_elems = sorted(elements, key=lambda e: e.start_tick)
		row_ends: list[int] = []
		result: dict[str, int] = {}
		for elem in sorted_elems:
			placed = False
			for row_idx, row_end in enumerate(row_ends):
				if elem.start_tick >= row_end:
					row_ends[row_idx] = elem.end_tick
					result[elem.id] = row_idx
					placed = True
					break
			if not placed:
				result[elem.id] = len(row_ends)
				row_ends.append(elem.end_tick)
		return result

	# 绘制

	def paintEvent(self, event) -> None:
		p = QPainter(self)
		p.setRenderHint(QPainter.Antialiasing)
		try:
			p.fillRect(self.rect(), self._bg)
			# 标签背景（无文字，由覆盖层渲染）
			p.fillRect(QRect(0, 0, TRACK_LABEL_WIDTH, self.height()), self._label_bg)
			# 色块
			p.setClipRect(QRect(TRACK_LABEL_WIDTH, 0, self.width() - TRACK_LABEL_WIDTH, self.height()))
			for blk in self._blocks:
				self._paint_block(p, blk)
			p.setClipping(False)
		finally:
			p.end()

	def _paint_block(self, p: QPainter, blk: _BlockLayout) -> None:
		elem = blk.element
		r = blk.rect
		sel = self._match_selection(elem, self._selected_id)
		self._paint_block_gradient(p, elem, r, sel)
		if sel:
			c = self._block_color(elem).lighter(140);
			c.setAlpha(230)
			p.setPen(QPen(self._sel_color, 2))
			p.drawRoundedRect(r.adjusted(1, 1, -1, -1), 3, 3)
		if r.width() > 20:
			p.setPen(QPen(QColor(255, 255, 255), 1))
			f = QFont();
			f.setPointSize(7);
			p.setFont(f)
			p.drawText(r.adjusted(4, 0, -4, 0), Qt.AlignVCenter | Qt.AlignLeft, elem.name)
		if r.width() > 36:
			p.setPen(QPen(QColor(255, 255, 255, 150), 1))
			f2 = QFont();
			f2.setPointSize(6);
			p.setFont(f2)
			p.drawText(QRect(r.right() - 18, r.top() + 2, 14, r.height() - 4), Qt.AlignCenter, self._icon(elem))

	def _paint_block_gradient(self, p: QPainter, elem: Element, r: QRect, sel: bool) -> None:
		"""渲染色块：支持左右分半（渐变）和四象限（双层烟花）."""
		disabled = not elem.enabled
		if isinstance(elem, _TFProxy):
			parent = elem._parent
			if elem._part == "traj":
				c_start, c_end = parent.traj_color.start, parent.traj_color.end
				use_grad = parent.traj_color.use_gradient
				layers = 1
			else:
				use_grad = parent.inner_color.use_gradient
				layers = 2 if parent.fw_type == "double_layer" else 1
				c_start = parent.inner_color.start;
				c_end = parent.inner_color.end
				c_outer_start = parent.outer_color.start;
				c_outer_end = parent.outer_color.end
		elif isinstance(elem, TrajectoryElement):
			c_start, c_end = elem.traj_color.start, elem.traj_color.end
			use_grad = elem.traj_color.use_gradient;
			layers = 1
		elif isinstance(elem, FireworkElement):
			use_grad = elem.inner_color.use_gradient
			layers = 2 if elem.fw_type == "double_layer" else 1
			c_start = elem.inner_color.start;
			c_end = elem.inner_color.end
			c_outer_start = elem.outer_color.start;
			c_outer_end = elem.outer_color.end
		else:
			c_start = c_end = ColorRGB(128, 128, 128)
			use_grad = False;
			layers = 1

		def qc(c, alpha=200):
			return QColor(max(c.r // 6, 15) if disabled else c.r,
			              max(c.g // 6, 15) if disabled else c.g,
			              max(c.b // 6, 15) if disabled else c.b, alpha)

		p.setClipRect(r)
		if layers == 2:
			half_w = r.width() // 2;
			half_h = r.height() // 2
			in_grad = None;
			out_grad = None
			if isinstance(elem, _TFProxy):
				in_grad = elem._parent.inner_color.use_gradient
				out_grad = elem._parent.outer_color.use_gradient
			elif isinstance(elem, FireworkElement):
				in_grad = elem.inner_color.use_gradient
				out_grad = elem.outer_color.use_gradient
			# 上层（内层）：渐变则分色，否则单一色
			if in_grad:
				p.fillRect(QRect(r.x(), r.y(), half_w, half_h), QBrush(qc(c_start)))
				p.fillRect(QRect(r.x() + half_w, r.y(), r.width() - half_w, half_h), QBrush(qc(c_end)))
			else:
				p.fillRect(QRect(r.x(), r.y(), r.width(), half_h), QBrush(qc(c_start)))
			# 下层（外层）：渐变则分色，否则单一色
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
			path = QPainterPath();
			path.addRoundedRect(r, 3, 3)
			p.fillPath(path, QBrush(qc(c_start)))
		p.setClipping(False)

	@staticmethod
	def _block_color(elem: Element) -> QColor:
		if isinstance(elem, _TFProxy):
			parent = elem._parent
			if elem._part == "traj":
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
	def _icon(elem: Element) -> str:
		if isinstance(elem, _TFProxy):
			parent = elem._parent
			if elem._part == "traj":
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

	# 交互

	def mousePressEvent(self, event: QMouseEvent) -> None:
		if event.button() != Qt.LeftButton: return
		x, y = event.position().x(), event.position().y()
		for blk in reversed(self._blocks):
			if blk.rect.contains(int(x), int(y)):
				self._dragging = blk
				self._drag_start_pos = QPoint(int(x), int(y))
				self._drag_start_tick = blk.element.start_tick
				self._drag_start_duration = blk.element.duration_ticks
				if isinstance(blk.element, _TFProxy):
					self._drag_parent_start = blk.element._parent.start_tick
					log.debug(
						f"时间线拖拽开始: id={blk.element.id}, part={blk.element._part}, "
						f"tick={blk.element.start_tick}, dur={blk.element.duration_ticks}, "
						f"parent_start={blk.element._parent.start_tick}"
					)
				else:
					self._drag_parent_start = blk.element.start_tick
					log.debug(
						f"时间线拖拽开始: id={blk.element.id}, type={blk.element.element_type.name}, "
						f"tick={blk.element.start_tick}, dur={blk.element.duration_ticks}"
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
			dt = int(dx / self._pixels_per_tick)
			elem = self._dragging.element
			if self._dragging_edge == "move":
				if isinstance(elem, _TFProxy):
					elem._parent.start_tick = max(0, self._drag_parent_start + dt)
				else:
					elem.start_tick = max(0, self._drag_start_tick + dt)
			elif self._dragging_edge == "left":
				ns = max(0, self._drag_start_tick + dt)
				nd = self._drag_start_duration + (self._drag_start_tick - ns)
				if nd >= 1: elem.start_tick = ns; elem.duration_ticks = nd
			elif self._dragging_edge == "right":
				elem.duration_ticks = max(1, self._drag_start_duration + dt)
			self._compute();
			self.update()
			self.drag_update.emit();
			return
		# 光标样式
		x, y = event.position().x(), event.position().y()
		for blk in self._blocks:
			r = blk.rect
			if r.contains(int(x), int(y)):
				margin = 6
				if x <= r.left() + margin: self.setCursor(Qt.SizeHorCursor); return
				if x >= r.right() - margin: self.setCursor(Qt.SizeHorCursor); return
				self.setCursor(Qt.PointingHandCursor);
				return
		if x > TRACK_LABEL_WIDTH: self.setCursor(Qt.ArrowCursor)

	def mouseReleaseEvent(self, event: QMouseEvent) -> None:
		if self._dragging:
			self.drag_undo_begin.emit()  # 开始宏 一次拖拽的多个属性变更合并为一个撤销步骤
			elem = self._dragging.element
			# element_moved（start_tick 变更）
			if self._dragging_edge == "move" and isinstance(elem, _TFProxy):
				# 所有 TF 代理的 middle-drag 均移动整个元素 -> parent.start_tick 变更
				parent = elem._parent
				if parent.start_tick != self._drag_parent_start:
					self.element_moved.emit(elem.id, parent.start_tick, self._drag_parent_start)
			elif not isinstance(elem, _TFProxy) or elem._part == "traj":
				# 非代理元素（start_tick 直接可写）或 traj 代理边缘拖拽（start_tick == parent.start_tick）
				# fw 代理的边缘拖拽在此被排除 其 start_tick 为派生值，实际变更为 traj_duration
				if elem.start_tick != self._drag_start_tick:
					self.element_moved.emit(elem.id, elem.start_tick, self._drag_start_tick)
			# element_resized（duration_ticks 变更，所有元素类型）
			if elem.duration_ticks != self._drag_start_duration:
				self.element_resized.emit(elem.id, elem.duration_ticks, self._drag_start_duration)
			# fw 代理左边缘拖拽改变了 traj_duration + fw_duration，需额外记录
			# fw 代理的 start_tick 为派生值 (parent.start_tick + traj_duration_ticks)，
			# 其变更实际对应 parent.traj_duration_ticks 变更，不可用 element_moved 追踪
			if isinstance(elem, _TFProxy) and elem._part == "fw" and self._dragging_edge == "left":
				parent = elem._parent
				old_traj_dur = self._drag_start_tick - self._drag_parent_start
				if parent.traj_duration_ticks != old_traj_dur:
					self.element_resized.emit(parent.id + "::traj", parent.traj_duration_ticks, old_traj_dur)
			self.drag_undo_end.emit()  # 结束宏
			# 输出拖拽后元素的最终 tick 状态
			if isinstance(elem, _TFProxy):
				p = elem._parent
				log.debug(
					f"拖拽结束: id={p.id[:8]}, part={elem._part}, "
					f"start={p.start_tick}, traj_dur={p.traj_duration_ticks}, fw_dur={p.fw_duration_ticks}, "
					f"traj_end={p.start_tick + p.traj_duration_ticks}, fw_end={p.start_tick + p.traj_duration_ticks + p.fw_duration_ticks}"
				)
			else:
				log.debug(
					f"拖拽结束: id={elem.id[:8]}, name={elem.name}, "
					f"start={elem.start_tick}, dur={elem.duration_ticks}, end={elem.end_tick}"
				)
		self._dragging = None;
		self._dragging_edge = "";
		self._drag_start_pos = None

	def wheelEvent(self, event: QWheelEvent) -> None:
		event.ignore()  # 向上传递到 TimelineWidget
