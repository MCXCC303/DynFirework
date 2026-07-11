"""轨迹烟花组合."""
from __future__ import annotations

from dataclasses import dataclass, field

from .base import Element, ElementType
from .values import ColorRGB, GradientColor, Position

@dataclass
class TrajFireworkElement(Element):
	start_position: Position = field(default_factory=Position)
	mid_position: Position = field(default_factory=lambda: Position(x=10, y=80, z=10))

	traj_type: str = "launch"
	traj_color: GradientColor = field(default_factory=GradientColor)
	traj_duration_ticks: int = 20

	fw_type: str = "single_layer"
	inner_color: GradientColor = field(
		default_factory=lambda: GradientColor(start=ColorRGB(r=0, g=0, b=255), end=ColorRGB(r=100, g=100, b=255))
	)
	outer_color: GradientColor = field(
		default_factory=lambda: GradientColor(start=ColorRGB(r=255, g=0, b=0), end=ColorRGB(r=255, g=100, b=100))
	)
	fw_duration_ticks: int = 20

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
		pass

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
