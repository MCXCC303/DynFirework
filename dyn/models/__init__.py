"""DynFirework 数据模型.

models/df/          DynFireworkMod v2.0 数据模型 (df 元素类型 + 注册表)
models/cb/          ColorBlock 数据模型 (cb 用)
models/project.py   Project 项目容器 + Backend 枚举
"""
from __future__ import annotations

# ColorBlock 旧类型 (cb)
from .cb import (
	Element,
	ElementType,
	TrajectoryElement as CbTrajectoryElement,
	FireworkElement as CbFireworkElement,
	TrajFireworkElement as CbTrajFireworkElement,
	TrajType as CbTrajType,
	FireworkType as CbFireworkType,
	ColorRGB,
	GradientColor,
	Position,
)
# DynFirework 新模型 (df)
from .df import (
	ElementCategory,
	FireworkType,
	TrajectoryType,
	EffectType,
	CompositeType,
	FireworkElement,
	TrajectoryElement,
	EffectElement,
	CompositeElement,
	ElementTypeDef,
	ELEMENT_TYPE_REGISTRY,
	register_type,
	get_type_def,
	get_types_by_category,
	get_type_key,
)
# 后端枚举
from .project import Project, Backend

__all__ = [
	# Backend
	"Backend",
	# cb
	"Element", "ElementType",
	"CbTrajectoryElement", "CbFireworkElement", "CbTrajFireworkElement",
	"CbTrajType", "CbFireworkType",
	"ColorRGB", "GradientColor", "Position",
	# df
	"ElementCategory",
	"FireworkType", "TrajectoryType", "EffectType", "CompositeType",
	"FireworkElement", "TrajectoryElement", "EffectElement", "CompositeElement",
	"ElementTypeDef", "ELEMENT_TYPE_REGISTRY",
	"register_type", "get_type_def", "get_types_by_category", "get_type_key",
	# Project
	"Project",
]
