"""particleex 后端调度器.
所有命令生成函数通过此模块路由到 particleex 后端。
"""
import logging

from . import commands as _backend

log = logging.getLogger("dyn.lib.shared_functions")

def color_expression(start_color, end_color, lifetime):
	return _backend.color_expression(start_color, end_color, lifetime)

def add_firework_command(tick, x, y, z, lifetime, color_expr, vx=0, vy=0, vz=0):
	return _backend.add_firework_command(tick, x, y, z, lifetime, color_expr, vx, vy, vz)

def add_spark_command(tick, x, y, z, vx, vy, vz, lifetime):
	return _backend.add_spark_command(tick, x, y, z, vx, vy, vz, lifetime)

def add_thick_spark_command(tick, x, y, z, vx, vy, vz, lifetime, range_x, range_y, range_z, particle_count):
	return _backend.add_thick_spark_command(tick, x, y, z, vx, vy, vz, lifetime,
	                                        range_x, range_y, range_z, particle_count)

def add_velocity_firework_command(tick, x, y, z, start_color, end_color, vx, vy, vz, lifetime):
	return _backend.add_velocity_firework_command(tick, x, y, z, start_color, end_color, vx, vy, vz, lifetime)

def lerp_color(color1, color2, factor):
	return _backend.lerp_color(color1, color2, factor)
