"""项目容器模型"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from dyn.logging_config import get_logger

log = get_logger(__name__)

from .elements import (
    Element,
    TrajectoryElement,
    FireworkElement,
    TrajFireworkElement,
    Position,
)


@dataclass
class Project:
    """DynFirework 项目的完整数据容器."""

    version: str = "1.0"
    name: str = "Untitled"
    music_path: str = ""
    bpm: float = 120.0
    time_signature: tuple[int, int] = (4, 4)
    ticks_per_beat: int = 20

    trajectories: list[TrajectoryElement] = field(default_factory=list)
    fireworks: list[FireworkElement] = field(default_factory=list)
    traj_fireworks: list[TrajFireworkElement] = field(default_factory=list)
    saved_positions: list[dict] = field(default_factory=list)

    timeline_zoom: float = 1.0
    timeline_scroll_offset: int = 0
    playback_cursor_tick: int = 0

    @property
    def all_elements(self) -> list[Element]:
        return self.trajectories + self.fireworks + self.traj_fireworks  # type: ignore[return-type]

    @property
    def total_duration_ticks(self) -> int:
        if not self.all_elements:
            return 0
        return max(e.end_tick for e in self.all_elements)

    def get_element(self, element_id: str) -> Element | None:
        for e in self.all_elements:
            if e.id == element_id:
                return e
        return None

    def remove_element(self, element_id: str) -> Element | None:
        for lst in (self.trajectories, self.fireworks, self.traj_fireworks):  # type: ignore[assignment]
            for i, e in enumerate(lst):
                if e.id == element_id:
                    return lst.pop(i)
        return None

    def add_trajectory(self, elem: TrajectoryElement) -> None:
        self.trajectories.append(elem)

    def add_firework(self, elem: FireworkElement) -> None:
        self.fireworks.append(elem)

    def to_json(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "project": {
                "name": self.name,
                "music_path": self.music_path,
                "bpm": self.bpm,
                "time_signature": list(self.time_signature),
                "ticks_per_beat": self.ticks_per_beat,
            },
            "trajectories": [t.to_json() for t in self.trajectories],
            "fireworks": [f.to_json() for f in self.fireworks],
            "traj_fireworks": [tf.to_json() for tf in self.traj_fireworks],
            "saved_positions": self.saved_positions,
            "timeline_state": {
                "zoom": self.timeline_zoom,
                "scroll_offset": self.timeline_scroll_offset,
                "playback_cursor_tick": self.playback_cursor_tick,
            },
        }

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> Project:
        proj = data.get("project", {})
        ts_data = data.get("timeline_state", {})
        return cls(
            version=data.get("version", "1.0"),
            name=proj.get("name", "Untitled"),
            music_path=proj.get("music_path", ""),
            bpm=proj.get("bpm", 120.0),
            time_signature=tuple(proj.get("time_signature", [4, 4])),
            ticks_per_beat=proj.get("ticks_per_beat", 20),
            trajectories=[TrajectoryElement.from_json(t) for t in data.get("trajectories", [])],
            fireworks=[FireworkElement.from_json(f) for f in data.get("fireworks", [])],
            traj_fireworks=[TrajFireworkElement.from_json(tf) for tf in data.get("traj_fireworks", [])],
            saved_positions=data.get("saved_positions", []),
            timeline_zoom=ts_data.get("zoom", 1.0),
            timeline_scroll_offset=ts_data.get("scroll_offset", 0),
            playback_cursor_tick=ts_data.get("playback_cursor_tick", 0),
        )

    @classmethod
    def from_file(cls, path: str | Path) -> Project:
        log.info(f"读取项目文件: {path}")
        raw = Path(path).read_text(encoding="utf-8")
        data = json.loads(raw)
        proj = cls.from_json(data)
        log.info(f"项目加载完成: {proj.name}, 元素={len(proj.all_elements)}")
        return proj

    def to_file(self, path: str | Path) -> None:
        log.info(f"写入项目文件: {path}")
        text = json.dumps(self.to_json(), ensure_ascii=False, indent=2)
        Path(path).write_text(text, encoding="utf-8")
        log.debug(f"项目写入完成: {len(text)} 字节")

    def to_json_string(self) -> str:
        return json.dumps(self.to_json(), ensure_ascii=False, indent=2)
