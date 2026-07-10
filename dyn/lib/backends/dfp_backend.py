# pylint: disable=all
# flake8: noqa
# mypy: ignore-errors
# DFP Backend   DynFirework Particles Mod, MC 1.20.1
# 命令格式: /dfp x y z r1 g1 b1 r2 g2 b2 vx vy vz lifetime
import random

from dyn.lib import global_storage

def color_expression(start_color, end_color, lifetime):
	r1, g1, b1 = start_color
	r2, g2, b2 = end_color
	# 返回dust格式的颜色数组，RGB值除以255转换为0-1范围
	return [r1 / 255.0, g1 / 255.0, b1 / 255.0], [r2 / 255.0, g2 / 255.0, b2 / 255.0]

def add_firework_command(tick, x, y, z, lifetime, color_expr, vx=0, vy=0, vz=0):
	from_color, to_color = color_expr
	# 转换颜色从0-1浮点数到0-255整数
	r1, g1, b1 = int(from_color[0] * 255), int(from_color[1] * 255), int(from_color[2] * 255)
	r2, g2, b2 = int(to_color[0] * 255), int(to_color[1] * 255), int(to_color[2] * 255)

	# DynFirework Mod格式：/dfp x y z r1 g1 b1 r2 g2 b2 vx vy vz lifetime
	# 粒子静止显示（速度=0），使用传入的lifetime参数（单位：ticks）
	command = f'dfp {round(x, 4)} {round(y, 4)} {round(z, 4)} {r1} {g1} {b1} {r2} {g2} {b2} 0 0 0 {int(lifetime)}'
	global_storage.add_command(tick, command)

def add_spark_command(tick, x, y, z, vx, vy, vz, lifetime):
	# 火花粒子使用暖白色到金黄色的渐变
	r1, g1, b1 = 255, 255, 200
	r2, g2, b2 = 255, 200, 100

	# DynFirework Mod格式：/dfp x y z r1 g1 b1 r2 g2 b2 vx vy vz lifetime
	# 使用传入的速度参数（vx, vy, vz），支持静止（0,0,0）和运动粒子
	command = f'dfp {round(x, 4)} {round(y, 4)} {round(z, 4)} {r1} {g1} {b1} {r2} {g2} {b2} {round(vx, 4)} {round(vy, 4)} {round(vz, 4)} {int(lifetime)}'
	global_storage.add_command(tick, command)

def add_thick_spark_command(tick, x, y, z, vx, vy, vz, lifetime, range_x, range_y, range_z, particle_count):
	# 粗火花粒子，在指定范围内生成多个粒子

	# 火花粒子使用暖白色到金黄色的渐变
	r1, g1, b1 = 255, 255, 200
	r2, g2, b2 = 255, 200, 100

	# 循环生成指定数量的粒子
	for _ in range(particle_count):
		# 位置随机偏移
		x_offset = x + random.uniform(-range_x, range_x)
		y_offset = y + random.uniform(-range_y, range_y)
		z_offset = z + random.uniform(-range_z, range_z)

		# 速度随机扰动（±10%）
		vx_offset = vx + random.uniform(-abs(vx) * 0.1, abs(vx) * 0.1)
		vy_offset = vy + random.uniform(-abs(vy) * 0.1, abs(vy) * 0.1)
		vz_offset = vz + random.uniform(-abs(vz) * 0.1, abs(vz) * 0.1)

		# DynFirework Mod格式：/dfp x y z r1 g1 b1 r2 g2 b2 vx vy vz lifetime
		# 直接使用物理模拟计算的速度，不额外补偿重力
		command = f'dfp {round(x_offset, 4)} {round(y_offset, 4)} {round(z_offset, 4)} {r1} {g1} {b1} {r2} {g2} {b2} {round(vx_offset, 4)} {round(vy_offset, 4)} {round(vz_offset, 4)} {int(lifetime)}'
		global_storage.add_command(tick, command)

def add_velocity_firework_command(tick, x, y, z, start_color, end_color, vx, vy, vz, lifetime):
	"""
	生成带初速度的烟花粒子
	粒子将在Mod物理引擎中运动，受重力和空气阻力影响

	参数:
	    tick: 游戏刻
	    x, y, z: 粒子位置
	    start_color: 起始颜色元组 (R, G, B)
	    end_color: 结束颜色元组 (R, G, B)
	    vx, vy, vz: 粒子初速度
	    lifetime: 粒子生命周期（ticks）
	"""
	r1, g1, b1 = start_color
	r2, g2, b2 = end_color

	# DynFirework Mod格式：/dfp x y z r1 g1 b1 r2 g2 b2 vx vy vz lifetime
	# 使用真实速度，让Mod物理引擎处理运动
	command = f'dfp {round(x, 4)} {round(y, 4)} {round(z, 4)} {r1} {g1} {b1} {r2} {g2} {b2} {round(vx, 4)} {round(vy, 4)} {round(vz, 4)} {int(lifetime)}'
	global_storage.add_command(tick, command)

def lerp_color(color1, color2, factor):
	"""Linearly interpolate between two colors."""
	r = color1[0] + (color2[0] - color1[0]) * factor
	g = color1[1] + (color2[1] - color1[1]) * factor
	b = color1[2] + (color2[2] - color1[2]) * factor
	return (int(r), int(g), int(b))
