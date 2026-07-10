"""项目容器模型"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from dyn.lib.file_format import read_project_archive, write_project_archive
from dyn.logging_config import get_logger

log = get_logger(__name__)

from .elements import (
	Element,
	TrajectoryElement,
	FireworkElement,
	TrajFireworkElement,
)

@dataclass
class Project:
	"""DynFirework 项目的完整数据容器."""

	version: str = "1.0"
	name: str = "Untitled"
	bpm: float = 120.0
	time_signature: tuple[int, int] = (4, 4)
	ticks_per_beat: int = 20
	mc_version: str = "1.20.1"

	trajectories: list[TrajectoryElement] = field(default_factory=list)
	fireworks: list[FireworkElement] = field(default_factory=list)
	traj_fireworks: list[TrajFireworkElement] = field(default_factory=list)
	saved_positions: list[dict] = field(default_factory=list)

	timeline_zoom: float = 1.0
	timeline_scroll_offset: int = 0
	playback_cursor_tick: int = 0

	# 音乐嵌入 不参与 JSON 序列化
	music_data: bytes | None = field(default=None, repr=False, compare=False)
	music_original_name: str = field(default="", repr=False, compare=False)

	@property
	def music_path(self) -> str:
		"""向后兼容: 返回音乐原始文件名."""
		return self.music_original_name

	@music_path.setter
	def music_path(self, value: str) -> None:
		self.music_original_name = value

	@property
	def has_music(self) -> bool:
		"""是否有嵌入的音乐数据."""
		return self.music_data is not None and len(self.music_data) > 0

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
		"""序列化为 JSON 字典（不含音乐数据）."""
		return {
			"version": self.version,
			"project": {
				"name": self.name,
				"bpm": self.bpm,
				"time_signature": list(self.time_signature),
				"ticks_per_beat": self.ticks_per_beat,
				"mc_version": self.mc_version,
				"music_original_name": self.music_original_name,
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
		"""从 JSON 字典反序列化（不含音乐数据）."""
		proj = data.get("project", {})
		ts_data = data.get("timeline_state", {})
		return cls(
			version=data.get("version", "1.0"),
			name=proj.get("name", "Untitled"),
			bpm=proj.get("bpm", 120.0),
			time_signature=tuple(proj.get("time_signature", [4, 4])),
			ticks_per_beat=proj.get("ticks_per_beat", 20),
			mc_version=proj.get("mc_version", "1.20.1"),
			music_original_name=proj.get("music_original_name", ""),
			trajectories=[TrajectoryElement.from_json(t) for t in data.get("trajectories", [])],
			fireworks=[FireworkElement.from_json(f) for f in data.get("fireworks", [])],
			traj_fireworks=[TrajFireworkElement.from_json(tf) for tf in data.get("traj_fireworks", [])],
			saved_positions=data.get("saved_positions", []),
			timeline_zoom=ts_data.get("zoom", 1.0),
			timeline_scroll_offset=ts_data.get("scroll_offset", 0),
			playback_cursor_tick=ts_data.get("playback_cursor_tick", 0),
		)

	# 文件 I/O tar.gz 归档格式
	@classmethod
	def from_file(cls, path: str | Path) -> Project:
		"""从 .dyn 文件读取项目."""

		path = Path(path)
		log.debug(f"读取项目文件: {path}")
		result = read_project_archive(path)

		# 从 manifest 提取项目元数据
		proj_meta = result.manifest.get("project", {})

		# 按类型分组元素
		trajs, fws, tfs = [], [], []
		for elem in result.elements:
			etype = elem["type"]
			data = elem["data"]
			if etype == "trajectory":
				trajs.append(TrajectoryElement.from_json(data))
			elif etype == "firework":
				fws.append(FireworkElement.from_json(data))
			elif etype == "traj_firework":
				tfs.append(TrajFireworkElement.from_json(data))

		music_name = ""
		if result.manifest.get("music"):
			music_name = result.manifest["music"].get("original_name", "")

		proj = cls(
			version=result.manifest.get("format_version", "1.0"),
			name=proj_meta.get("name", "Untitled"),
			bpm=proj_meta.get("bpm", 120.0),
			time_signature=tuple(proj_meta.get("time_signature", [4, 4])),
			ticks_per_beat=proj_meta.get("ticks_per_beat", 20),
			mc_version=proj_meta.get("mc_version", "1.20.1"),
			music_original_name=music_name,
			trajectories=trajs,
			fireworks=fws,
			traj_fireworks=tfs,
			saved_positions=result.positions,
			timeline_zoom=result.timeline_state.get("zoom", 1.0),
			timeline_scroll_offset=result.timeline_state.get("scroll_offset", 0),
			playback_cursor_tick=result.timeline_state.get("playback_cursor_tick", 0),
		)

		if result.music_data:
			proj.music_data = result.music_data

		if result.errors:
			log.warning(
				f"项目文件存在 {len(result.errors)} 个校验问题: {result.errors}"
			)

		log.debug(f"项目加载完成: name={proj.name}, traj={len(trajs)}, fw={len(fws)}, tf={len(tfs)}, positions={len(result.positions)}, music={'有' if result.music_data else '无'}")
		return proj

	def to_file(self, path: str | Path) -> None:
		"""将项目写入 .dyn tar.gz 归档."""

		path = Path(path)
		log.debug(f"写入项目归档: {path}")

		# 项目元数据
		proj_meta = {
			"name": self.name,
			"bpm": self.bpm,
			"time_signature": list(self.time_signature),
			"ticks_per_beat": self.ticks_per_beat,
			"mc_version": self.mc_version,
		}

		# 构建元素列表
		elements: list[dict[str, Any]] = []
		for e in self.trajectories:
			elements.append({"type": "trajectory", "id": e.id, "data": e.to_json()})
		for e in self.fireworks:
			elements.append({"type": "firework", "id": e.id, "data": e.to_json()})
		for e in self.traj_fireworks:
			elements.append({"type": "traj_firework", "id": e.id, "data": e.to_json()})

		# 时间线状态
		ts = {
			"zoom": self.timeline_zoom,
			"scroll_offset": self.timeline_scroll_offset,
			"playback_cursor_tick": self.playback_cursor_tick,
		}

		log.debug(f"写入 {len(elements)} 条元素")
		write_project_archive(
			filepath=path,
			manifest_data=proj_meta,
			elements=elements,
			positions=self.saved_positions,
			timeline_state=ts,
			music_data=self.music_data,
			music_original_name=self.music_original_name,
		)

		log.debug(f"项目写入完成: {self.name}")

	def to_json_string(self) -> str:
		"""序列化为 JSON 字符串."""
		return json.dumps(self.to_json(), ensure_ascii=False, indent=2)
