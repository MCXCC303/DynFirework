"""DynFireworkMod v2.0 数据模型包."""
from __future__ import annotations

from .base import Element as _ElementV2, ElementCategory
from .composites import CompositeElement
from .effects import EffectElement
from .fireworks import FireworkElement
from .registry import (
	ElementTypeDef,
	ELEMENT_TYPE_REGISTRY,
	register_type,
	get_type_def,
	get_types_by_category,
	get_type_key,
)
from .trajectories import TrajectoryElement
from .values import (
	ColorRGB,
	Position,
	GradientColor,
	FireworkType as FireworkType,
	TrajectoryType,
	EffectType,
	CompositeType,
)

def _init_registry() -> None:
	if ELEMENT_TYPE_REGISTRY:
		return

	register_type(ElementTypeDef(
		type_key="single_layer", category=ElementCategory.FIREWORK,
		display_name="单层烟花", element_class=FireworkElement,
		form_class=None, export_func="single_layer_firework", icon="●",
	))
	register_type(ElementTypeDef(
		type_key="double_layer", category=ElementCategory.FIREWORK,
		display_name="双层烟花", element_class=FireworkElement,
		form_class=None, export_func="double_layer_firework", icon="◐",
	))
	register_type(ElementTypeDef(
		type_key="directional", category=ElementCategory.FIREWORK,
		display_name="定向烟花", element_class=FireworkElement,
		form_class=None, export_func="directional_firework", icon=">",
	))
	register_type(ElementTypeDef(
		type_key="clustered", category=ElementCategory.FIREWORK,
		display_name="集束烟花", element_class=FireworkElement,
		form_class=None, export_func="clustered_firework", icon="✦",
	))
	register_type(ElementTypeDef(
		type_key="expanding_sphere", category=ElementCategory.FIREWORK,
		display_name="膨胀球烟花", element_class=FireworkElement,
		form_class=None, export_func="expanding_sphere_firework", icon="◌",
	))
	register_type(ElementTypeDef(
		type_key="nebula", category=ElementCategory.FIREWORK,
		display_name="星云烟花", element_class=FireworkElement,
		form_class=None, export_func="nebula_firework", icon="☁",
	))

	register_type(ElementTypeDef(
		type_key="launch", category=ElementCategory.TRAJECTORY,
		display_name="基础发射", element_class=TrajectoryElement,
		form_class=None, export_func="launch_trajectory", icon="/",
	))
	register_type(ElementTypeDef(
		type_key="launch_spark", category=ElementCategory.TRAJECTORY,
		display_name="火花轨迹", element_class=TrajectoryElement,
		form_class=None, export_func="launch_spark_trajectory", icon="*",
	))
	register_type(ElementTypeDef(
		type_key="expanding", category=ElementCategory.TRAJECTORY,
		display_name="扩散轨迹", element_class=TrajectoryElement,
		form_class=None, export_func="expanding_trajectory", icon="□",
	))
	register_type(ElementTypeDef(
		type_key="spiral", category=ElementCategory.TRAJECTORY,
		display_name="螺旋轨迹", element_class=TrajectoryElement,
		form_class=None, export_func="spiral_trajectory", icon="∿",
	))

	register_type(ElementTypeDef(
		type_key="beam", category=ElementCategory.EFFECT,
		display_name="束状发射", element_class=EffectElement,
		form_class=None, export_func="beam_effect", icon="|",
	))
	register_type(ElementTypeDef(
		type_key="spray", category=ElementCategory.EFFECT,
		display_name="持续喷射", element_class=EffectElement,
		form_class=None, export_func="spray_effect", icon="≈",
	))
	register_type(ElementTypeDef(
		type_key="double_helix", category=ElementCategory.EFFECT,
		display_name="双螺旋", element_class=EffectElement,
		form_class=None, export_func="double_helix_effect", icon="♲",
	))
	register_type(ElementTypeDef(
		type_key="rotating_ring", category=ElementCategory.EFFECT,
		display_name="旋转环", element_class=EffectElement,
		form_class=None, export_func="rotating_ring_effect", icon="○",
	))

	register_type(ElementTypeDef(
		type_key="secondary_explosion", category=ElementCategory.COMPOSITE,
		display_name="二次爆炸", element_class=CompositeElement,
		form_class=None, export_func="secondary_explosion", icon="✳",
	))
	register_type(ElementTypeDef(
		type_key="combo_ec", category=ElementCategory.COMPOSITE,
		display_name="同步烟花", element_class=CompositeElement,
		form_class=None, export_func="combo_ec", icon="✿",
	))

_init_registry()

__all__ = [
	"ColorRGB", "Position", "GradientColor",
	"ElementCategory",
	"FireworkType", "TrajectoryType", "EffectType", "CompositeType",
	"FireworkElement", "TrajectoryElement", "EffectElement", "CompositeElement",
	"ElementTypeDef", "ELEMENT_TYPE_REGISTRY",
	"register_type", "get_type_def", "get_types_by_category", "get_type_key",
]
