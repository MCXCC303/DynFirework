"""DynFirework 数据模型.

models/df/     DynFireworkMod v2.0 数据模型 (V2 元素类型 + 注册表)
models/particleex/      particleex 旧数据模型 (particleex 用)
models/project.py  Project 项目容器
"""
from __future__ import annotations

# V2 新模型
from .df import (
	ElementCategory,
	FireworkTypeV2,
	TrajectoryType,
	EffectType,
	CompositeType,
	FireworkElementV2,
	TrajectoryElementV2,
	EffectElement,
	CompositeElement,
	ElementTypeDef,
	ELEMENT_TYPE_REGISTRY,
	register_type,
	get_type_def,
	get_types_by_category,
	get_type_key,
)
# V1 旧类型 (particleex 兼容)
from .particleex import (
	Element,
	ElementType,
	TrajectoryElement,
	FireworkElement,
	TrajFireworkElement,
	TrajType,
	FireworkType,
	ColorRGB,
	GradientColor,
	Position,
)
from .project import Project

__all__ = [
	# V1
	"Element", "ElementType", "TrajectoryElement", "FireworkElement",
	"TrajFireworkElement", "TrajType", "FireworkType",
	"ColorRGB", "GradientColor", "Position",
	# V2
	"ElementCategory",
	"FireworkTypeV2", "TrajectoryType", "EffectType", "CompositeType",
	"FireworkElementV2", "TrajectoryElementV2", "EffectElement", "CompositeElement",
	"ElementTypeDef", "ELEMENT_TYPE_REGISTRY",
	"register_type", "get_type_def", "get_types_by_category", "get_type_key",
	# Project
	"Project",
]
