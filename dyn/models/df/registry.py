"""元素类型注册表 注册式扩展，新增类型添加一行 register_type()."""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from dyn.logging_config import get_logger
from .base import ElementCategory

log = get_logger(__name__)

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
	if def_.type_key in ELEMENT_TYPE_REGISTRY:
		log.warning(f"覆盖已注册的类型键: {def_.type_key}")
	ELEMENT_TYPE_REGISTRY[def_.type_key] = def_

def get_type_def(type_key: str) -> ElementTypeDef:
	if type_key not in ELEMENT_TYPE_REGISTRY:
		log.warning(f"未注册的类型键: {type_key}")
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
	log.error(f"未知元素类型: {type(elem)}")
	raise ValueError(f"Unknown element type: {type(elem)}")
