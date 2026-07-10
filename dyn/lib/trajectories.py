# firework_trajectories.py
# pylint: skip-file
# flake8: noqa
import logging
import math
import random

import numpy as np
from scipy.interpolate import splprep, splev

from . import shared_functions
from .global_storage import g

log = logging.getLogger("dyn.lib.trajectories")

def simulate_trajectory(vx0, vy0, vz0, x0, y0, z0, duration, k, m0):
	t_step = 1.0 / 20  # 一秒20个tick
	t = 0
	x, y, z = x0, y0, z0
	vy = vy0  # Initialize vy to prevent UnboundLocalError

	while t <= duration:
		vx = vx0 * math.exp(-k * t / m0)
		vz = vz0 * math.exp(-k * t / m0)
		vy = (vy0 + m0 * g / k) * math.exp(-k * t / m0) - m0 * g / k

		x = x0 + (vx0 * m0 / k) * (1 - math.exp(-k * t / m0))
		z = z0 + (vz0 * m0 / k) * (1 - math.exp(-k * t / m0))
		y = y0 - (m0 * g * t / k) + (vy0 + (m0 * g / k)) * (m0 / k) * (1 - math.exp(-k * t / m0))

		t += t_step

	return x, y, z, vy

def calculate_initial_velocity_bisection(x0, y0, z0, x1, y1, z1, duration, k, m0):
	vx_low, vx_high = -200, 200
	vy_low, vy_high = 0, 200  # 发射初始速度不应为负
	vz_low, vz_high = -200, 200

	# 使用二分法寻找合适的初速度
	precision = 0.01  # 精度要求
	while vx_high - vx_low > precision or vy_high - vy_low > precision or vz_high - vz_low > precision:
		vx0 = (vx_low + vx_high) / 2
		vy0 = (vy_low + vy_high) / 2
		vz0 = (vz_low + vz_high) / 2

		x, y, z, vy = simulate_trajectory(vx0, vy0, vz0, x0, y0, z0, duration, k, m0)

		if x < x1:
			vx_low = vx0
		else:
			vx_high = vx0

		if y < y1:
			vy_low = vy0
		else:
			vy_high = vy0

		if z < z1:
			vz_low = vz0
		else:
			vz_high = vz0

	return (vx_low + vx_high) / 2, (vy_low + vy_high) / 2, (vz_low + vz_high) / 2

def launch_trajectory(end_tick, x0, y0, z0, x1, y1, z1, start_color, end_color, duration, k, m0, lifetime,
                      rho):  # rho表示一个tick内生成多少个粒子
	log.debug(f"发射轨迹: end_tick={end_tick}, from=({x0:.1f},{y0:.1f},{z0:.1f}) to=({x1:.1f},{y1:.1f},{z1:.1f}), duration={duration:.2f}s, rho={rho}")
	t_step = 1.0 / 20 / rho  # 一秒20个tick
	initial_tick = end_tick - int(duration * 20)  # 计算起始tick
	VELOCITY_SCALE = 0.05  # 速度缩放系数

	# 计算初始速度
	vx0, vy0, vz0 = calculate_initial_velocity_bisection(x0, y0, z0, x1, y1, z1, duration, k, m0)

	t = 0
	n_tick = initial_tick
	while t <= duration:
		# 计算水平方向的位移和速度
		vx = vx0 * math.exp(-k * t / m0)
		vz = vz0 * math.exp(-k * t / m0)
		x_ = x0 + (vx0 * m0 / k) * (1 - math.exp(-k * t / m0))
		z_ = z0 + (vz0 * m0 / k) * (1 - math.exp(-k * t / m0))

		# 计算垂直方向的位移和速度
		vy = (vy0 + m0 * g / k) * math.exp(-k * t / m0) - m0 * g / k
		y_ = y0 - (m0 * g * t / k) + (vy0 + (m0 * g / k)) * (m0 / k) * (1 - math.exp(-k * t / m0))

		# 计算颜色表达式
		color_expr = shared_functions.color_expression(start_color, end_color, lifetime)

		# 添加粒子指令（传递缩放后的速度）
		# 轨迹粒子lifetime延长2倍：lifetime * 20 * 2 = lifetime * 40
		shared_functions.add_firework_command(int(n_tick), round(x_, 4), round(y_, 4), round(z_, 4), lifetime * 40,
		                                      color_expr, vx * VELOCITY_SCALE, vy * VELOCITY_SCALE, vz * VELOCITY_SCALE)

		t += t_step
		n_tick += 1.0 / rho  # 增加n_tick

def launch_spark_trajectory(end_tick, x0, y0, z0, x1, y1, z1, duration, k, m0, lifetime, particle_count):
	log.debug(f"火花轨迹: end_tick={end_tick}, particles={particle_count}, duration={duration:.2f}s")
	t_step = 1.0 / 20  # 一秒20个tick
	initial_tick = end_tick - int(duration * 20)  # 计算起始tick

	# 计算初始速度
	vx0, vy0, vz0 = calculate_initial_velocity_bisection(x0, y0, z0, x1, y1, z1, duration, k, m0)

	t = 0
	n_tick = initial_tick  # 使用 n_tick 并重置为初始 tick
	while t <= duration:
		# 计算水平方向的位移
		vx = vx0 * math.exp(-k * t / m0)
		vz = vz0 * math.exp(-k * t / m0)
		x_ = x0 + (vx0 * m0 / k) * (1 - math.exp(-k * t / m0))
		z_ = z0 + (vz0 * m0 / k) * (1 - math.exp(-k * t / m0))

		# 计算垂直方向的位移
		vy = (vy0 + m0 * g / k) * math.exp(-k * t / m0) - m0 * g / k
		y_ = y0 - (m0 * g * t / k) + (vy0 + (m0 * g / k)) * (m0 / k) * (1 - math.exp(-k * t / m0))

		# 生成火星粒子效果
		for _ in range(particle_count):  # 每个tick生成particle_count个火星粒子
			# 基础向后速度（减半：0.05 -> 0.025）
			spark_vx = vx * -0.025
			spark_vy = vy * -0.025
			spark_vz = vz * -0.025

			# 随机偏移范围（水平方向+-1倍，垂直方向+-0.5倍）
			spark_vx += random.uniform(-abs(spark_vx) * 1.0, abs(spark_vx) * 1.0)
			spark_vy += random.uniform(-abs(spark_vy) * 0.5, abs(spark_vy) * 0.5)
			spark_vz += random.uniform(-abs(spark_vz) * 1.0, abs(spark_vz) * 1.0)

			# 确保vy不向上（火花不应该向上飞）
			spark_vy = min(spark_vy, 0)

			# lifetime为0.5秒（10 ticks）
			shared_functions.add_spark_command(n_tick, round(x_, 4), round(y_, 4), round(z_, 4), spark_vx, spark_vy,
			                                   spark_vz, 10)

		t += t_step
		n_tick += 1  # 增加n_tick

def simulate_base_trajectory(vx0, vy0, vz0, x0, y0, z0, duration, k, m0, points_per_tick):
	t_step = 1.0 / 20 / points_per_tick  # 一秒20个tick
	trajectory = []
	t = 0

	while t <= duration:
		vx = vx0 * math.exp(-k * t / m0)
		vz = vz0 * math.exp(-k * t / m0)
		vy = (vy0 + m0 * g / k) * math.exp(-k * t / m0) - m0 * g / k

		x = x0 + (vx0 * m0 / k) * (1 - math.exp(-k * t / m0))
		z = z0 + (vz0 * m0 / k) * (1 - math.exp(-k * t / m0))
		y = y0 - (m0 * g * t / k) + (vy0 + (m0 * g / k)) * (m0 / k) * (1 - math.exp(-k * t / m0))

		trajectory.append((x, y, z))
		t += t_step

	return trajectory

def generate_random_offset_trajectory(base_trajectory, interval_ticks):
	offset_trajectory = []
	num_base_points = len(base_trajectory)
	base_points = np.array(base_trajectory)
	offsets = np.zeros_like(base_points)

	for i in range(num_base_points):
		if i % interval_ticks == 0 or i == num_base_points - 1:
			offset = 2 * (1 - (i / num_base_points)) * 0.5  # 末端偏移量趋近0
			offsets[i] = [
				random.uniform(-offset, offset),  # 只在x和z方向上偏移
				0,  # 确保y坐标不变
				random.uniform(-offset, offset)
			]

	tck, u = splprep([base_points[:, 0] + offsets[:, 0],
	                  base_points[:, 1],
	                  base_points[:, 2] + offsets[:, 2]], s=1)
	u_fine = np.linspace(0, 1, num_base_points)
	interpolated_points = splev(u_fine, tck)

	for x, y, z in zip(*interpolated_points):
		offset_trajectory.append((x, y, z))

	return offset_trajectory

def trajectory_with_random_offset(end_tick, x0, y0, z0, x1, y1, z1, k, m0, duration, lifetime, interval_ticks,
                                  points_per_tick):
	vx0, vy0, vz0 = calculate_initial_velocity_bisection(x0, y0, z0, x1, y1, z1, duration, k, m0)

	base_trajectory = simulate_base_trajectory(vx0, vy0, vz0, x0, y0, z0, duration, k, m0, points_per_tick)
	spiral_trajectory = generate_random_offset_trajectory(base_trajectory, interval_ticks)

	num_points = len(spiral_trajectory)
	for i, (x, y, z) in enumerate(spiral_trajectory):
		n_tick = end_tick - int((num_points - i) / points_per_tick)
		# 轨迹粒子lifetime延长2倍
		shared_functions.add_spark_command(n_tick, x, y, z, 0, 0, 0, lifetime * 40)

def thick_trajectory_with_random_offset(end_tick, x0, y0, z0, x1, y1, z1, k, m0, duration, lifetime, interval_ticks,
                                        points_per_tick, range_x, range_y, range_z, particle_count):
	vx0, vy0, vz0 = calculate_initial_velocity_bisection(x0, y0, z0, x1, y1, z1, duration, k, m0)

	base_trajectory = simulate_base_trajectory(vx0, vy0, vz0, x0, y0, z0, duration, k, m0, points_per_tick)
	spiral_trajectory = generate_random_offset_trajectory(base_trajectory, interval_ticks)

	num_points = len(spiral_trajectory)
	for i, (x, y, z) in enumerate(spiral_trajectory):
		n_tick = end_tick - int((num_points - i) / points_per_tick)
		# 轨迹粒子lifetime延长2倍
		shared_functions.add_thick_spark_command(n_tick, x, y, z, 0, 0, 0, lifetime * 40, range_x, range_y, range_z,
		                                         particle_count)

def expanding_trajectory_with_random_offset(end_tick, x0, y0, z0, x1, y1, z1, k, m0, duration, lifetime, interval_ticks,
                                            points_per_tick, range_x, range_y, range_z, particle_count, speed_factor):
	# 计算基础轨迹的初始速度
	vx0, vy0, vz0 = calculate_initial_velocity_bisection(x0, y0, z0, x1, y1, z1, duration, k, m0)

	# 生成基础轨迹
	base_trajectory = simulate_base_trajectory(vx0, vy0, vz0, x0, y0, z0, duration, k, m0, points_per_tick)

	# 生成偏移轨迹
	spiral_trajectory = generate_random_offset_trajectory(base_trajectory, interval_ticks)

	num_points = len(base_trajectory)

	for i in range(num_points):
		initial_x, initial_y, initial_z = base_trajectory[i]
		target_x, target_y, target_z = spiral_trajectory[i]

		# 计算速度向量，直接使用坐标差乘以speed_factor，确保vy=0
		# 速度缩小为原来的1/5（*0.2）
		vx = (target_x - initial_x) * speed_factor * 0.2
		vy = 0  # 确保纵坐标不变
		vz = (target_z - initial_z) * speed_factor * 0.2

		# 计算 n_tick
		n_tick = end_tick - int((num_points - i - 1) / points_per_tick)

		# 添加指令
		# 轨迹粒子lifetime延长2倍
		shared_functions.add_thick_spark_command(n_tick, round(initial_x, 4), round(initial_y, 4), round(initial_z, 4),
		                                         vx, vy, vz, lifetime * 40, range_x, range_y, range_z, particle_count)
