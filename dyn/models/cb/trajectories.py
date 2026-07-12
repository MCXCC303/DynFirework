from __future__ import annotations

from dataclasses import dataclass, field

from dyn.logging_config import get_logger
from .base import Element, ElementType

log = get_logger(__name__)
from .values import GradientColor, Position

@dataclass
class TrajectoryElement(Element):
	start_position: Position = field(default_factory=Position)
	end_position: Position = field(default_factory=lambda: Position(x=10, y=64, z=10))

	traj_color: GradientColor = field(default_factory=GradientColor)

	traj_type: str = "launch"

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
		log.debug(f"反序列化 TrajectoryElement: name={base.get('name')}")
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
