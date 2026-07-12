"""统一元素代理层 秒单位视图，封装 V1 (cb) tick 转 second 转换和 V2 直通."""
from __future__ import annotations

from enum import Enum

from dyn.models.cb.base import Element as CbElement
from dyn.models.cb.composites import TrajFireworkElement
from dyn.models.df.base import Element

class _ElementView:
	"""秒单位视图，封装 cb/df 元素，统一 start_time/duration 接口.

	简单元素：_elem = 元素自身，_part = None
	复合元素子部件：_elem = 复合元素，_part = "traj"|"fw"|...
	"""

	def __init__(self, elem, part: str | None = None):
		self._elem = elem
		self._part = part

	@property
	def _is_cb(self) -> bool:
		return isinstance(self._elem, CbElement)

	@property
	def start_time(self) -> float | int | None:
		if self._is_cb:
			if self._part is None:
				return self._elem.start_tick / 20.0
			elif self._part == "traj":
				return self._elem.start_tick / 20.0
			elif self._part == "fw":
				return (self._elem.start_tick + self._elem.traj_duration_ticks) / 20.0
			return None
		else:
			return self._elem.start_time

	@start_time.setter
	def start_time(self, v: float | int):
		if self._is_cb:
			tick = max(0, round(v * 20))
			if self._part is None:
				self._elem.start_tick = tick
			elif self._part == "traj":
				self._elem.start_tick = tick
			elif self._part == "fw":
				new_traj_dur = max(1, tick - self._elem.start_tick)
				self._elem.traj_duration_ticks = new_traj_dur
		else:
			self._elem.start_time = max(0.0, v)

	@property
	def duration(self) -> float | int | None:
		if self._is_cb:
			if self._part is None:
				return self._elem.duration_ticks / 20.0
			elif self._part == "traj":
				return self._elem.traj_duration_ticks / 20.0
			elif self._part == "fw":
				return self._elem.fw_duration_ticks / 20.0
			return None
		else:
			return self._elem.duration

	@duration.setter
	def duration(self, v: float):
		tick = max(1, round(v * 20))
		if self._is_cb:
			if self._part is None:
				self._elem.duration_ticks = tick
			elif self._part == "traj":
				self._elem.traj_duration_ticks = tick
			elif self._part == "fw":
				self._elem.fw_duration_ticks = tick
		else:
			self._elem.duration = max(0.05, v)

	@property
	def end_time(self) -> float | int | None:
		return self.start_time + self.duration

	@property
	def id(self) -> str:
		if self._part is None:
			return self._elem.id
		return self._elem.id + "::" + self._part

	@property
	def name(self) -> str:
		return self._elem.name

	@property
	def enabled(self) -> bool:
		return self._elem.enabled

	@property
	def is_composite_part(self) -> bool:
		return self._part is not None

	def is_tf(self) -> bool:
		return isinstance(self._elem, TrajFireworkElement)

	@staticmethod
	def tick_to_second(tick: int) -> float:
		return tick / 20.0

	@staticmethod
	def second_to_tick(sec: float) -> int:
		return max(0, round(sec * 20))

	@staticmethod
	def _second_to_tick_min1(sec: float) -> int:
		return max(1, round(sec * 20))

	@property
	def elem(self):
		return self._elem

	@property
	def part(self):
		return self._part

def create_track_views(elements: list) -> dict[str, list[_ElementView]]:
	"""将元素列表转换为四轨道的视图列表.
	cb (ColorBlock) 元素通过 element_type 属性识别，df (DynFirework) 元素通过 category 属性识别.
	"""
	from dyn.models.cb.base import ElementType as CbElementType
	from dyn.models.df.base import ElementCategory

	views: dict[str, list[_ElementView]] = {
		"fw": [], "traj": [], "effect": [], "composite": [],
	}
	for elem in elements:
		if isinstance(elem, CbElement):
			if isinstance(elem, TrajFireworkElement):
				views["traj"].append(_ElementView(elem, "traj"))
				views["fw"].append(_ElementView(elem, "fw"))
				views["composite"].append(_ElementView(elem))
			elif elem.element_type == CbElementType.TRAJECTORY:
				views["traj"].append(_ElementView(elem))
			elif elem.element_type == CbElementType.FIREWORK:
				views["fw"].append(_ElementView(elem))
		elif isinstance(elem, Element):
			cat = elem.category
			if cat == ElementCategory.FIREWORK:
				views["fw"].append(_ElementView(elem))
			elif cat == ElementCategory.TRAJECTORY:
				views["traj"].append(_ElementView(elem))
			elif cat == ElementCategory.EFFECT:
				views["effect"].append(_ElementView(elem))
			elif cat == ElementCategory.COMPOSITE:
				views["composite"].append(_ElementView(elem))
				_append_composite_parts(views, elem)
	return views

def _append_composite_parts(views: dict, elem) -> None:
	from dyn.models.df.composites import CompositeElement
	if not isinstance(elem, CompositeElement):
		return
	ct = elem.composite_type
	if isinstance(ct, Enum):
		ct = ct.value
	if ct == "secondary_explosion":
		views["fw"].append(_ElementView(elem, "primary"))
		views["fw"].append(_ElementView(elem, "secondary"))
	elif ct == "combo_ec":
		views["fw"].append(_ElementView(elem, "clustered"))
		views["fw"].append(_ElementView(elem, "expanding"))
