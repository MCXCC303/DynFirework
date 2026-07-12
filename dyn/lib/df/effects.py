"""DynFireworkMod v2.0 特殊效果计算 - beam/spray/doublehelix/rotatingring.
每个函数从 EffectElement 提取参数，调用 commands 生成 /df 命令，写入 global_storage.
"""
from __future__ import annotations

import logging

from dyn.lib import global_storage
from dyn.lib.df.commands import cmd_beam, cmd_spray, cmd_double_helix, cmd_rotating_ring
from dyn.lib.units import seconds_to_tick

log = logging.getLogger("dyn.lib.df.effects")

def beam_effect(elem) -> None:
	"""束状发射 - /df beam."""
	tick = seconds_to_tick(elem.start_time)
	pos = elem.position
	cmd = cmd_beam(
		x=pos.x, y=pos.y, z=pos.z,
		sr1=elem.beam_start_color.start.r, sg1=elem.beam_start_color.start.g, sb1=elem.beam_start_color.start.b,
		sr2=elem.beam_start_color.end.r, sg2=elem.beam_start_color.end.g, sb2=elem.beam_start_color.end.b,
		er1=elem.beam_end_color.start.r, eg1=elem.beam_end_color.start.g, eb1=elem.beam_end_color.start.b,
		er2=elem.beam_end_color.end.r, eg2=elem.beam_end_color.end.g, eb2=elem.beam_end_color.end.b,
		min_speed=elem.beam_min_speed, max_speed=elem.beam_max_speed,
		h_angle=elem.beam_h_angle, v_angle=elem.beam_v_angle,
		spread_angle=elem.beam_spread_angle,
		count=elem.beam_count, particles_per=elem.beam_particles_per,
		lifetime=elem.beam_lifetime,
	)
	global_storage.add_command(tick, cmd)
	log.debug(f"beam_effect: elem={elem.id}({elem.name}), tick={tick}, pos=({pos.x:.1f},{pos.y:.1f},{pos.z:.1f}), count={elem.beam_count}, spread={elem.beam_spread_angle}")

def spray_effect(elem) -> None:
	"""持续喷射 - /df spray."""
	tick = seconds_to_tick(elem.start_time)
	pos = elem.position
	cmd = cmd_spray(
		x=pos.x, y=pos.y, z=pos.z,
		sr1=elem.spray_start_color.start.r, sg1=elem.spray_start_color.start.g, sb1=elem.spray_start_color.start.b,
		sr2=elem.spray_start_color.end.r, sg2=elem.spray_start_color.end.g, sb2=elem.spray_start_color.end.b,
		er1=elem.spray_end_color.start.r, eg1=elem.spray_end_color.start.g, eb1=elem.spray_end_color.start.b,
		er2=elem.spray_end_color.end.r, eg2=elem.spray_end_color.end.g, eb2=elem.spray_end_color.end.b,
		min_speed=elem.spray_min_speed, max_speed=elem.spray_max_speed,
		h_angle=elem.spray_h_angle, v_angle=elem.spray_v_angle,
		cone_angle=elem.spray_cone_angle,
		duration_ticks=elem.spray_duration_ticks,
		particles_per_tick=elem.spray_particles_per_tick,
		particle_lifetime_ticks=elem.spray_particle_lifetime_ticks,
	)
	global_storage.add_command(tick, cmd)
	log.debug(f"spray_effect: elem={elem.id}({elem.name}), tick={tick}, duration_ticks={elem.spray_duration_ticks}, particles_per_tick={elem.spray_particles_per_tick}")

def double_helix_effect(elem) -> None:
	"""双螺旋 - /df doublehelix."""
	tick = seconds_to_tick(elem.start_time)
	cmd = cmd_double_helix(
		cx=elem.position.x, cz=elem.position.z, base_y=elem.position.y,
		radius=elem.dh_radius, rise_speed=elem.dh_rise_speed, rotation_speed=elem.dh_rotation_speed,
		density=elem.dh_density, min_vy=elem.dh_min_vy, max_vy=elem.dh_max_vy,
		duration_ticks=elem.dh_duration_ticks, lifetime=elem.dh_lifetime,
		c1r1=elem.dh_color1.start.r, c1g1=elem.dh_color1.start.g, c1b1=elem.dh_color1.start.b,
		c1r2=elem.dh_color1.end.r, c1g2=elem.dh_color1.end.g, c1b2=elem.dh_color1.end.b,
		c2r1=elem.dh_color2.start.r, c2g1=elem.dh_color2.start.g, c2b1=elem.dh_color2.start.b,
		c2r2=elem.dh_color2.end.r, c2g2=elem.dh_color2.end.g, c2b2=elem.dh_color2.end.b,
	)
	global_storage.add_command(tick, cmd)
	log.debug(f"double_helix_effect: elem={elem.id}({elem.name}), tick={tick}, radius={elem.dh_radius}, rotation_speed={elem.dh_rotation_speed}")

def rotating_ring_effect(elem) -> None:
	"""旋转环 - /df rotatingring."""
	tick = seconds_to_tick(elem.start_time)
	pos = elem.position
	cmd = cmd_rotating_ring(
		cx=pos.x, cy=pos.y, cz=pos.z,
		ring_radius=elem.rr_ring_radius, tube_radius=elem.rr_tube_radius,
		rotation_speed=elem.rr_rotation_speed, density=elem.rr_density,
		radial_velocity=elem.rr_radial_velocity,
		duration_ticks=elem.rr_duration_ticks, lifetime=elem.rr_lifetime,
		r1=elem.rr_color.start.r, g1=elem.rr_color.start.g, b1=elem.rr_color.start.b,
		r2=elem.rr_color.end.r, g2=elem.rr_color.end.g, b2=elem.rr_color.end.b,
	)
	global_storage.add_command(tick, cmd)
	log.debug(f"rotating_ring_effect: elem={elem.id}({elem.name}), tick={tick}, ring_radius={elem.rr_ring_radius}, rotation_speed={elem.rr_rotation_speed}")
