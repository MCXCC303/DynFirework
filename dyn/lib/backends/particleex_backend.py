# ParticleEx Backend   ParticleEx / Colorblock Mod, MC 1.12.2 / 1.16.5
# 命令格式:
#   /particleex rgbatickparameter minecraft:end_rod ... "color_expr" ...
#   /particleex normal minecraft:end_rod ...
from dyn.lib import global_storage

def color_expression(start_color, end_color, lifetime):
	"""生成Colorblock模组的rgbatickparameter颜色表达式.

	返回一个字符串表达式，模组在渲染时根据粒子生命周期插值颜色.
	"""
	r1, g1, b1 = start_color
	r2, g2, b2 = end_color
	return (
		f"x=0;y=0;z=0;"
		f"cr=({r1}+({r2}-{r1})*(t/{lifetime}))/255.0;"
		f"cg=({g1}+({g2}-{g1})*(t/{lifetime}))/255.0;"
		f"cb=({b1}+({b2}-{b1})*(t/{lifetime}))/255.0"
	)

def add_firework_command(tick, x, y, z, lifetime, color_expr, vx=0, vy=0, vz=0):
	"""生成带颜色渐变的粒子.

	ParticleEx rgbatickparameter模式下粒子位置固定（速度为0），
	颜色由color_expr字符串表达式驱动渐变.
	vx/vy/vz参数在此后端被忽略（Colorblock不支持粒子的速度渐变）.
	"""
	_command = (
		f"particleex rgbatickparameter minecraft:end_rod "
		f"{round(x, 4)} {round(y, 4)} {round(z, 4)} "
		f"0.0 0.0 0.0 0.0 1.0 "
		f'"{color_expr}" 0.1 1 {int(lifetime)}'
	)
	global_storage.add_command(tick, _command)

def add_spark_command(tick, x, y, z, vx, vy, vz, lifetime):
	"""生成火花粒子   使用白色粒子+速度运动."""
	_command = (
		f"particleex normal minecraft:end_rod "
		f"{round(x, 4)} {round(y, 4)} {round(z, 4)} "
		f"1.0 1.0 1.0 1.0 "
		f"{round(vx, 4)} {round(vy, 4)} {round(vz, 4)} "
		f"0 0 0 1 {int(lifetime)}"
	)
	global_storage.add_command(tick, _command)

def add_thick_spark_command(tick, x, y, z, vx, vy, vz, lifetime, range_x, range_y, range_z, particle_count):
	"""生成粗火花粒子   使用particleex normal的范围参数随机散布."""
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
	"""生成带初速度的烟花粒子.

	ParticleEx normal模式不支持颜色渐变表达式，因此取起点和终点颜色的
	中点值作为单一颜色，同时传递速度让模组物理引擎处理运动.
	"""
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
	"""Linear interpolate between two RGB colors."""
	r = color1[0] + (color2[0] - color1[0]) * factor
	g = color1[1] + (color2[1] - color1[1]) * factor
	b = color1[2] + (color2[2] - color1[2]) * factor
	return (int(r), int(g), int(b))
