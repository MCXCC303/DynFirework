"""Colorblock Mod (/particleex) 命令生成, MC 1.12.2/1.16.5.
命令格式: /particleex rgbatickparameter minecraft:end_rod ...
"""
from __future__ import annotations

import logging

from dyn.lib import global_storage

log = logging.getLogger(__name__)

def color_expression(start_color, end_color, lifetime):
	log.debug(f"color_expression: lifetime={lifetime}")
	r1, g1, b1 = start_color
	r2, g2, b2 = end_color
	return (
		f"x=0;y=0;z=0;"
		f"cr=({r1}+({r2}-{r1})*(t/{lifetime}))/255.0;"
		f"cg=({g1}+({g2}-{g1})*(t/{lifetime}))/255.0;"
		f"cb=({b1}+({b2}-{b1})*(t/{lifetime}))/255.0"
	)

def add_firework_command(tick, x, y, z, lifetime, color_expr, vx=0, vy=0, vz=0):
	log.debug(f"add_firework_command: tick={tick}, pos=({x:.1f},{y:.1f},{z:.1f})")
	_command = (
		f"particleex rgbatickparameter minecraft:end_rod "
		f"{round(x, 4)} {round(y, 4)} {round(z, 4)} "
		f"0.0 0.0 0.0 0.0 1.0 "
		f'"{color_expr}" 0.1 1 {int(lifetime)}'
	)
	global_storage.add_command(tick, _command)

def add_spark_command(tick, x, y, z, vx, vy, vz, lifetime):
	log.debug(f"add_spark_command: tick={tick}, pos=({x:.1f},{y:.1f},{z:.1f}), lifetime={lifetime}")
	_command = (
		f"particleex normal minecraft:end_rod "
		f"{round(x, 4)} {round(y, 4)} {round(z, 4)} "
		f"1.0 1.0 1.0 1.0 "
		f"{round(vx, 4)} {round(vy, 4)} {round(vz, 4)} "
		f"0 0 0 1 {int(lifetime)}"
	)
	global_storage.add_command(tick, _command)

def add_thick_spark_command(tick, x, y, z, vx, vy, vz, lifetime, range_x, range_y, range_z, particle_count):
	log.debug(f"add_thick_spark_command: tick={tick}, pos=({x:.1f},{y:.1f},{z:.1f}), lifetime={lifetime}, particles={particle_count}")
	_command = (
		f"particleex normal minecraft:end_rod "
		f"{round(x, 4)} {round(y, 4)} {round(z, 4)} "
		f"1.0 1.0 1.0 1.0 "
		f"{round(vx, 4)} {round(vy, 4)} {round(vz, 4)} "
		f"{round(range_x, 4)} {round(range_y, 4)} {round(range_z, 4)} "
		f"{particle_count} {int(lifetime)}"
	)
	global_storage.add_command(tick, _command)

def add_velocity_firework_command(tick, x, y, z, start_color, end_color, vx, vy, vz, lifetime):
	log.debug(f"add_velocity_firework_command: tick={tick}, pos=({x:.1f},{y:.1f},{z:.1f}), lifetime={lifetime}")
	mid_r, mid_g, mid_b = lerp_color(start_color, end_color, 0.5)
	_command = (
		f"particleex normal minecraft:end_rod "
		f"{round(x, 4)} {round(y, 4)} {round(z, 4)} "
		f"{mid_r / 255.0:.4f} {mid_g / 255.0:.4f} {mid_b / 255.0:.4f} 1.0 "
		f"{round(vx, 4)} {round(vy, 4)} {round(vz, 4)} "
		f"0 0 0 1 {int(lifetime)}"
	)
	global_storage.add_command(tick, _command)

def lerp_color(color1, color2, factor):
	r = color1[0] + (color2[0] - color1[0]) * factor
	g = color1[1] + (color2[1] - color1[1]) * factor
	b = color1[2] + (color2[2] - color1[2]) * factor
	return (int(r), int(g), int(b))
