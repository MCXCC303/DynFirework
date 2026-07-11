"""导出参数构建 + 元素类型到导出函数映射 供 CLI 和 ExportService 共用."""
from __future__ import annotations

from typing import Callable

from dyn.models.df.base import ElementCategory
from dyn.models.df.composites import CompositeElement
from dyn.models.df.effects import EffectElement
from dyn.models.df.fireworks import FireworkElement as FireworkElementV2
from dyn.models.df.registry import get_type_key
from dyn.models.df.trajectories import TrajectoryElement as TrajectoryElementV2
from dyn.models.df.values import (
	ColorRGB as V2ColorRGB, Position as V2Position, GradientColor as V2GradientColor,
	FireworkType, TrajectoryType, CompositeType,
)

# 类型键 -> df 模组 V2 导出函数映射

def _build_fw_dispatch() -> dict[str, Callable]:
	from dyn.lib.df import fireworks as _fw
	return {
		"single_layer": _fw.single_layer_firework,
		"double_layer": _fw.double_layer_firework,
		"directional": _fw.directional_firework_v2,
		"clustered": _fw.clustered_firework_v2,
		"expanding_sphere": _fw.expanding_sphere_firework_v2,
		"nebula": _fw.nebula_firework,
	}

def _build_traj_dispatch() -> dict[str, Callable]:
	from dyn.lib.df import trajectories as _traj
	return {
		"launch": _traj.launch_trajectory_v2,
		"launch_spark": _traj.launch_spark_trajectory_v2,
		"expanding": _traj.expanding_trajectory_v2,
		"spiral": _traj.spiral_trajectory_v2,
	}

def _build_effect_dispatch() -> dict[str, Callable]:
	from dyn.lib.df import effects as _eff
	return {
		"beam": _eff.beam_effect,
		"spray": _eff.spray_effect,
		"double_helix": _eff.double_helix_effect,
		"rotating_ring": _eff.rotating_ring_effect,
	}

def _build_composite_dispatch() -> dict[str, Callable]:
	from dyn.lib.df import composites as _comp
	return {
		"secondary_explosion": _comp.secondary_explosion,
		"combo_ec": _comp.combo_ec,
	}

FW_FUNC_MAP: dict[str, Callable] = {}
TRAJ_FUNC_MAP: dict[str, Callable] = {}
EFFECT_FUNC_MAP: dict[str, Callable] = {}
COMPOSITE_FUNC_MAP: dict[str, Callable] = {}

def _init_maps() -> None:
	if FW_FUNC_MAP:
		return
	FW_FUNC_MAP.update(_build_fw_dispatch())
	TRAJ_FUNC_MAP.update(_build_traj_dispatch())
	EFFECT_FUNC_MAP.update(_build_effect_dispatch())
	COMPOSITE_FUNC_MAP.update(_build_composite_dispatch())

def export_firework(elem) -> None:
	_init_maps()
	func = FW_FUNC_MAP.get(get_type_key(elem))
	if func:
		func(elem)

def export_trajectory(elem) -> None:
	_init_maps()
	func = TRAJ_FUNC_MAP.get(get_type_key(elem))
	if func:
		func(elem)

def export_effect(elem) -> None:
	_init_maps()
	func = EFFECT_FUNC_MAP.get(get_type_key(elem))
	if func:
		func(elem)

def export_composite(elem) -> None:
	_init_maps()
	func = COMPOSITE_FUNC_MAP.get(get_type_key(elem))
	if func:
		func(elem)

EXPORT_DISPATCH: dict[ElementCategory, Callable] = {
	ElementCategory.FIREWORK: export_firework,
	ElementCategory.TRAJECTORY: export_trajectory,
	ElementCategory.EFFECT: export_effect,
	ElementCategory.COMPOSITE: export_composite,
}

def export_element(elem) -> None:
	v2 = _ensure_v2(elem)
	handler = EXPORT_DISPATCH.get(v2.category)
	if handler:
		handler(v2)

def _ensure_v2(elem):
	from dyn.models.particleex import (
		TrajectoryElement as OldTraj,
		FireworkElement as OldFw,
		TrajFireworkElement as OldTF,
	)
	if isinstance(elem, (FireworkElementV2, TrajectoryElementV2, EffectElement, CompositeElement)):
		return elem

	if isinstance(elem, OldTF):
		return _convert_old_tf(elem)
	if isinstance(elem, OldTraj):
		return _convert_old_traj(elem)
	if isinstance(elem, OldFw):
		return _convert_old_fw(elem)

	return _convert_old_fw(elem) if hasattr(elem, 'fw_type') else elem

def _old_to_v2_pos(pos) -> V2Position:
	return V2Position(x=pos.x, y=pos.y, z=pos.z)

def _old_to_v2_gradient(gc) -> V2GradientColor:
	return V2GradientColor(
		start=V2ColorRGB(r=gc.start.r, g=gc.start.g, b=gc.start.b),
		end=V2ColorRGB(r=gc.end.r, g=gc.end.g, b=gc.end.b),
		use_gradient=gc.use_gradient,
	)

def _map_old_traj_type(t: str) -> TrajectoryType:
	mapping = {"launch": "launch", "spark": "launch_spark", "expanding": "expanding",
	           "offset": "launch", "thick": "launch"}
	return TrajectoryType(mapping.get(t, "launch"))

def _convert_old_traj(elem) -> TrajectoryElementV2:
	traj_type = _map_old_traj_type(elem.traj_type)
	return TrajectoryElementV2(
		id=elem.id, name=elem.name,
		start_time=elem.start_tick / 20.0,
		duration=elem.duration_ticks / 20.0,
		enabled=elem.enabled, notes=elem.notes,
		traj_type=traj_type,
		start_position=_old_to_v2_pos(elem.start_position),
		end_position=_old_to_v2_pos(elem.end_position),
		traj_color=_old_to_v2_gradient(elem.traj_color),
		k=elem.k, m0=elem.m0, rho=elem.rho,
		lifetime=getattr(elem, 'lifetime', 3.0),
		particle_count=elem.particle_count,
		range_x=getattr(elem, 'range_x', 0.0),
		range_y=getattr(elem, 'range_y', 0.0),
		range_z=getattr(elem, 'range_z', 0.0),
		speed_factor=getattr(elem, 'speed_factor', 1.0),
	)

def _convert_old_fw(elem) -> FireworkElementV2:
	fw_type = FireworkType(elem.fw_type if isinstance(elem.fw_type, str) else elem.fw_type.value)
	return FireworkElementV2(
		id=elem.id, name=elem.name,
		start_time=elem.start_tick / 20.0,
		duration=elem.duration_ticks / 20.0,
		enabled=elem.enabled, notes=elem.notes,
		fw_type=fw_type,
		position=_old_to_v2_pos(elem.position),
		inner_color=_old_to_v2_gradient(elem.inner_color),
		outer_color=_old_to_v2_gradient(elem.outer_color),
		speed=elem.speed, inner_speed=elem.inner_speed, outer_speed=elem.outer_speed,
		particle_count=getattr(elem, 'particle_count', 100),
		horizontal_angle=elem.horizontal_angle, vertical_angle=elem.vertical_angle,
		spread_angle=elem.spread_angle, track_count=elem.track_count,
		radius=elem.radius, radial_speed=elem.radial_speed,
	)

def _convert_old_tf(elem) -> CompositeElement:
	return CompositeElement(
		id=elem.id, name=elem.name,
		start_time=elem.start_tick / 20.0,
		duration=elem.duration_ticks / 20.0 if hasattr(elem, 'duration_ticks') else (
				                                                                            elem.traj_duration_ticks + elem.fw_duration_ticks) / 20.0,
		enabled=elem.enabled, notes=elem.notes,
		composite_type=CompositeType.SECONDARY_EXPLOSION,
		position=_old_to_v2_pos(elem.mid_position if elem.mid_position else elem.end_position),
		se_start_position=_old_to_v2_pos(elem.start_position),
		se_mid_position=_old_to_v2_pos(elem.mid_position if elem.mid_position else elem.end_position),
		se_primary_type=FireworkType(elem.fw_type if isinstance(elem.fw_type, str) else "single_layer"),
		se_primary_color=_old_to_v2_gradient(elem.inner_color),
		se_primary_speed=elem.speed,
		se_primary_count=getattr(elem, 'track_count', 100),
		se_primary_duration=elem.fw_duration_ticks / 20.0,
		se_primary_lifetime=elem.fw_duration_ticks / 20.0,
	)
