"""DynFireworkMod v2.0 轨迹计算 - 每个函数从 TrajectoryElementV2 提取参数，生成单条 /df 命令."""
from __future__ import annotations

from dyn.lib import global_storage
from dyn.lib.df.commands import (
	cmd_launch, cmd_launch_spark, cmd_expanding_traj, cmd_spiral, cmd_shell,
)
from dyn.lib.units import seconds_to_tick

def launch_trajectory_v2(elem) -> None:
	tick = seconds_to_tick(elem.start_time)
	sp = elem.start_position
	ep = elem.end_position
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

def launch_spark_trajectory_v2(elem) -> None:
	tick = seconds_to_tick(elem.start_time)
	sp = elem.start_position
	ep = elem.end_position
	cmd = cmd_launch_spark(
		x0=sp.x, y0=sp.y, z0=sp.z,
		x1=ep.x, y1=ep.y, z1=ep.z,
		r1=elem.traj_color.start.r, g1=elem.traj_color.start.g, b1=elem.traj_color.start.b,
		r2=elem.traj_color.end.r, g2=elem.traj_color.end.g, b2=elem.traj_color.end.b,
		k=elem.k, m0=elem.m0, particle_count=elem.particle_count,
		duration=elem.duration, lifetime=elem.lifetime,
	)
	global_storage.add_command(tick, cmd)

def expanding_trajectory_v2(elem) -> None:
	tick = seconds_to_tick(elem.start_time)
	sp = elem.start_position
	ep = elem.end_position
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

def spiral_trajectory_v2(elem) -> None:
	tick = seconds_to_tick(elem.start_time)
	sp = elem.start_position
	ep = elem.end_position
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
