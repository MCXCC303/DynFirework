from abc import ABC, abstractmethod

from PySide6.QtGui import QColor

from dyn.lib.units import MinecraftPosition, MinecraftVelocity, MinecraftTick


class AbstractTrajectory(ABC):
	@abstractmethod
	def build_positions(self, start: MinecraftPosition, end: MinecraftPosition):
		# 两个坐标点，必要参数
		pass

	@abstractmethod
	def build_launch_velocity(self) -> MinecraftVelocity:
		# 暂时没看出来有什么需要单独写一个函数的计算功能，直接在这里处理应该不会出问题
		# 在build_positions之后build
		# 好像也可以合并到build_positions中
		pass

	@abstractmethod
	def build_color(self, start_color: QColor, end_color: QColor | None = None):
		# 必要参数，从gui中获取
		pass

	@abstractmethod
	def build_particle_properties(self, particle_life_time: MinecraftTick, particle_mass: int):
		# 粒子的生命周期（particle_life_time）、粒子的质量（m_0）
		# 建议提供默认设置
		pass

	@abstractmethod
	def build_physical_properties(self, k: float = 1.2, g: float = 9.8, velocity_scale: float = 0.05):
		# 空气阻力系数（k)、重力加速度（g=9.8)、速度缩放系数（_velocity_scale=0.05)
		# 建议提供默认设置
		pass


class AbstractFirework(ABC):
	def __init__(self):
		super().__init__()
		self._g = None
		self._k = None
		self._particle_mass = None
		self._particle_life_time = None
		self._explode_speed_coefficient = None
		self._vertical_angle = None
		self._horizontal_angle = None
		self._color_end = None
		self._color_start = None
		self._position = None
		self._velocity_scale = None
		self._traj = None

	@abstractmethod
	def build_position(self, position: MinecraftPosition):
		# 必要参数
		pass

	@abstractmethod
	def build_colors(self, color_start: QColor, color_end: QColor | None = None):
		# 必要参数，根据层数决定数量
		# 其实应该可以直接在双层烟花里创建两个对象
		pass

	@abstractmethod
	def build_explode_angle(self, horizontal_angle: float, vertical_angle: float):
		# 可以从gui中获取，也可以默认设置
		# 建议提供默认设置
		pass

	@abstractmethod
	def build_explode_velocity(self, explode_speed_coefficient: float):
		# 把speed参数改为explode_speed_coefficient，在这里重新计算爆炸速度
		# 建议提供默认设置
		pass

	@abstractmethod
	def build_particle_properties(self, particle_life_time: MinecraftTick, m_0: int):
		pass

	@abstractmethod
	def build_physical_properties(self, k: float = 1.2, g: float = 9.8, velocity_scale: float = 0.05):
		pass

	@abstractmethod
	def build_trajectory_old(self, traj: AbstractTrajectory):
		# 可选，直接传入AbstractTrajectory继承类
		# 不知道有没有用，以后看用不用得到
		pass

	@property
	@abstractmethod
	def traj_rand_offset(self):
		"""
		目前共3种随机偏移：聚向/集束烟花单侧偏移、单层烟花单层偏移、双层烟花双层偏移
		扩散球面烟花不偏移
		"""
		pass

	@property
	@abstractmethod
	def dfp_command(self):
		"""
		将所有写入粒子命令转入重写
		"""
		pass

	@property
	@abstractmethod
	def label_color(self):
		"""
		在元素列表和时间线显示的颜色，可以支持：
		单色（轨迹、单层烟花、扩散环）
		双向（渐变轨迹、轨迹单层烟花）
		四向渐变（渐变轨迹单层渐变烟花、双层双渐变烟花）
		"""
		pass

	@abstractmethod
	def to_check_list(self):
		"""
		将完整信息输出为检查器信息，xml/json格式
		"""
		pass

	@abstractmethod
	def build_from_check_list(self):
		"""
		从检查器信息还原原属性（自定义元素）
		"""
		pass


class AbstractTrajFirework(AbstractFirework, AbstractTrajectory, ABC):
	# 理论上这个类可以覆盖所有的轨迹类效果，包括不含轨迹的烟花、不含烟花的轨迹、不含烟花轨迹的特殊效果等等等等
	# 特殊效果可以通过继承AbstractFirework类搭配AbstractTrajectory类实现
	# 但实际上我也不知道这个类具体可以用到哪些烟花
	@abstractmethod
	def build_trajectory(self, traj: AbstractTrajectory):
		pass

	@abstractmethod
	def build_firework(self, firework: AbstractFirework):
		pass
