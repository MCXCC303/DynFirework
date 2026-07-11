"""TrajectoryElement - 轨迹类."""
from __future__ import annotations

from dataclasses import dataclass, field

from .base import Element, ElementCategory
from .values import ColorRGB, GradientColor, Position, TrajectoryType

@dataclass
class TrajectoryElement(Element):
	traj_type: TrajectoryType = TrajectoryType.LAUNCH
	start_position: Position = field(default_factory=Position)
	end_position: Position = field(default_factory=lambda: Position(x=10, y=64, z=10))
	traj_color: GradientColor = field(default_factory=GradientColor)

	k: float = 1.2
	m0: float = 0.5
	rho: float = 1.0
	lifetime: float = 3.0
	particle_count: int = 1

	range_x: float = 0.0
	range_y: float = 0.0
	range_z: float = 0.0
	speed_factor: float = 1.0

	spiral_radius: float = 2.0
	spiral_speed: float = 3.0
	shrink_exponent: float = 1.0

	add_shell: bool = False
	shell_color: ColorRGB = field(default_factory=ColorRGB)
	shell_size: float = 1.0

	@property
	def category(self) -> ElementCategory:
		return ElementCategory.TRAJECTORY

	def to_json(self) -> dict:
		base = super().to_json()
		base.update({
			"type": self.traj_type.value,
			"start_position": self.start_position.to_json(),
			"end_position": self.end_position.to_json(),
			"traj_color": self.traj_color.to_json(),
			"k": self.k,
			"m0": self.m0,
			"rho": self.rho,
			"lifetime": self.lifetime,
			"particle_count": self.particle_count,
			"range_x": self.range_x,
			"range_y": self.range_y,
			"range_z": self.range_z,
			"speed_factor": self.speed_factor,
			"spiral_radius": self.spiral_radius,
			"spiral_speed": self.spiral_speed,
			"shrink_exponent": self.shrink_exponent,
			"add_shell": self.add_shell,
			"shell_color": self.shell_color.to_json(),
			"shell_size": self.shell_size,
		})
		return base

	@classmethod
	def from_json(cls, data: dict) -> TrajectoryElement:
		base = cls._from_json_base(data)
		return cls(
			**base,
			traj_type=TrajectoryType(data.get("type", "launch")),
			start_position=Position.from_json(data.get("start_position", {})),
			end_position=Position.from_json(data.get("end_position", {})),
			traj_color=GradientColor.from_json(data.get("traj_color", {})),
			k=data.get("k", 1.2),
			m0=data.get("m0", 0.5),
			rho=data.get("rho", 1.0),
			lifetime=data.get("lifetime", 3.0),
			particle_count=data.get("particle_count", 1),
			range_x=data.get("range_x", 0.0),
			range_y=data.get("range_y", 0.0),
			range_z=data.get("range_z", 0.0),
			speed_factor=data.get("speed_factor", 1.0),
			spiral_radius=data.get("spiral_radius", 2.0),
			spiral_speed=data.get("spiral_speed", 3.0),
			shrink_exponent=data.get("shrink_exponent", 1.0),
			add_shell=data.get("add_shell", False),
			shell_color=ColorRGB.from_json(data.get("shell_color", {})),
			shell_size=data.get("shell_size", 1.0),
		)
