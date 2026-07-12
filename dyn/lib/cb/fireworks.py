# basic_fireworks.py
# pylint: skip-file
# flake8: noqa
import logging
import math
import random

from dyn.lib.cb import commands
from dyn.lib.global_storage import g

log = logging.getLogger("dyn.lib.cb.fireworks")

def basic_single_layer_firework(tick, x, y, z, start_color, end_color, speed, horizontal_angle_step,
                                vertical_angle_step, duration, lifetime):
	log.debug(f"单层烟花: tick={tick}, pos=({x:.1f},{y:.1f},{z:.1f}), speed={speed}, duration={duration:.2f}s")
	t_step = 1.0 / 20  # 一秒20个tick
	initial_tick = tick  # 存储起始tick
	VELOCITY_SCALE = 0.05  # 速度缩放系数

	horizontal_angles = int(360 / horizontal_angle_step)
	vertical_angles = int(180 / vertical_angle_step)

	for i in range(horizontal_angles):
		for j in range(vertical_angles):
			# 随机生成水平和垂直角度偏移
			horizontal_angle_offset = random.uniform(-horizontal_angle_step / 2, horizontal_angle_step / 2)
			vertical_angle_offset = random.uniform(-vertical_angle_step / 2, vertical_angle_step / 2)

			# 计算粒子的初始方向
			horizontal_angle = (i * horizontal_angle_step + horizontal_angle_offset) % 360
			vertical_angle = (j * vertical_angle_step + vertical_angle_offset) % 180 - 90
			rad_horizontal = math.radians(horizontal_angle)
			rad_vertical = math.radians(vertical_angle)
			speed_ = speed + random.uniform(-speed / 12, speed / 12)
			vx0 = speed_ * math.cos(rad_vertical) * math.cos(rad_horizontal)
			vy0 = speed_ * math.sin(rad_vertical)
			vz0 = speed_ * math.cos(rad_vertical) * math.sin(rad_horizontal)

			t = 0
			n_tick = initial_tick  # 使用 n_tick 并重置为初始 tick
			while t <= duration:
				# 计算水平方向的位移
				k = 1.2  # 空气阻力系数
				m0 = 0.5  # 粒子质量（减小以增强空气阻力效果）
				vx = vx0 * math.exp(-k * t / m0)
				vz = vz0 * math.exp(-k * t / m0)
				x_ = x + (vx0 * m0 / k) * (1 - math.exp(-k * t / m0))
				z_ = z + (vz0 * m0 / k) * (1 - math.exp(-k * t / m0))

				# 计算垂直方向的位移和速度
				vy = (vy0 + (m0 * g / k)) * math.exp(-k * t / m0) - m0 * g / k
				y_ = y - (m0 * g * t / k) + (vy0 + (m0 * g / k)) * (m0 / k) * (1 - math.exp(-k * t / m0))

				# 计算颜色表达式
				color_expr = commands.color_expression(start_color, end_color, lifetime)

				# 添加粒子指令（传递缩放后的速度）
				# lifetime参数被忽略，使用固定值15 ticks
				commands.add_firework_command(n_tick, round(x_, 4), round(y_, 4), round(z_, 4), 15,
				                              color_expr, vx * VELOCITY_SCALE, vy * VELOCITY_SCALE, vz * VELOCITY_SCALE)

				t += t_step
				n_tick += 1  # 增加n_tick
	total_particles = horizontal_angles * vertical_angles
	log.debug(f"basic_single_layer_firework: 生成粒子总数={total_particles}, duration={duration:.2f}s")

def calculate_inner_angle_steps(outer_horizontal_angle_step, outer_vertical_angle_step, inner_speed, outer_speed):
	if inner_speed == 0:
		log.warning("calculate_inner_angle_steps: inner_speed为0，返回默认角度步长")
		return outer_horizontal_angle_step, outer_vertical_angle_step
	# 内外层的半径比例
	radius_ratio = outer_speed / inner_speed

	# 根据半径比例调整内层的角度步长，使内层粒子的密度接近外层的密度
	inner_horizontal_angle_step = outer_horizontal_angle_step * radius_ratio
	inner_vertical_angle_step = outer_vertical_angle_step * radius_ratio

	return inner_horizontal_angle_step, inner_vertical_angle_step

def basic_double_layer_firework(tick, x, y, z, inner_start_color, inner_end_color, outer_start_color, outer_end_color,
                                inner_speed, outer_speed, outer_horizontal_angle_step, outer_vertical_angle_step,
                                duration, lifetime):
	log.debug(f"双层烟花: tick={tick}, pos=({x:.1f},{y:.1f},{z:.1f}), inner_speed={inner_speed}, outer_speed={outer_speed}")
	# 计算内层的角度步长
	inner_horizontal_angle_step, inner_vertical_angle_step = calculate_inner_angle_steps(outer_horizontal_angle_step,
	                                                                                     outer_vertical_angle_step,
	                                                                                     inner_speed, outer_speed)

	# 生成内层烟花
	basic_single_layer_firework(tick, x, y, z, inner_start_color, inner_end_color, inner_speed,
	                            inner_horizontal_angle_step, inner_vertical_angle_step, duration, lifetime)
	# 生成外层烟花
	basic_single_layer_firework(tick, x, y, z, outer_start_color, outer_end_color, outer_speed,
	                            outer_horizontal_angle_step, outer_vertical_angle_step, duration, lifetime)

def directional_firework(tick, x, y, z, start_color, end_color, speed,
                         direction_horizontal_angle, direction_vertical_angle, spread_angle, track_count,
                         duration, lifetime):
	log.debug(f"定向烟花: tick={tick}, tracks={track_count}, spread={spread_angle}")
	t_step = 1.0 / 20  # 一秒20个tick
	initial_tick = tick  # 存储起始tick
	VELOCITY_SCALE = 0.05  # 速度缩放系数

	for i in range(track_count):
		# 在spread_angle范围内添加随机偏移
		random_horizontal_angle = random.uniform(-spread_angle / 2, spread_angle / 2)
		random_vertical_angle = random.uniform(-spread_angle / 2, spread_angle / 2)

		total_horizontal_angle = direction_horizontal_angle + random_horizontal_angle
		total_vertical_angle = direction_vertical_angle + random_vertical_angle

		# 转换为弧度
		rad_horizontal = math.radians(total_horizontal_angle)
		rad_vertical = math.radians(total_vertical_angle)

		# 初始速度向量
		vx0 = speed * math.cos(rad_vertical) * math.cos(rad_horizontal)
		vy0 = speed * math.sin(rad_vertical)
		vz0 = speed * math.cos(rad_vertical) * math.sin(rad_horizontal)

		# print(f"vx0={vx0}, vy0={vy0}, vz0={vz0}")

		t = 0
		n_tick = initial_tick  # 使用 n_tick 并重置为初始 tick
		while t <= duration:
			# 计算水平方向的位移
			k = 1.2  # 空气阻力系数
			m0 = 1.0  # 粒子质量（减小以增强空气阻力效果）
			vx = vx0 * math.exp(-k * t / m0)
			vz = vz0 * math.exp(-k * t / m0)
			x_ = x + (vx0 * m0 / k) * (1 - math.exp(-k * t / m0))
			z_ = z + (vz0 * m0 / k) * (1 - math.exp(-k * t / m0))

			# 计算垂直方向的位移和速度
			g = 9.8  # 重力加速度
			vy = (vy0 + (m0 * g / k)) * math.exp(-k * t / m0) - m0 * g / k
			y_ = y - (m0 * g * t / k) + (vy0 + (m0 * g / k)) * (m0 / k) * (1 - math.exp(-k * t / m0))

			# 计算颜色表达式
			color_expr = commands.color_expression(start_color, end_color, lifetime)

			# 添加粒子指令（传递缩放后的速度）
			# lifetime参数被忽略，使用固定值15 ticks
			commands.add_firework_command(n_tick, round(x_, 4), round(y_, 4), round(z_, 4), 15,
			                              color_expr, vx * VELOCITY_SCALE, vy * VELOCITY_SCALE, vz * VELOCITY_SCALE)

			t += t_step
			n_tick += 1  # 增加n_tick

def clustered_firework(tick, x, y, z, start_color, end_color, speed, horizontal_angle_step, vertical_angle_step,
                       track_count, spread_angle, duration, lifetime):
	log.debug(f"clustered_firework: tick={tick}, pos=({x:.1f},{y:.1f},{z:.1f}), h_angles={int(360 / horizontal_angle_step)}, v_angles={int(180 / vertical_angle_step)}, tracks={track_count}")
	horizontal_angles = int(360 / horizontal_angle_step)
	vertical_angles = int(180 / vertical_angle_step)
	for i in range(horizontal_angles):
		for j in range(vertical_angles):
			# 随机生成水平和垂直角度偏移
			horizontal_angle_offset = random.uniform(-horizontal_angle_step / 4, horizontal_angle_step / 4)
			vertical_angle_offset = random.uniform(-vertical_angle_step / 4, vertical_angle_step / 4)
			horizontal_angle = (i * horizontal_angle_step + horizontal_angle_offset) % 360
			vertical_angle = (j * vertical_angle_step + vertical_angle_offset) % 180 - 90
			# print(f"{horizontal_angle}, {vertical_angle}")
			directional_firework(tick, x, y, z, start_color, end_color, speed,
			                     horizontal_angle, vertical_angle, spread_angle, track_count, duration, lifetime)

def expanding_sphere_firework(tick, x, y, z, start_color, end_color,
                              radius, particle_count, radial_speed,
                              lifetime):
	"""
	生成扩散球面烟花效果
	使用斐波那契球面算法（Golden Spiral）生成均匀分布的粒子
	每个粒子沿位矢方向扩散，在单个tick生成一波带速度的粒子

	参数:
		tick: 起始游戏刻
		x, y, z: 球心坐标
		start_color: 起始颜色元组 (R, G, B)
		end_color: 结束颜色元组 (R, G, B)
		radius: 初始球面半径
		particle_count: 球面上的粒子数量
		radial_speed: 沿位矢方向的扩散速度
		lifetime: 粒子生命周期（ticks）
	"""
	log.debug(f"expanding_sphere_firework: tick={tick}, pos=({x:.1f},{y:.1f},{z:.1f}), radius={radius}, particles={particle_count}, radial_speed={radial_speed}")
	# 黄金角（Golden Angle）约等于 2.39996 弧度
	golden_angle = math.pi * (3.0 - math.sqrt(5.0))

	# 使用斐波那契球面算法生成均匀分布的点，并直接生成粒子
	for i in range(particle_count):
		# 计算 y 坐标（从 -1 到 1）
		y_normalized = 1.0 - (i / float(particle_count - 1)) * 2.0

		# 计算该高度处的圆半径
		radius_at_y = math.sqrt(1.0 - y_normalized * y_normalized)

		# 计算旋转角度
		theta = i * golden_angle

		# 计算 x, z 坐标
		x_normalized = math.cos(theta) * radius_at_y
		z_normalized = math.sin(theta) * radius_at_y

		# 缩放到实际半径并偏移到球心位置
		point_x = x + x_normalized * radius
		point_y = y + y_normalized * radius
		point_z = z + z_normalized * radius

		# 计算归一化的位矢方向（扩散方向）
		direction_x = x_normalized
		direction_y = y_normalized
		direction_z = z_normalized

		# 初始速度 = 扩散速度 * 归一化方向
		vx = radial_speed * direction_x
		vy = radial_speed * direction_y
		vz = radial_speed * direction_z

		# 直接在initial tick生成带速度的粒子
		commands.add_velocity_firework_command(
			tick, point_x, point_y, point_z,
			start_color, end_color,
			vx, vy, vz,
			lifetime
		)
