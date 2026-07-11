"""元素类型注册表 注册式扩展，新增类型添加一行 register_type()."""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .base import ElementCategory

if TYPE_CHECKING:
	from .base import Element

@dataclass
class ElementTypeDef:
	type_key: str
	category: ElementCategory
	display_name: str
	element_class: type
	form_class: type = None
	export_func: str = ""
	icon: str = ""

ELEMENT_TYPE_REGISTRY: dict[str, ElementTypeDef] = {}

def register_type(def_: ElementTypeDef) -> None:
	ELEMENT_TYPE_REGISTRY[def_.type_key] = def_

def get_type_def(type_key: str) -> ElementTypeDef:
	return ELEMENT_TYPE_REGISTRY[type_key]

def get_types_by_category(cat: ElementCategory) -> list[ElementTypeDef]:
	return [d for d in ELEMENT_TYPE_REGISTRY.values() if d.category == cat]

def get_type_key(elem: Element) -> str:
	from .fireworks import FireworkElement
	from .trajectories import TrajectoryElement
	from .effects import EffectElement
	from .composites import CompositeElement

	if isinstance(elem, FireworkElement):
		return elem.fw_type.value
	if isinstance(elem, TrajectoryElement):
		return elem.traj_type.value
	if isinstance(elem, EffectElement):
		return elem.effect_type.value
	if isinstance(elem, CompositeElement):
		return elem.composite_type.value
	raise ValueError(f"Unknown element type: {type(elem)}")
