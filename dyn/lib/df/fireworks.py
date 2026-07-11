"""DynFireworkMod v2.0 烟花计算 - 每个函数从 FireworkElementV2 提取参数，生成单条 /df 命令."""
from __future__ import annotations

from dyn.lib import global_storage
from dyn.lib.df.commands import (
	cmd_single_layer, cmd_double_layer, cmd_directional,
	cmd_clustered, cmd_expanding, cmd_nebula,
)
from dyn.lib.units import seconds_to_tick

def single_layer_firework(elem) -> None:
	tick = seconds_to_tick(elem.start_time)
	pos = elem.position
	cmd = cmd_single_layer(
		x=pos.x, y=pos.y, z=pos.z,
		r1=elem.inner_color.start.r, g1=elem.inner_color.start.g, b1=elem.inner_color.start.b,
		r2=elem.inner_color.end.r, g2=elem.inner_color.end.g, b2=elem.inner_color.end.b,
		speed=elem.speed, particle_count=elem.particle_count,
		duration=elem.duration, lifetime=elem.duration, flicker=elem.enable_tail_flicker,
	)
	global_storage.add_command(tick, cmd)

def double_layer_firework(elem) -> None:
	tick = seconds_to_tick(elem.start_time)
	pos = elem.position
	cmd = cmd_double_layer(
		x=pos.x, y=pos.y, z=pos.z,
		ir1=elem.inner_color.start.r, ig1=elem.inner_color.start.g, ib1=elem.inner_color.start.b,
		ir2=elem.inner_color.end.r, ig2=elem.inner_color.end.g, ib2=elem.inner_color.end.b,
		or1=elem.outer_color.start.r, og1=elem.outer_color.start.g, ob1=elem.outer_color.start.b,
		or2=elem.outer_color.end.r, og2=elem.outer_color.end.g, ob2=elem.outer_color.end.b,
		inner_speed=elem.inner_speed, outer_speed=elem.outer_speed,
		inner_count=elem.inner_count, outer_count=elem.outer_count,
		h_angle=elem.horizontal_angle, v_angle=elem.vertical_angle,
		duration=elem.duration, lifetime=elem.duration, flicker=elem.enable_tail_flicker,
	)
	global_storage.add_command(tick, cmd)

def directional_firework(elem) -> None:
	tick = seconds_to_tick(elem.start_time)
	pos = elem.position
	cmd = cmd_directional(
		x=pos.x, y=pos.y, z=pos.z,
		r1=elem.inner_color.start.r, g1=elem.inner_color.start.g, b1=elem.inner_color.start.b,
		r2=elem.inner_color.end.r, g2=elem.inner_color.end.g, b2=elem.inner_color.end.b,
		speed=elem.speed, h_angle=elem.horizontal_angle, v_angle=elem.vertical_angle,
		spread_angle=elem.spread_angle, track_count=elem.track_count,
		duration=elem.duration, lifetime=elem.duration, flicker=elem.enable_tail_flicker,
	)
	global_storage.add_command(tick, cmd)

def clustered_firework(elem) -> None:
	tick = seconds_to_tick(elem.start_time)
	pos = elem.position
	cmd = cmd_clustered(
		x=pos.x, y=pos.y, z=pos.z,
		r1=elem.inner_color.start.r, g1=elem.inner_color.start.g, b1=elem.inner_color.start.b,
		r2=elem.inner_color.end.r, g2=elem.inner_color.end.g, b2=elem.inner_color.end.b,
		speed=elem.speed, h_angle=elem.horizontal_angle, v_angle=elem.vertical_angle,
		direction_count=elem.direction_count, spread_angle=elem.spread_angle,
		track_count=elem.track_count,
		duration=elem.duration, lifetime=elem.duration, flicker=elem.enable_tail_flicker,
	)
	global_storage.add_command(tick, cmd)

def expanding_sphere_firework(elem) -> None:
	tick = seconds_to_tick(elem.start_time)
	pos = elem.position
	cmd = cmd_expanding(
		x=pos.x, y=pos.y, z=pos.z,
		r1=elem.inner_color.start.r, g1=elem.inner_color.start.g, b1=elem.inner_color.start.b,
		r2=elem.inner_color.end.r, g2=elem.inner_color.end.g, b2=elem.inner_color.end.b,
		radius=elem.radius, radial_speed=elem.radial_speed,
		particle_count=elem.track_count, lifetime=elem.duration,
		flicker=elem.enable_tail_flicker,
	)
	global_storage.add_command(tick, cmd)

def nebula_firework(elem) -> None:
	tick = seconds_to_tick(elem.start_time)
	pos = elem.position
	cmd = cmd_nebula(
		x=pos.x, y=pos.y, z=pos.z,
		r1=elem.inner_color.start.r, g1=elem.inner_color.start.g, b1=elem.inner_color.start.b,
		r2=elem.inner_color.end.r, g2=elem.inner_color.end.g, b2=elem.inner_color.end.b,
		particle_count=elem.particle_count, expansion_speed=elem.expansion_speed,
		density_falloff=elem.density_falloff, duration=elem.duration,
		flicker=elem.enable_tail_flicker,
	)
	global_storage.add_command(tick, cmd)
