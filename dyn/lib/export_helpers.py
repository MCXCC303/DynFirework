"""导出参数构建 + 元素类型到导出函数映射 供 CLI 和 ExportService 共用."""
from __future__ import annotations

from typing import Callable

from dyn.models.df.base import ElementCategory

def _build_fw_dispatch() -> dict[str, Callable]:
	from dyn.lib.df import fireworks as _fw
	return {
		"single_layer": _fw.single_layer_firework,
		"double_layer": _fw.double_layer_firework,
		"directional": _fw.directional_firework,
		"clustered": _fw.clustered_firework,
		"expanding_sphere": _fw.expanding_sphere_firework,
		"nebula": _fw.nebula_firework,
	}

def _build_traj_dispatch() -> dict[str, Callable]:
	from dyn.lib.df import trajectories as _traj
	return {
		"launch": _traj.launch_trajectory,
		"launch_spark": _traj.launch_spark_trajectory,
		"expanding": _traj.expanding_trajectory,
		"spiral": _traj.spiral_trajectory,
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
	from dyn.models.df.registry import get_type_key
	func = FW_FUNC_MAP.get(get_type_key(elem))
	if func:
		func(elem)

def export_trajectory(elem) -> None:
	_init_maps()
	from dyn.models.df.registry import get_type_key
	func = TRAJ_FUNC_MAP.get(get_type_key(elem))
	if func:
		func(elem)

def export_effect(elem) -> None:
	_init_maps()
	from dyn.models.df.registry import get_type_key
	func = EFFECT_FUNC_MAP.get(get_type_key(elem))
	if func:
		func(elem)

def export_composite(elem) -> None:
	_init_maps()
	from dyn.models.df.registry import get_type_key
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
	handler = EXPORT_DISPATCH.get(elem.category)
	if handler:
		handler(elem)

# CB 导出调度 按 cb ElementType 分发到 lib/cb/ 函数

def _export_cb_firework(elem) -> None:
	from dyn.lib.cb import fireworks as _fw
	from dyn.models.cb import TrajFireworkElement, FireworkType

	if isinstance(elem, TrajFireworkElement):
		pos = elem.mid_position
		tick = elem.fw_start_tick
		duration = elem.fw_duration_ticks / 20.0
	else:
		pos = elem.position
		tick = elem.start_tick
		duration = elem.duration_ticks / 20.0
	x, y, z = pos.x, pos.y, pos.z
	inner_start = elem.inner_color.start.as_tuple()
	inner_end = elem.inner_color.end.as_tuple()
	outer_start = elem.outer_color.start.as_tuple()
	outer_end = elem.outer_color.end.as_tuple()

	lifetime = 15
	fw_type = elem.fw_type

	if fw_type == FireworkType.SINGLE_LAYER.value:
		_fw.basic_single_layer_firework(
			tick, x, y, z, inner_start, inner_end, elem.speed,
			elem.horizontal_angle, elem.vertical_angle, duration, lifetime)
	elif fw_type == FireworkType.DOUBLE_LAYER.value:
		_fw.basic_double_layer_firework(
			tick, x, y, z, inner_start, inner_end, outer_start, outer_end,
			elem.inner_speed, elem.outer_speed,
			elem.horizontal_angle, elem.vertical_angle, duration, lifetime)
	elif fw_type == FireworkType.DIRECTIONAL.value:
		_fw.directional_firework(
			tick, x, y, z, inner_start, inner_end, elem.speed,
			elem.horizontal_angle, elem.vertical_angle,
			elem.spread_angle, elem.track_count, duration, lifetime)
	elif fw_type == FireworkType.CLUSTERED.value:
		_fw.clustered_firework(
			tick, x, y, z, inner_start, inner_end, elem.speed,
			elem.horizontal_angle, elem.vertical_angle,
			elem.track_count, elem.spread_angle, duration, lifetime)
	elif fw_type == FireworkType.EXPANDING_SPHERE.value:
		_fw.expanding_sphere_firework(
			tick, x, y, z, inner_start, inner_end,
			elem.radius, elem.track_count, elem.radial_speed, lifetime)

def _export_cb_trajectory(elem) -> None:
	from dyn.lib.cb import trajectories as _traj
	from dyn.models.cb import TrajFireworkElement, TrajType

	start = elem.start_position
	end = elem.end_position
	traj_color = elem.traj_color
	start_color = traj_color.start.as_tuple()
	end_color = traj_color.end.as_tuple()

	if isinstance(elem, TrajFireworkElement):
		end_tick = elem.traj_end_tick
		duration = elem.traj_duration_ticks / 20.0
	else:
		end_tick = elem.end_tick
		duration = elem.duration_ticks / 20.0

	lifetime = 15
	k = elem.k
	m0 = elem.m0
	traj_type = elem.traj_type

	# TrajFireworkElement 缺少部分 TrajectoryElement 专属属性，使用 getattr 兜底
	iv = getattr(elem, 'interval_ticks', 5)
	ppt = getattr(elem, 'points_per_tick', 1)
	rx = getattr(elem, 'range_x', 0.0)
	ry = getattr(elem, 'range_y', 0.0)
	rz = getattr(elem, 'range_z', 0.0)
	pc = getattr(elem, 'particle_count', 1)
	sf = getattr(elem, 'speed_factor', 1.0)

	if traj_type == TrajType.LAUNCH.value:
		_traj.launch_trajectory(
			end_tick, start.x, start.y, start.z, end.x, end.y, end.z,
			start_color, end_color, duration, k, m0, lifetime, elem.rho)
	elif traj_type == TrajType.SPARK.value:
		_traj.launch_spark_trajectory(
			end_tick, start.x, start.y, start.z, end.x, end.y, end.z,
			duration, k, m0, lifetime, pc)
	elif traj_type == TrajType.OFFSET.value:
		_traj.trajectory_with_random_offset(
			end_tick, start.x, start.y, start.z, end.x, end.y, end.z,
			k, m0, duration, lifetime, iv, ppt)
	elif traj_type == TrajType.THICK.value:
		_traj.thick_trajectory_with_random_offset(
			end_tick, start.x, start.y, start.z, end.x, end.y, end.z,
			k, m0, duration, lifetime, iv, ppt, rx, ry, rz, pc)
	elif traj_type == TrajType.EXPANDING.value:
		_traj.expanding_trajectory_with_random_offset(
			end_tick, start.x, start.y, start.z, end.x, end.y, end.z,
			k, m0, duration, lifetime, iv, ppt, rx, ry, rz, pc, sf)

def _export_cb_traj_firework(elem) -> None:
	_export_cb_trajectory(elem)
	_export_cb_firework(elem)

def _build_cb_export_dispatch() -> dict:
	from dyn.models.cb import ElementType
	return {
		ElementType.TRAJECTORY: _export_cb_trajectory,
		ElementType.FIREWORK: _export_cb_firework,
		ElementType.TRAJ_FIREWORK: _export_cb_traj_firework,
	}

CB_EXPORT_DISPATCH: dict = {}

def _init_cb_dispatch() -> None:
	if CB_EXPORT_DISPATCH:
		return
	CB_EXPORT_DISPATCH.update(_build_cb_export_dispatch())

def export_cb_element(elem) -> None:
	_init_cb_dispatch()
	handler = CB_EXPORT_DISPATCH.get(elem.element_type)
	if handler:
		handler(elem)
