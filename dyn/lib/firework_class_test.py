from PyQt5.QtGui import QColor

from dyn.lib.base_class import AbstractFirework, AbstractTrajectory
from dyn.lib.units import MinecraftPosition, MinecraftTick


class BasicSingleLayerFirework(AbstractFirework):
	def build_position(self, position: MinecraftPosition):
		self._position = position
		return self

	def build_colors(self, color_start: QColor, color_end: QColor | None = None):
		self._color_start = color_start
		self._color_end = color_end
		return self

	def build_explode_angle(self, horizontal_angle: float, vertical_angle: float):
		self._horizontal_angle = horizontal_angle
		self._vertical_angle = vertical_angle
		return self

	def build_explode_velocity(self, explode_speed_coefficient: float):
		self._explode_speed_coefficient = explode_speed_coefficient
		return self

	def build_particle_properties(self, particle_life_time: MinecraftTick, particle_mass: int):
		self._particle_life_time = particle_life_time
		self._particle_mass = particle_mass
		return self

	def build_physical_properties(self, k: float = 1.2, g: float = 9.8, velocity_scale: float = 0.05):
		self._k = k
		self._g = g
		self._velocity_scale = velocity_scale
		return self

	def build_trajectory_old(self, traj: AbstractTrajectory):
		self._traj = traj
		return self

	@property
	def traj_rand_offset(self):
		return

	@property
	def dfp_command(self):
		return

	@property
	def label_color(self):
		return

	def to_check_list(self):
		pass

	def build_from_check_list(self):
		pass

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
