"""项目容器模型 V2 单列表 + V1 三列表向后兼容."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from dyn.lib.file_format import read_project_archive, write_project_archive
from dyn.logging_config import get_logger

log = get_logger(__name__)

from .df.base import Element as DfElement, ElementCategory
from .df.composites import CompositeElement
from .df.effects import EffectElement
from .df.fireworks import FireworkElement as FireworkElementV2
from .df.trajectories import TrajectoryElement as TrajectoryElementV2
from .particleex import (
	Element as V1Element,
	TrajectoryElement as V1TrajectoryElement,
	FireworkElement as V1FireworkElement,
	TrajFireworkElement as V1TrajFireworkElement,
)

_V2_ELEMENT_CLASSES: dict[str, type] = {
	"firework_v2": FireworkElementV2,
	"trajectory_v2": TrajectoryElementV2,
	"effect": EffectElement,
	"composite": CompositeElement,
}

_V1_ELEMENT_CLASSES: dict[str, type] = {
	"trajectory": V1TrajectoryElement,
	"firework": V1FireworkElement,
	"traj_firework": V1TrajFireworkElement,
}

def _detect_element_version(data: dict) -> str:
	"""检测元素 JSON 数据的格式版本.
	V1: 包含 start_tick / duration_ticks
	V2: 包含 start_time / duration
	"""
	if "start_tick" in data or "duration_ticks" in data:
		return "v1"
	return "v2"

def _convert_v1_element_to_v2(elem: V1Element) -> DfElement:
	"""将 V1 元素对象转换为 V2."""
	from dyn.lib.export_helpers import _ensure_v2
	return _ensure_v2(elem)

def _deserialize_v2_element(etype: str, data: dict) -> DfElement:
	"""从 JSON 反序列化 V2 元素."""
	cls = _V2_ELEMENT_CLASSES.get(etype)
	if cls is None:
		raise ValueError(f"Unknown V2 element type: {etype}")
	return cls.from_json(data)

def _deserialize_v1_element(etype: str, data: dict) -> V1Element:
	"""从 JSON 反序列化 V1 元素."""
	cls = _V1_ELEMENT_CLASSES.get(etype)
	if cls is None:
		raise ValueError(f"Unknown V1 element type: {etype}")
	return cls.from_json(data)

@dataclass
class Project:
	"""DynFirework 项目的完整数据容器 V2."""

	version: str = "2.0"
	name: str = "Untitled"
	bpm: float = 120.0
	time_signature: tuple[Any] = (4, 4)
	ticks_per_beat: int = 20
	mc_version: str = "1.20.1"
	backend: str = "df"

	# V2 单列表
	elements: list[DfElement] = field(default_factory=list)

	# V1 三列表 向后兼容
	trajectories: list[V1TrajectoryElement] = field(default_factory=list)
	fireworks: list[V1FireworkElement] = field(default_factory=list)
	traj_fireworks: list[V1TrajFireworkElement] = field(default_factory=list)

	saved_positions: list[dict] = field(default_factory=list)

	timeline_zoom: float = 1.0
	timeline_scroll_offset: int = 0
	playback_cursor_tick: int = 0

	# 音乐嵌入 不参与 JSON 序列化
	music_data: bytes | None = field(default=None, repr=False, compare=False)
	music_original_name: str = field(default="", repr=False, compare=False)

	@property
	def music_path(self) -> str:
		return self.music_original_name

	@music_path.setter
	def music_path(self, value: str) -> None:
		self.music_original_name = value

	@property
	def has_music(self) -> bool:
		return self.music_data is not None and len(self.music_data) > 0

	@property
	def all_elements(self) -> list:
		"""返回所有元素 V2 优先."""
		if self.elements:
			return self.elements
		return self.trajectories + self.fireworks + self.traj_fireworks  # type: ignore[return-type]

	@property
	def total_duration_ticks(self) -> int:
		"""向后兼容 总时长 (tick)."""
		return int(self.total_duration * 20)

	@property
	def total_duration(self) -> float:
		"""总时长 (秒)."""
		if self.elements:
			if not self.elements:
				return 0.0
			return max(e.end_time for e in self.elements)
		all_elems = self.all_elements
		if not all_elems:
			return 0.0
		first = all_elems[0]
		if hasattr(first, 'end_time'):
			return max(e.end_time for e in all_elems)
		return max(e.end_tick for e in all_elems) / 20.0

	def get_element(self, element_id: str) -> DfElement | V1Element | None:
		for e in self.elements:
			if e.id == element_id:
				return e
		for lst in (self.trajectories, self.fireworks, self.traj_fireworks):  # type: ignore[assignment]
			for e in lst:
				if e.id == element_id:
					return e
		return None

	def remove_element(self, element_id: str) -> DfElement | V1Element | None:
		for i, e in enumerate(self.elements):
			if e.id == element_id:
				return self.elements.pop(i)
		for lst in (self.trajectories, self.fireworks, self.traj_fireworks):  # type: ignore[assignment]
			for i, e in enumerate(lst):
				if e.id == element_id:
					return lst.pop(i)
		return None

	def add_element(self, elem: DfElement) -> None:
		self.elements.append(elem)

	def to_json(self) -> dict[str, Any]:
		"""序列化为 JSON 字典 V2 格式."""
		result: dict[str, Any] = {
			"version": self.version,
			"project": {
				"name": self.name,
				"bpm": self.bpm,
				"time_signature": list(self.time_signature),
				"ticks_per_beat": self.ticks_per_beat,
				"mc_version": self.mc_version,
				"backend": self.backend,
				"music_original_name": self.music_original_name,
			},
			"elements": [
				{
					"type": f"{e.category.value}_v2" if e.category in (ElementCategory.FIREWORK,
					                                                   ElementCategory.TRAJECTORY) else e.category.value,
					"id": e.id,
					"data": e.to_json(),
				}
				for e in self.elements
			],
			"saved_positions": self.saved_positions,
			"timeline_state": {
				"zoom": self.timeline_zoom,
				"scroll_offset": self.timeline_scroll_offset,
				"playback_cursor_tick": self.playback_cursor_tick,
			},
		}
		return result

	@classmethod
	def from_json(cls, data: dict[str, Any]) -> Project:
		"""从 JSON 字典反序列化 支持 V1 和 V2 格式."""
		proj = data.get("project", {})
		ts_data = data.get("timeline_state", {})

		elements: list[DfElement] = []

		# V2 格式 elements 列表
		raw_elements = data.get("elements", [])
		if raw_elements:
			for entry in raw_elements:
				etype = entry["type"]
				elem_data = entry["data"]
				ver = _detect_element_version(elem_data)
				if ver == "v2":
					elements.append(_deserialize_v2_element(etype, elem_data))
				else:
					v1_elem = _deserialize_v1_element(etype, elem_data)
					elements.append(_convert_v1_element_to_v2(v1_elem))
		else:
			# V1 格式 三列表
			for t in data.get("trajectories", []):
				elements.append(_convert_v1_element_to_v2(V1TrajectoryElement.from_json(t)))
			for f in data.get("fireworks", []):
				elements.append(_convert_v1_element_to_v2(V1FireworkElement.from_json(f)))
			for tf in data.get("traj_fireworks", []):
				elements.append(_convert_v1_element_to_v2(V1TrajFireworkElement.from_json(tf)))

		return cls(
			version=data.get("version", "1.0"),
			name=proj.get("name", "Untitled"),
			bpm=proj.get("bpm", 120.0),
			time_signature=tuple(proj.get("time_signature", [4, 4])),
			ticks_per_beat=proj.get("ticks_per_beat", 20),
			mc_version=proj.get("mc_version", "1.20.1"),
			backend=proj.get("backend", "particleex" if data.get("version", "") == "1.0" else "df"),
			music_original_name=proj.get("music_original_name", ""),
			elements=elements,
			saved_positions=data.get("saved_positions", []),
			timeline_zoom=ts_data.get("zoom", 1.0),
			timeline_scroll_offset=ts_data.get("scroll_offset", 0),
			playback_cursor_tick=ts_data.get("playback_cursor_tick", 0),
		)

	# 文件 I/O

	@classmethod
	def from_file(cls, path: str | Path) -> Project:
		"""从 .dyn 文件读取项目 自动检测格式版本并迁移."""
		path = Path(path)
		log.debug(f"读取项目文件: {path}")
		result = read_project_archive(path)

		proj_meta = result.manifest.get("project", {})
		elements: list[DfElement] = []

		for elem in result.elements:
			etype = elem["type"]
			elem_data = elem["data"]
			ver = _detect_element_version(elem_data)
			if ver == "v2":
				try:
					elements.append(_deserialize_v2_element(etype, elem_data))
				except (KeyError, ValueError) as e:
					log.warning(f"V2 元素反序列化失败: {e}, type={etype}, id={elem.get('id')}")
			else:
				try:
					v1_elem = _deserialize_v1_element(etype, elem_data)
					elements.append(_convert_v1_element_to_v2(v1_elem))
				except (KeyError, ValueError) as e:
					log.warning(f"V1 元素反序列化/迁移失败: {e}, type={etype}, id={elem.get('id')}")

		music_name = ""
		if result.manifest.get("music"):
			music_name = result.manifest["music"].get("original_name", "")

		proj = cls(
			version=result.manifest.get("format_version", "2.0"),
			name=proj_meta.get("name", "Untitled"),
			bpm=proj_meta.get("bpm", 120.0),
			time_signature=tuple(proj_meta.get("time_signature", [4, 4])),
			ticks_per_beat=proj_meta.get("ticks_per_beat", 20),
			mc_version=proj_meta.get("mc_version", "1.20.1"),
			backend=proj_meta.get("backend", "particleex" if result.manifest.get("format_version", "") == "1.0" else "df"),
			music_original_name=music_name,
			elements=elements,
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

		log.debug(f"项目加载完成: name={proj.name}, elements={len(elements)}, positions={len(result.positions)}, music={'有' if result.music_data else '无'}")
		return proj

	def to_file(self, path: str | Path) -> None:
		"""将项目写入 .dyn tar.gz 归档 V2 格式."""
		path = Path(path)
		log.debug(f"写入项目归档: {path}")

		proj_meta = {
			"name": self.name,
			"bpm": self.bpm,
			"time_signature": list(self.time_signature),
			"ticks_per_beat": self.ticks_per_beat,
			"mc_version": self.mc_version,
			"backend": self.backend,
		}

		elements_payload: list[dict[str, Any]] = []
		for e in self.elements:
			cat = e.category
			if cat in (ElementCategory.FIREWORK, ElementCategory.TRAJECTORY):
				etype = f"{cat.value}_v2"
			else:
				etype = cat.value
			elements_payload.append({"type": etype, "id": e.id, "data": e.to_json()})

		ts = {
			"zoom": self.timeline_zoom,
			"scroll_offset": self.timeline_scroll_offset,
			"playback_cursor_tick": self.playback_cursor_tick,
		}

		log.debug(f"写入 {len(elements_payload)} 条元素")
		write_project_archive(
			filepath=path,
			manifest_data=proj_meta,
			elements=elements_payload,
			positions=self.saved_positions,
			timeline_state=ts,
			music_data=self.music_data,
			music_original_name=self.music_original_name,
		)

		log.debug(f"项目写入完成: {self.name}")

	def to_json_string(self) -> str:
		return json.dumps(self.to_json(), ensure_ascii=False, indent=2)
