"""导出参数构建共享工具 供 CLI 和 ExportService 共用."""
from __future__ import annotations

from typing import Any

TRAJ_FUNC_MAP = {
	"launch": "launch_trajectory",
	"spark": "launch_spark_trajectory",
	"offset": "trajectory_with_random_offset",
	"thick": "thick_trajectory_with_random_offset",
	"expanding": "expanding_trajectory_with_random_offset",
}

FW_FUNC_MAP = {
	"single_layer": "basic_single_layer_firework",
	"double_layer": "basic_double_layer_firework",
	"directional": "directional_firework",
	"clustered": "clustered_firework",
	"expanding_sphere": "expanding_sphere_firework",
}


def build_traj_kwargs(elem: Any, x0: float, y0: float, z0: float,
                      x1: float, y1: float, z1: float, duration_ticks: int) -> dict[str, Any]:
	"""构建轨迹导出参数 按 traj_type 填充类型专属参数."""
	color = elem.traj_color
	kwargs: dict[str, Any] = {
		"x0": x0, "y0": y0, "z0": z0,
		"x1": x1, "y1": y1, "z1": z1,
		"start_color": color.start.as_tuple(),
		"end_color": color.end.as_tuple() if color.use_gradient else color.start.as_tuple(),
		"duration": duration_ticks / 20,
		"k": elem.k, "m0": elem.m0,
		"lifetime": duration_ticks / 20,
	}
	if elem.traj_type == "launch":
		kwargs["rho"] = elem.rho
	elif elem.traj_type in ("spark",):
		kwargs["particle_count"] = elem.particle_count
	elif elem.traj_type in ("offset", "thick", "expanding"):
		kwargs["interval_ticks"] = elem.interval_ticks
		kwargs["points_per_tick"] = elem.points_per_tick
		if elem.traj_type in ("thick", "expanding"):
			kwargs["range_x"] = elem.range_x
			kwargs["range_y"] = elem.range_y
			kwargs["range_z"] = elem.range_z
			kwargs["particle_count"] = elem.particle_count
		if elem.traj_type == "expanding":
			kwargs["speed_factor"] = elem.speed_factor
	return kwargs


def fill_fw_kwargs(elem: Any, kwargs: dict[str, Any]) -> None:
	"""填充烟花导出参数 按 fw_type 设置颜色/角度/速度等."""
	inner_end = elem.inner_color.end.as_tuple() if elem.inner_color.use_gradient else elem.inner_color.start.as_tuple()
	outer_end = elem.outer_color.end.as_tuple() if elem.outer_color.use_gradient else elem.outer_color.start.as_tuple()

	if elem.fw_type == "single_layer":
		kwargs["start_color"] = elem.inner_color.start.as_tuple()
		kwargs["end_color"] = inner_end
		kwargs["speed"] = elem.speed
		kwargs["horizontal_angle_step"] = elem.horizontal_angle
		kwargs["vertical_angle_step"] = elem.vertical_angle
	elif elem.fw_type == "double_layer":
		kwargs["inner_start_color"] = elem.inner_color.start.as_tuple()
		kwargs["inner_end_color"] = inner_end
		kwargs["outer_start_color"] = elem.outer_color.start.as_tuple()
		kwargs["outer_end_color"] = outer_end
		kwargs["inner_speed"] = elem.inner_speed
		kwargs["outer_speed"] = elem.outer_speed
		kwargs["outer_horizontal_angle_step"] = elem.horizontal_angle
		kwargs["outer_vertical_angle_step"] = elem.vertical_angle
	elif elem.fw_type == "directional":
		kwargs["start_color"] = elem.inner_color.start.as_tuple()
		kwargs["end_color"] = inner_end
		kwargs["speed"] = elem.speed
		kwargs["spread_angle"] = elem.spread_angle
		kwargs["track_count"] = elem.track_count
		kwargs["direction_horizontal_angle"] = elem.horizontal_angle
		kwargs["direction_vertical_angle"] = elem.vertical_angle
	elif elem.fw_type == "clustered":
		kwargs["start_color"] = elem.inner_color.start.as_tuple()
		kwargs["end_color"] = inner_end
		kwargs["speed"] = elem.speed
		kwargs["spread_angle"] = elem.spread_angle
		kwargs["track_count"] = elem.track_count
		kwargs["horizontal_angle_step"] = elem.horizontal_angle
		kwargs["vertical_angle_step"] = elem.vertical_angle
	elif elem.fw_type == "expanding_sphere":
		kwargs["start_color"] = elem.inner_color.start.as_tuple()
		kwargs["end_color"] = inner_end
		kwargs["radius"] = elem.radius
		kwargs["particle_count"] = elem.track_count
		kwargs["radial_speed"] = elem.radial_speed
