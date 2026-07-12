"""元素控制器 管理所有时间线元素的 CRUD 和属性同步.
按后端类型统一存储元素 (cb: tick / df: 秒)，加载时按 Project.backend 直存.
"""
from __future__ import annotations

import copy
from typing import TYPE_CHECKING
from uuid import uuid4

from PySide6.QtCore import QObject, Signal

from dyn.logging_config import get_logger

log = get_logger(__name__)

from dyn.models.df.base import ElementCategory, Element as DfElement
from dyn.models.df.composites import CompositeElement as DfCompositeElement
from dyn.models.df.effects import EffectElement as DfEffectElement
from dyn.models.df.fireworks import FireworkElement as DfFireworkElement
from dyn.models.df.trajectories import TrajectoryElement as DfTrajectoryElement
from dyn.models.cb import Position as CbPosition
from dyn.models.cb import TrajFireworkElement as CbTrajFireworkElement
from dyn.models.df.values import (
	FireworkType, TrajectoryType, EffectType, CompositeType, Position,
)

if TYPE_CHECKING:
	pass

_ELEMENT_CLASSES: dict[ElementCategory, type] = {
	ElementCategory.FIREWORK: DfFireworkElement,
	ElementCategory.TRAJECTORY: DfTrajectoryElement,
	ElementCategory.EFFECT: DfEffectElement,
	ElementCategory.COMPOSITE: DfCompositeElement,
}

_DEFAULT_TYPE_KEYS: dict[ElementCategory, str] = {
	ElementCategory.FIREWORK: "single_layer",
	ElementCategory.TRAJECTORY: "launch",
	ElementCategory.EFFECT: "beam",
	ElementCategory.COMPOSITE: "secondary_explosion",
}

CATEGORY_DISPLAY: dict[ElementCategory, str] = {
	ElementCategory.FIREWORK: "爆炸",
	ElementCategory.TRAJECTORY: "轨迹",
	ElementCategory.EFFECT: "效果",
	ElementCategory.COMPOSITE: "复合",
}

# 由 property_panel 直接赋值的复杂类型属性，不需要 undo 记录
_COMPLEX_KEYS: frozenset[str] = frozenset({
	"position", "extra", "end_position", "traj_type", "fw_type",
	"traj_gradient", "inner_gradient", "outer_gradient",
	"traj_color_start", "traj_color_end",
	"inner_color_start", "inner_color_end",
	"outer_color_start", "outer_color_end",
	"element_type", "effect_type", "composite_type",
	"start_position", "end_position",
	"inner_color", "outer_color",
	"traj_color", "start_color", "end_color",
	"beam_start_color", "beam_end_color",
	"spray_start_color", "spray_end_color",
	"dh_color1", "dh_color2", "rr_color",
	"se_primary_color", "se_secondary_color",
	"ce_cluster_color", "ce_sphere_color",
	"se_start_position", "se_mid_position",
	"ce_position", "shell_color",
})

# 代理 ID 后缀列表
_PROXY_SUFFIXES: tuple[str, ...] = (
	"::fw", "::traj", "::primary", "::secondary",
	"::clustered", "::expanding",
)

class ElementController(QObject):
	"""中央元素管理服务 df: 统一存储 df 元素."""

	element_added = Signal(DfElement)
	element_removed = Signal(str)
	element_changed = Signal(str, str, object)
	selection_changed = Signal(str)

	def __init__(self, parent: QObject | None = None) -> None:
		super().__init__(parent)
		self._elements: dict[str, DfElement] = {}
		self._selected_id: str = ""

	# 查询

	@property
	def elements(self):
		return self._elements

	@property
	def selected_element(self) -> DfElement | None:
		return self._elements.get(self._selected_id)

	@property
	def selected_id(self) -> str:
		return self._selected_id

	@property
	def all_elements(self) -> list[DfElement]:
		return sorted(self._elements.values(), key=lambda e: e.start_time)

	def get_elements_by_category(self, cat: ElementCategory) -> list[DfElement]:
		return [e for e in self._elements.values() if e.category == cat]

	@property
	def trajectory_count(self) -> int:
		return len(self.get_elements_by_category(ElementCategory.TRAJECTORY))

	@property
	def firework_count(self) -> int:
		return len(self.get_elements_by_category(ElementCategory.FIREWORK))

	@property
	def traj_firework_count(self) -> int:
		return len(self.get_elements_by_category(ElementCategory.COMPOSITE))

	@property
	def effect_count(self) -> int:
		return len(self.get_elements_by_category(ElementCategory.EFFECT))

	@property
	def total_duration(self) -> float:
		if not self._elements:
			return 0.0
		return max(e.end_time for e in self._elements.values())

	def get_element(self, element_id: str) -> DfElement | None:
		return self._elements.get(element_id)

	# 选择

	def select_element(self, element_id: str) -> None:
		self._selected_id = element_id
		self.selection_changed.emit(element_id)

	def clear_selection(self) -> None:
		self._selected_id = ""
		self.selection_changed.emit("")

	# 创建 / 添加

	def add_element(self, elem: DfElement) -> None:
		if elem.id in self._elements:
			log.warning(f"覆盖已存在元素: id={elem.id}, name={elem.name}")
		self._elements[elem.id] = elem
		log.debug(f"添加元素: category={elem.category.value} id={elem.id} name={elem.name}")
		self.element_added.emit(elem)

	def create_element(
			self, category: ElementCategory, type_key: str = "",
			name: str = "", start_time: float = 0.0,
	) -> DfElement:
		"""工厂方法 创建指定类别 + 子类型的 df 元素."""
		cls = _ELEMENT_CLASSES.get(category)
		if cls is None:
			raise ValueError(f"Unknown category: {category}")

		tk = type_key or _DEFAULT_TYPE_KEYS.get(category, "")
		cat_label = CATEGORY_DISPLAY.get(category, category.value)
		count = len(self.get_elements_by_category(category))
		elem_name = name or f"{cat_label} {count}"

		if category == ElementCategory.FIREWORK:
			elem = DfFireworkElement(
				name=elem_name, start_time=start_time,
				fw_type=FireworkType(tk) if tk else FireworkType.SINGLE_LAYER,
			)
		elif category == ElementCategory.TRAJECTORY:
			elem = DfTrajectoryElement(
				name=elem_name, start_time=start_time,
				traj_type=TrajectoryType(tk) if tk else TrajectoryType.LAUNCH,
			)
		elif category == ElementCategory.EFFECT:
			elem = DfEffectElement(
				name=elem_name, start_time=start_time,
				effect_type=EffectType(tk) if tk else EffectType.BEAM,
			)
		elif category == ElementCategory.COMPOSITE:
			elem = DfCompositeElement(
				name=elem_name, start_time=start_time,
				composite_type=CompositeType(tk) if tk else CompositeType.SECONDARY_EXPLOSION,
			)
		else:
			raise ValueError(f"Unknown category: {category}")

		return elem

	# 删除

	def remove_element(self, element_id: str) -> DfElement | None:
		removed = self._elements.pop(element_id, None)
		if removed is None:
			log.warning(f"删除失败: 元素不存在 id={element_id}")
			return None
		log.debug(f"删除元素: category={removed.category.value} id={element_id} name={removed.name}")
		if self._selected_id == element_id:
			self._selected_id = ""
			self.selection_changed.emit("")
		self.element_removed.emit(element_id)
		return removed

	def remove_selected(self) -> DfElement | None:
		if not self._selected_id:
			return None
		return self.remove_element(self._selected_id)

	# 属性修改

	def set_property(self, element_id: str, key: str, value: object) -> bool:
		elem = self._elements.get(element_id)
		if elem is None:
			log.warning(f"set_property 失败: 元素不存在 id={element_id}, key={key}")
			return False
		if not hasattr(elem, key):
			log.warning(f"set_property 失败: 元素无此属性 id={element_id}, key={key}, type={type(elem).__name__}")
			return False
		old_val = getattr(elem, key, None)
		setattr(elem, key, value)
		log.debug(f"set_property: id={element_id}, name={elem.name}, {key}: {old_val} -> {value}")
		self.element_changed.emit(element_id, key, value)
		return True

	# 位置设置 按元素类型分发

	def set_position(self, element_id: str, which: str,
	                 x: float, y: float, z: float) -> bool:
		"""设置元素的位置字段 按类型自动分发到正确的属性."""
		elem = self._elements.get(element_id)
		if elem is None:
			return False

		pos = Position(x=x, y=y, z=z)

		if isinstance(elem, DfTrajectoryElement):
			if which == "end":
				elem.end_position = pos
			else:
				elem.start_position = pos
		elif isinstance(elem, DfFireworkElement):
			elem.position = pos
		elif isinstance(elem, DfEffectElement):
			elem.position = pos
		elif isinstance(elem, DfCompositeElement):
			if which == "se_start":
				elem.se_start_position = pos
			elif which == "se_mid":
				elem.se_mid_position = pos
			else:
				elem.position = pos
		else:
			# cb 兼容
			cb_pos = CbPosition(x=x, y=y, z=z)
			if which == "end":
				if isinstance(elem, CbTrajFireworkElement):
					elem.mid_position = cb_pos
				elif isinstance(elem, DfTrajectoryElement):
					elem.end_position = cb_pos
			else:
				if isinstance(elem, CbTrajFireworkElement):
					elem.start_position = cb_pos
				elif isinstance(elem, DfTrajectoryElement):
					elem.start_position = cb_pos
				elif isinstance(elem, DfFireworkElement):
					elem.position = cb_pos

		self.element_changed.emit(element_id, "position", pos)
		return True

	# 属性变更协调 区分复杂类型(面板已直接赋值)和简单类型(需undo)

	def apply_property_change(self, element_id: str, key: str,
	                          value: object, old_value: object) -> bool:
		"""应用属性变更 复杂类型(面板已直改)返回True，简单类型执行 set_property 返回False(需undo)."""
		if key in _COMPLEX_KEYS:
			return True
		self.set_property(element_id, key, value)
		return False

	@staticmethod
	def resolve_proxy_id(element_id: str) -> tuple[str, str]:
		"""解析代理 ID 返回 (real_id, part)."""
		for suffix in _PROXY_SUFFIXES:
			if element_id.endswith(suffix):
				return element_id[:-len(suffix)], suffix[2:]
		return element_id, ""

	# 克隆

	def clone_element(self, element_id: str) -> DfElement | None:
		elem = self._elements.get(element_id)
		if elem is None:
			return None
		cloned = copy.deepcopy(elem)
		cloned.id = str(uuid4())
		cloned.name = f"{elem.name} (副本)"
		return cloned

	# 项目同步

	def load_from_project(self, project) -> None:
		"""从 Project 加载元素 按后端类型直接存入."""
		self._elements.clear()
		self._selected_id = ""

		for e in project.elements:
			self._elements[e.id] = e

	def to_project(self, project) -> None:
		"""将元素写回 Project V2 单列表."""
		project.elements = list(self._elements.values())

		# 同时填充 V1 三列表以保持向后兼容
		project.trajectories = []
		project.fireworks = []
		if hasattr(project, 'traj_fireworks'):
			project.traj_fireworks = []
