"""FireworkElement - 爆炸类烟花."""
from __future__ import annotations

from dataclasses import dataclass, field

from .base import Element, ElementCategory
from .values import ColorRGB, GradientColor, Position, FireworkType

@dataclass
class FireworkElement(Element):
	fw_type: FireworkType = FireworkType.SINGLE_LAYER
	position: Position = field(default_factory=lambda: Position(y=80))

	inner_color: GradientColor = field(default_factory=GradientColor)
	outer_color: GradientColor = field(
		default_factory=lambda: GradientColor(start=ColorRGB(r=255, g=0, b=0), end=ColorRGB(r=255, g=100, b=100))
	)

	speed: float = 10.0
	inner_speed: float = 8.0
	outer_speed: float = 10.0
	particle_count: int = 100
	inner_count: int = 80
	outer_count: int = 120
	horizontal_angle: float = 30.0
	vertical_angle: float = 30.0
	spread_angle: float = 15.0
	direction_count: int = 12
	track_count: int = 5
	radius: float = 5.0
	radial_speed: float = 3.0

	expansion_speed: float = 2.0
	density_falloff: float = 2.0

	enable_tail_flicker: bool = False

	@property
	def category(self) -> ElementCategory:
		return ElementCategory.FIREWORK

	def to_json(self) -> dict:
		base = super().to_json()
		base.update({
			"type": self.fw_type.value,
			"position": self.position.to_json(),
			"inner_color": self.inner_color.to_json(),
			"outer_color": self.outer_color.to_json(),
			"speed": self.speed,
			"inner_speed": self.inner_speed,
			"outer_speed": self.outer_speed,
			"particle_count": self.particle_count,
			"inner_count": self.inner_count,
			"outer_count": self.outer_count,
			"horizontal_angle": self.horizontal_angle,
			"vertical_angle": self.vertical_angle,
			"spread_angle": self.spread_angle,
			"direction_count": self.direction_count,
			"track_count": self.track_count,
			"radius": self.radius,
			"radial_speed": self.radial_speed,
			"expansion_speed": self.expansion_speed,
			"density_falloff": self.density_falloff,
			"enable_tail_flicker": self.enable_tail_flicker,
		})
		return base

	@classmethod
	def from_json(cls, data: dict) -> FireworkElement:
		base = cls._from_json_base(data)
		return cls(
			**base,
			fw_type=FireworkType(data.get("type", "single_layer")),
			position=Position.from_json(data.get("position", {})),
			inner_color=GradientColor.from_json(data.get("inner_color", {})),
			outer_color=GradientColor.from_json(data.get("outer_color", {})),
			speed=data.get("speed", 10.0),
			inner_speed=data.get("inner_speed", 8.0),
			outer_speed=data.get("outer_speed", 10.0),
			particle_count=data.get("particle_count", 100),
			inner_count=data.get("inner_count", 80),
			outer_count=data.get("outer_count", 120),
			horizontal_angle=data.get("horizontal_angle", 30.0),
			vertical_angle=data.get("vertical_angle", 30.0),
			spread_angle=data.get("spread_angle", 15.0),
			direction_count=data.get("direction_count", 12),
			track_count=data.get("track_count", 5),
			radius=data.get("radius", 5.0),
			radial_speed=data.get("radial_speed", 3.0),
			expansion_speed=data.get("expansion_speed", 2.0),
			density_falloff=data.get("density_falloff", 2.0),
			enable_tail_flicker=data.get("enable_tail_flicker", False),
		)
