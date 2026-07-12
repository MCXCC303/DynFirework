"""元素控制器 管理所有时间线元素的 CRUD 和属性同步.
按后端类型统一存储元素 (cb: tick / df: 秒)，加载时按 Project.backend 直存.
"""
from __future__ import annotations

import copy
from typing import Any
from uuid import uuid4

from PySide6.QtCore import QObject, Signal

from dyn.logging_config import get_logger

log = get_logger(__name__)

from dyn.models.project import Backend
from dyn.models.df.base import ElementCategory, Element as DfElement
from dyn.models.df.composites import CompositeElement as DfCompositeElement
from dyn.models.df.effects import EffectElement as DfEffectElement
from dyn.models.df.fireworks import FireworkElement as DfFireworkElement
from dyn.models.df.trajectories import TrajectoryElement as DfTrajectoryElement
from dyn.models.df.values import (
	FireworkType as DfFireworkType, TrajectoryType as DfTrajectoryType,
	EffectType, CompositeType, Position as DfPosition,
)
from dyn.models.cb.base import ElementType as CbElementType
from dyn.models.cb.trajectories import TrajectoryElement as CbTrajectoryElement
from dyn.models.cb.fireworks import FireworkElement as CbFireworkElement
from dyn.models.cb.composites import TrajFireworkElement as CbTrajFireworkElement
from dyn.models.cb.values import Position as CbPosition

# DF 元素工厂映射
_DF_ELEMENT_CLASSES: dict[ElementCategory, type] = {
	ElementCategory.FIREWORK: DfFireworkElement,
	ElementCategory.TRAJECTORY: DfTrajectoryElement,
	ElementCategory.EFFECT: DfEffectElement,
	ElementCategory.COMPOSITE: DfCompositeElement,
}

_DF_DEFAULT_TYPE_KEYS: dict[ElementCategory, str] = {
	ElementCategory.FIREWORK: "single_layer",
	ElementCategory.TRAJECTORY: "launch",
	ElementCategory.EFFECT: "beam",
	ElementCategory.COMPOSITE: "secondary_explosion",
}

# CB 元素工厂映射
_CB_ELEMENT_CLASSES: dict[CbElementType, type] = {
	CbElementType.TRAJECTORY: CbTrajectoryElement,
	CbElementType.FIREWORK: CbFireworkElement,
	CbElementType.TRAJ_FIREWORK: CbTrajFireworkElement,
}

_CB_DEFAULT_TYPE_KEYS: dict[CbElementType, str] = {
	CbElementType.TRAJECTORY: "launch",
	CbElementType.FIREWORK: "single_layer",
	CbElementType.TRAJ_FIREWORK: "launch",
}

DF_CATEGORY_DISPLAY: dict[ElementCategory, str] = {
	ElementCategory.FIREWORK: "爆炸",
	ElementCategory.TRAJECTORY: "轨迹",
	ElementCategory.EFFECT: "效果",
	ElementCategory.COMPOSITE: "复合",
}

CB_CATEGORY_DISPLAY: dict[CbElementType, str] = {
	CbElementType.TRAJECTORY: "轨迹",
	CbElementType.FIREWORK: "烟花",
	CbElementType.TRAJ_FIREWORK: "轨迹烟花",
}

CATEGORY_DISPLAY: dict = DF_CATEGORY_DISPLAY

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
	"""中央元素管理服务 按后端类型统一存储元素."""

	element_added = Signal(object)
	element_removed = Signal(str)
	element_changed = Signal(str, str, object)
	selection_changed = Signal(str)

	def __init__(self, parent: QObject | None = None, backend: Backend = Backend.DF) -> None:
		super().__init__(parent)
		self._backend = backend
		self._elements: dict[str, Any] = {}
		self._selected_id: str = ""

	@property
	def backend(self) -> Backend:
		return self._backend

	def set_backend(self, backend: Backend) -> None:
		self._backend = backend
		self._elements.clear()
		self._selected_id = ""

	@property
	def category_display(self) -> dict:
		if self._backend == Backend.CB:
			return CB_CATEGORY_DISPLAY
		return DF_CATEGORY_DISPLAY

	@property
	def categories(self) -> list:
		if self._backend == Backend.CB:
			return list(CbElementType)
		return list(ElementCategory)

	# 查询

	@property
	def elements(self):
		return self._elements

	@property
	def selected_element(self) -> Any:
		return self._elements.get(self._selected_id)

	@property
	def selected_id(self) -> str:
		return self._selected_id

	@property
	def all_elements(self) -> list:
		if self._backend == Backend.CB:
			return sorted(self._elements.values(), key=lambda e: e.start_tick)
		return sorted(self._elements.values(), key=lambda e: e.start_time)

	def get_elements_by_category(self, cat) -> list:
		if self._backend == Backend.CB:
			return [e for e in self._elements.values() if e.element_type == cat]
		return [e for e in self._elements.values() if e.category == cat]

	@property
	def trajectory_count(self) -> int:
		cat = CbElementType.TRAJECTORY if self._backend == Backend.CB else ElementCategory.TRAJECTORY
		return len(self.get_elements_by_category(cat))

	@property
	def firework_count(self) -> int:
		cat = CbElementType.FIREWORK if self._backend == Backend.CB else ElementCategory.FIREWORK
		return len(self.get_elements_by_category(cat))

	@property
	def traj_firework_count(self) -> int:
		if self._backend == Backend.CB:
			return len(self.get_elements_by_category(CbElementType.TRAJ_FIREWORK))
		return len(self.get_elements_by_category(ElementCategory.COMPOSITE))

	@property
	def effect_count(self) -> int:
		return len(self.get_elements_by_category(ElementCategory.EFFECT))

	@property
	def total_duration(self) -> float:
		if not self._elements:
			return 0.0
		if self._backend == Backend.CB:
			return max(e.end_tick for e in self._elements.values()) / 20.0
		return max(e.end_time for e in self._elements.values())

	def get_element(self, element_id: str) -> Any:
		return self._elements.get(element_id)

	# 选择

	def select_element(self, element_id: str) -> None:
		self._selected_id = element_id
		self.selection_changed.emit(element_id)

	def clear_selection(self) -> None:
		self._selected_id = ""
		self.selection_changed.emit("")

	# 创建 / 添加

	def add_element(self, elem) -> None:
		if elem.id in self._elements:
			log.warning(f"覆盖已存在元素: id={elem.id}, name={elem.name}")
		self._elements[elem.id] = elem
		log.debug(f"添加元素: id={elem.id} name={elem.name}")
		self.element_added.emit(elem)

	def create_element(
			self, category, type_key: str = "",
			name: str = "", start_time: float = 0.0,
	):
		"""工厂方法 按 backend 创建对应类型的元素.
		category: DF 用 ElementCategory，CB 用 ElementType
		start_time: DF 为秒(float)，CB 为 tick(int)
		"""
		if self._backend == Backend.CB:
			return self._create_cb_element(category, type_key, name, int(start_time))
		return self._create_df_element(category, type_key, name, start_time)

	def _create_df_element(
			self, category: ElementCategory, type_key: str,
			name: str, start_time: float,
	) -> DfElement:
		"""创建 df 元素."""
		cls = _DF_ELEMENT_CLASSES.get(category)
		if cls is None:
			raise ValueError(f"Unknown category: {category}")

		tk = type_key or _DF_DEFAULT_TYPE_KEYS.get(category, "")
		cat_label = DF_CATEGORY_DISPLAY.get(category, category.value)
		count = len(self.get_elements_by_category(category))
		elem_name = name or f"{cat_label} {count}"

		if category == ElementCategory.FIREWORK:
			elem = DfFireworkElement(
				name=elem_name, start_time=start_time,
				fw_type=DfFireworkType(tk) if tk else DfFireworkType.SINGLE_LAYER,
			)
		elif category == ElementCategory.TRAJECTORY:
			elem = DfTrajectoryElement(
				name=elem_name, start_time=start_time,
				traj_type=DfTrajectoryType(tk) if tk else DfTrajectoryType.LAUNCH,
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

	def _create_cb_element(
			self, element_type: CbElementType, type_key: str,
			name: str, start_tick: int,
	):
		"""创建 cb 元素."""
		cls = _CB_ELEMENT_CLASSES.get(element_type)
		if cls is None:
			raise ValueError(f"Unknown element type: {element_type}")

		tk = type_key or _CB_DEFAULT_TYPE_KEYS.get(element_type, "")
		cat_label = CB_CATEGORY_DISPLAY.get(element_type, element_type.name)
		count = len(self.get_elements_by_category(element_type))
		elem_name = name or f"{cat_label} {count}"

		if element_type == CbElementType.TRAJECTORY:
			elem = CbTrajectoryElement(
				name=elem_name, start_tick=start_tick,
				traj_type=tk,
			)
		elif element_type == CbElementType.FIREWORK:
			elem = CbFireworkElement(
				name=elem_name, start_tick=start_tick,
				fw_type=tk,
			)
		elif element_type == CbElementType.TRAJ_FIREWORK:
			elem = CbTrajFireworkElement(
				name=elem_name, start_tick=start_tick,
				traj_type=tk,
				fw_type="single_layer",
			)
		else:
			raise ValueError(f"Unknown element type: {element_type}")

		return elem

	# 删除

	def remove_element(self, element_id: str) -> Any:
		removed = self._elements.pop(element_id, None)
		if removed is None:
			log.warning(f"删除失败: 元素不存在 id={element_id}")
			return None
		log.debug(f"删除元素: id={element_id} name={removed.name}")
		if self._selected_id == element_id:
			self._selected_id = ""
			self.selection_changed.emit("")
		self.element_removed.emit(element_id)
		return removed

	def remove_selected(self) -> Any:
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

		if self._backend == Backend.CB:
			pos = CbPosition(x=x, y=y, z=z)
			if isinstance(elem, CbTrajFireworkElement):
				if which == "end":
					elem.mid_position = pos
				else:
					elem.start_position = pos
			elif isinstance(elem, CbTrajectoryElement):
				if which == "end":
					elem.end_position = pos
				else:
					elem.start_position = pos
			elif isinstance(elem, CbFireworkElement):
				elem.position = pos
		else:
			pos = DfPosition(x=x, y=y, z=z)
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
				elif which == "ce_pos":
					elem.ce_position = pos
				else:
					elem.position = pos

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

	def clone_element(self, element_id: str) -> Any:
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
		self._backend = project.backend
		self._elements.clear()
		self._selected_id = ""

		for e in project.elements:
			self._elements[e.id] = e

	def to_project(self, project) -> None:
		"""将元素写回 Project 单列表."""
		project.elements = list(self._elements.values())
