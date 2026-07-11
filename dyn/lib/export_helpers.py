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
