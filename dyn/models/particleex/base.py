"""Element 基类 + ElementType 枚举."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from uuid import uuid4

class ElementType(Enum):
	TRAJECTORY = auto()
	FIREWORK = auto()
	TRAJ_FIREWORK = auto()

@dataclass
class Element:
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
