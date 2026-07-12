from __future__ import annotations

from dataclasses import dataclass, field

from dyn.logging_config import get_logger
from .base import Element, ElementType

log = get_logger(__name__)
from .values import ColorRGB, GradientColor, Position

@dataclass
class FireworkElement(Element):
	fw_type: str = "single_layer"

	position: Position = field(default_factory=lambda: Position(x=10, y=80, z=10))

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

	horizontal_angle: float = 30.0
	vertical_angle: float = 30.0

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
		log.debug(f"反序列化 FireworkElement: name={base.get('name')}")
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
