"""ColorRGB, Position, GradientColor + TrajType, FireworkType 值对象枚举."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

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
