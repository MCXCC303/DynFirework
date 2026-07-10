"""烟花与轨迹元素的数据模型."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from uuid import uuid4

class ElementType(Enum):
	TRAJECTORY = auto()
	FIREWORK = auto()
	TRAJ_FIREWORK = auto()

class TrajType(Enum):
	LAUNCH = "launch"
	SPARK = "spark"
	OFFSET = "offset"
	THICK = "thick"
	EXPANDING = "expanding"

class FireworkType(Enum):
	SINGLE_LAYER = "single_layer"
	DOUBLE_LAYER = "double_layer"
	DIRECTIONAL = "directional"
	CLUSTERED = "clustered"
	EXPANDING_SPHERE = "expanding_sphere"

@dataclass
class ColorRGB:
	"""RGB 颜色值对象."""
	r: int = 255
	g: int = 165
	b: int = 0

	def as_tuple(self) -> tuple[int, int, int]:
		return (self.r, self.g, self.b)

	def to_json(self) -> dict:
		return {"r": self.r, "g": self.g, "b": self.b}

	@classmethod
	def from_json(cls, data: dict) -> ColorRGB:
		return cls(r=data["r"], g=data["g"], b=data["b"])

@dataclass
class Position:
	"""3D 坐标值对象."""
	x: float = 0.0
	y: float = 64.0
	z: float = 0.0

	def as_tuple(self) -> tuple[float, float, float]:
		return (self.x, self.y, self.z)

	def to_json(self) -> dict:
		return {"x": self.x, "y": self.y, "z": self.z}

	@classmethod
	def from_json(cls, data: dict) -> Position:
		return cls(x=data["x"], y=data["y"], z=data["z"])

@dataclass
class GradientColor:
	"""带渐变的颜色对."""
	start: ColorRGB = field(default_factory=ColorRGB)
	end: ColorRGB = field(default_factory=lambda: ColorRGB(r=255, g=100, b=0))
	use_gradient: bool = False

	def to_json(self) -> dict:
		return {
			"start": self.start.to_json(),
			"end": self.end.to_json(),
			"use_gradient": self.use_gradient,
		}

	@classmethod
	def from_json(cls, data: dict) -> GradientColor:
		return cls(
			start=ColorRGB.from_json(data["start"]),
			end=ColorRGB.from_json(data["end"]),
			use_gradient=data.get("use_gradient", False),
		)

@dataclass
class Element:
	"""时间线元素基类."""
	id: str = field(default_factory=lambda: str(uuid4()))
	name: str = "New Element"
	start_tick: int = 0
	duration_ticks: int = 20
	enabled: bool = True
	notes: str = ""

	@property
	def end_tick(self) -> int:
		return self.start_tick + self.duration_ticks

	@property
	def element_type(self) -> ElementType:
		raise NotImplementedError

	def to_json(self) -> dict:
		return {
			"id": self.id,
			"name": self.name,
			"start_tick": self.start_tick,
			"duration_ticks": self.duration_ticks,
			"enabled": self.enabled,
			"notes": self.notes,
		}

	@classmethod
	def _from_json_base(cls, data: dict) -> dict:
		return {
			"id": data.get("id", str(uuid4())),
			"name": data.get("name", "New Element"),
			"start_tick": data.get("start_tick", 0),
			"duration_ticks": data.get("duration_ticks", 20),
			"enabled": data.get("enabled", True),
			"notes": data.get("notes", ""),
		}

@dataclass
class TrajectoryElement(Element):
	"""轨迹元素   对应 firework_trajectories.py 中的函数参数."""

	# 位置
	start_position: Position = field(default_factory=Position)
	end_position: Position = field(default_factory=lambda: Position(x=10, y=64, z=10))

	# 颜色
	traj_color: GradientColor = field(default_factory=GradientColor)

	# 类型
	traj_type: str = "launch"

	# 物理参数
	k: float = 1.2
	m0: float = 0.5
	rho: int = 1
	particle_count: int = 1
	interval_ticks: int = 5
	points_per_tick: int = 1
	range_x: float = 0.0
	range_y: float = 0.0
	range_z: float = 0.0
	speed_factor: float = 1.0

	@property
	def element_type(self) -> ElementType:
		return ElementType.TRAJECTORY

	@property
	def start_color_tuple(self) -> tuple[int, int, int]:
		return self.traj_color.start.as_tuple()

	@property
	def end_color_tuple(self) -> tuple[int, int, int] | None:
		if self.traj_color.use_gradient:
			return self.traj_color.end.as_tuple()
		return None

	def to_json(self) -> dict:
		base = super().to_json()
		sp = self.start_position or Position()
		ep = self.end_position or Position()
		base.update({
			"type": self.traj_type,
			"start_position": sp.to_json(),
			"end_position": ep.to_json(),
			"traj_color": self.traj_color.to_json(),
			"params": {
				"k": self.k, "m0": self.m0, "rho": self.rho,
				"particle_count": self.particle_count,
				"interval_ticks": self.interval_ticks,
				"points_per_tick": self.points_per_tick,
				"range_x": self.range_x, "range_y": self.range_y,
				"range_z": self.range_z, "speed_factor": self.speed_factor,
			},
		})
		return base

	@classmethod
	def from_json(cls, data: dict) -> TrajectoryElement:
		base = cls._from_json_base(data)
		params = data.get("params", {})
		return cls(
			**base,
			start_position=Position.from_json(data.get("start_position", {})),
			end_position=Position.from_json(data.get("end_position", {})),
			traj_color=GradientColor.from_json(data.get("traj_color", {})),
			traj_type=data.get("type", "launch"),
			k=params.get("k", 1.2), m0=params.get("m0", 0.5),
			rho=params.get("rho", 1),
			particle_count=params.get("particle_count", 1),
			interval_ticks=params.get("interval_ticks", 5),
			points_per_tick=params.get("points_per_tick", 1),
			range_x=params.get("range_x", 0.0),
			range_y=params.get("range_y", 0.0),
			range_z=params.get("range_z", 0.0),
			speed_factor=params.get("speed_factor", 1.0),
		)

@dataclass
class FireworkElement(Element):
	"""烟花元素   对应 basic_fireworks.py 中的函数参数."""

	# 类型
	fw_type: str = "single_layer"

	# 位置 (爆炸中心)
	position: Position = field(default_factory=lambda: Position(x=10, y=80, z=10))

	# 颜色
	inner_color: GradientColor = field(
		default_factory=lambda: GradientColor(
			start=ColorRGB(r=0, g=0, b=255),
			end=ColorRGB(r=100, g=100, b=255),
		)
	)
	outer_color: GradientColor = field(
		default_factory=lambda: GradientColor(
			start=ColorRGB(r=255, g=0, b=0),
			end=ColorRGB(r=255, g=100, b=100),
		)
	)

	# 角度
	horizontal_angle: float = 30.0
	vertical_angle: float = 30.0

	# 物理参数
	speed: float = 10.0
	inner_speed: float = 8.0
	outer_speed: float = 10.0
	spread_angle: float = 15.0
	track_count: int = 1
	radius: float = 5.0
	radial_speed: float = 3.0

	@property
	def element_type(self) -> ElementType:
		return ElementType.FIREWORK

	@property
	def inner_start_color_tuple(self) -> tuple[int, int, int]:
		return self.inner_color.start.as_tuple()

	@property
	def outer_start_color_tuple(self) -> tuple[int, int, int]:
		return self.outer_color.start.as_tuple()

	def to_json(self) -> dict:
		base = super().to_json()
		base.update({
			"type": self.fw_type,
			"position": (self.position or Position()).to_json(),
			"inner_color": self.inner_color.to_json(),
			"outer_color": self.outer_color.to_json(),
			"angles": {
				"horizontal": self.horizontal_angle,
				"vertical": self.vertical_angle,
			},
			"params": {
				"speed": self.speed, "inner_speed": self.inner_speed,
				"outer_speed": self.outer_speed,
				"spread_angle": self.spread_angle,
				"track_count": self.track_count,
				"radius": self.radius, "radial_speed": self.radial_speed,
			},
		})
		return base

	@classmethod
	def from_json(cls, data: dict) -> FireworkElement:
		base = cls._from_json_base(data)
		params = data.get("params", {})
		angles = data.get("angles", {})
		return cls(
			**base,
			fw_type=data.get("type", "single_layer"),
			position=Position.from_json(data.get("position", {})),
			inner_color=GradientColor.from_json(data.get("inner_color", {})),
			outer_color=GradientColor.from_json(data.get("outer_color", {})),
			horizontal_angle=angles.get("horizontal", 30.0),
			vertical_angle=angles.get("vertical", 30.0),
			speed=params.get("speed", 10.0),
			inner_speed=params.get("inner_speed", 8.0),
			outer_speed=params.get("outer_speed", 10.0),
			spread_angle=params.get("spread_angle", 15.0),
			track_count=params.get("track_count", 1),
			radius=params.get("radius", 5.0),
			radial_speed=params.get("radial_speed", 3.0),
		)

@dataclass
class TrajFireworkElement(Element):
	"""轨迹烟花组合   轨迹末端自动对齐烟花爆炸中心."""

	# 位置（共享：轨迹终点 = 烟花爆炸中心）
	start_position: Position = field(default_factory=Position)
	mid_position: Position = field(default_factory=lambda: Position(x=10, y=80, z=10))

	# 轨迹部分
	traj_type: str = "launch"
	traj_color: GradientColor = field(default_factory=GradientColor)
	traj_duration_ticks: int = 20

	# 烟花部分
	fw_type: str = "single_layer"
	inner_color: GradientColor = field(
		default_factory=lambda: GradientColor(start=ColorRGB(r=0, g=0, b=255), end=ColorRGB(r=100, g=100, b=255))
	)
	outer_color: GradientColor = field(
		default_factory=lambda: GradientColor(start=ColorRGB(r=255, g=0, b=0), end=ColorRGB(r=255, g=100, b=100))
	)
	fw_duration_ticks: int = 20

	# 烟花参数
	horizontal_angle: float = 30.0
	vertical_angle: float = 30.0
	speed: float = 10.0
	inner_speed: float = 8.0
	outer_speed: float = 10.0
	spread_angle: float = 15.0
	track_count: int = 1
	k: float = 1.2
	m0: float = 0.5
	rho: int = 1

	@property
	def element_type(self) -> ElementType:
		return ElementType.TRAJ_FIREWORK

	@property
	def traj_start_tick(self) -> int:
		return self.start_tick

	@property
	def traj_end_tick(self) -> int:
		return self.start_tick + self.traj_duration_ticks

	@property
	def fw_start_tick(self) -> int:
		return self.traj_end_tick

	@property
	def end_tick(self) -> int:
		return self.fw_start_tick + self.fw_duration_ticks

	@property
	def duration_ticks(self) -> int:
		return self.traj_duration_ticks + self.fw_duration_ticks

	@duration_ticks.setter
	def duration_ticks(self, v: int) -> None:
		pass  # 派生值，不可直接设

	@property
	def end_position(self) -> Position:
		return self.mid_position if self.mid_position else Position()

	@end_position.setter
	def end_position(self, v: Position) -> None:
		self.mid_position = v

	def to_json(self) -> dict:
		base = super().to_json()
		base.update({
			"start_position": self.start_position.to_json(),
			"mid_position": self.mid_position.to_json(),
			"traj_type": self.traj_type,
			"traj_color": self.traj_color.to_json(),
			"traj_duration_ticks": self.traj_duration_ticks,
			"fw_type": self.fw_type,
			"inner_color": self.inner_color.to_json(),
			"outer_color": self.outer_color.to_json(),
			"fw_duration_ticks": self.fw_duration_ticks,
			"angles": {"horizontal": self.horizontal_angle, "vertical": self.vertical_angle},
			"params": {
				"speed": self.speed, "inner_speed": self.inner_speed,
				"outer_speed": self.outer_speed, "spread_angle": self.spread_angle,
				"track_count": self.track_count, "k": self.k, "m0": self.m0, "rho": self.rho,
			},
		})
		return base

	@classmethod
	def from_json(cls, data: dict) -> TrajFireworkElement:
		base = cls._from_json_base(data)
		params = data.get("params", {})
		angles = data.get("angles", {})
		return cls(
			**base,
			start_position=Position.from_json(data.get("start_position", {})),
			mid_position=Position.from_json(data.get("mid_position", {})),
			traj_type=data.get("traj_type", "launch"),
			traj_color=GradientColor.from_json(data.get("traj_color", {})),
			traj_duration_ticks=data.get("traj_duration_ticks", 20),
			fw_type=data.get("fw_type", "single_layer"),
			inner_color=GradientColor.from_json(data.get("inner_color", {})),
			outer_color=GradientColor.from_json(data.get("outer_color", {})),
			fw_duration_ticks=data.get("fw_duration_ticks", 20),
			horizontal_angle=angles.get("horizontal", 30.0),
			vertical_angle=angles.get("vertical", 30.0),
			speed=params.get("speed", 10.0),
			inner_speed=params.get("inner_speed", 8.0),
			outer_speed=params.get("outer_speed", 10.0),
			spread_angle=params.get("spread_angle", 15.0),
			track_count=params.get("track_count", 1),
			k=params.get("k", 1.2), m0=params.get("m0", 0.5), rho=params.get("rho", 1),
		)
