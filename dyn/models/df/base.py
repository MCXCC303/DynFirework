"""Element 抽象基类 + ElementCategory 枚举."""
from __future__ import annotations

from abc import abstractmethod, ABC
from dataclasses import dataclass, field
from enum import Enum
from uuid import uuid4

class ElementCategory(Enum):
	FIREWORK = "firework"
	TRAJECTORY = "trajectory"
	EFFECT = "effect"
	COMPOSITE = "composite"

@dataclass
class Element(ABC):
	id: str = field(default_factory=lambda: str(uuid4()))
	name: str = "New Element"
	start_time: float = 0.0
	duration: float = 2.0
	enabled: bool = True
	notes: str = ""

	@property
	def end_time(self) -> float:
		return self.start_time + self.duration

	@property
	@abstractmethod
	def category(self) -> ElementCategory: ...

	def to_json(self) -> dict:
		return {
			"id": self.id,
			"name": self.name,
			"start_time": self.start_time,
			"duration": self.duration,
			"enabled": self.enabled,
			"notes": self.notes,
		}

	@classmethod
	def _from_json_base(cls, data: dict) -> dict:
		return {
			"id": data.get("id", str(uuid4())),
			"name": data.get("name", "New Element"),
			"start_time": data.get("start_time", 0.0),
			"duration": data.get("duration", 2.0),
			"enabled": data.get("enabled", True),
			"notes": data.get("notes", ""),
		}
