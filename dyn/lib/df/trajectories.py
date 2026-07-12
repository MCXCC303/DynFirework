"""DynFireworkMod v2.0 轨迹计算 - 每个函数从 TrajectoryElementV2 提取参数，生成单条 /df 命令."""
from __future__ import annotations

import logging

from dyn.lib import global_storage

log = logging.getLogger(__name__)
from dyn.lib.df.commands import (
	cmd_launch, cmd_launch_spark, cmd_expanding_traj, cmd_spiral, cmd_shell,
)
from dyn.lib.units import seconds_to_tick

def launch_trajectory(elem) -> None:
	tick = seconds_to_tick(elem.start_time)
	sp = elem.start_position
	ep = elem.end_position
	log.debug(f"导出launch轨迹: tick={tick}, start=({sp.x:.1f},{sp.y:.1f},{sp.z:.1f}), end=({ep.x:.1f},{ep.y:.1f},{ep.z:.1f})")
	cmd = cmd_launch(
		x0=sp.x, y0=sp.y, z0=sp.z,
		x1=ep.x, y1=ep.y, z1=ep.z,
		r1=elem.traj_color.start.r, g1=elem.traj_color.start.g, b1=elem.traj_color.start.b,
		r2=elem.traj_color.end.r, g2=elem.traj_color.end.g, b2=elem.traj_color.end.b,
		k=elem.k, m0=elem.m0, rho=elem.rho,
		duration=elem.duration, lifetime=elem.lifetime,
	)
	global_storage.add_command(tick, cmd)
	if elem.add_shell:
		sc = elem.shell_color
		global_storage.add_command(tick, cmd_shell(ep.x, ep.y, ep.z, sc.r, sc.g, sc.b, elem.shell_size))
		log.debug(f"launch_trajectory add_shell=True: pos=({ep.x:.1f},{ep.y:.1f},{ep.z:.1f})")

def launch_spark_trajectory(elem) -> None:
	tick = seconds_to_tick(elem.start_time)
	sp = elem.start_position
	ep = elem.end_position
	log.debug(f"导出launch_spark轨迹: tick={tick}, start=({sp.x:.1f},{sp.y:.1f},{sp.z:.1f}), end=({ep.x:.1f},{ep.y:.1f},{ep.z:.1f})")
	cmd = cmd_launch_spark(
		x0=sp.x, y0=sp.y, z0=sp.z,
		x1=ep.x, y1=ep.y, z1=ep.z,
		r1=elem.traj_color.start.r, g1=elem.traj_color.start.g, b1=elem.traj_color.start.b,
		r2=elem.traj_color.end.r, g2=elem.traj_color.end.g, b2=elem.traj_color.end.b,
		k=elem.k, m0=elem.m0, particle_count=elem.particle_count,
		duration=elem.duration, lifetime=elem.lifetime,
	)
	global_storage.add_command(tick, cmd)

def expanding_trajectory(elem) -> None:
	tick = seconds_to_tick(elem.start_time)
	sp = elem.start_position
	ep = elem.end_position
	log.debug(f"导出expanding轨迹: tick={tick}, start=({sp.x:.1f},{sp.y:.1f},{sp.z:.1f}), end=({ep.x:.1f},{ep.y:.1f},{ep.z:.1f})")
	cmd = cmd_expanding_traj(
		x0=sp.x, y0=sp.y, z0=sp.z,
		x1=ep.x, y1=ep.y, z1=ep.z,
		r1=elem.traj_color.start.r, g1=elem.traj_color.start.g, b1=elem.traj_color.start.b,
		r2=elem.traj_color.end.r, g2=elem.traj_color.end.g, b2=elem.traj_color.end.b,
		k=elem.k, m0=elem.m0,
		range_x=elem.range_x, range_y=elem.range_y, range_z=elem.range_z,
		particle_count=elem.particle_count, speed_factor=elem.speed_factor,
		duration=elem.duration, lifetime=elem.lifetime,
	)
	global_storage.add_command(tick, cmd)

def spiral_trajectory(elem) -> None:
	tick = seconds_to_tick(elem.start_time)
	sp = elem.start_position
	ep = elem.end_position
	log.debug(f"导出spiral轨迹: tick={tick}, start=({sp.x:.1f},{sp.y:.1f},{sp.z:.1f}), end=({ep.x:.1f},{ep.y:.1f},{ep.z:.1f})")
	cmd = cmd_spiral(
		x0=sp.x, y0=sp.y, z0=sp.z,
		x1=ep.x, y1=ep.y, z1=ep.z,
		r1=elem.traj_color.start.r, g1=elem.traj_color.start.g, b1=elem.traj_color.start.b,
		r2=elem.traj_color.end.r, g2=elem.traj_color.end.g, b2=elem.traj_color.end.b,
		k=elem.k, m0=elem.m0,
		spiral_radius=elem.spiral_radius, spiral_speed=elem.spiral_speed,
		shrink_exponent=elem.shrink_exponent, particle_count=elem.particle_count,
		duration=elem.duration, lifetime=elem.lifetime,
	)
	global_storage.add_command(tick, cmd)
