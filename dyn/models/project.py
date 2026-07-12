"""项目容器模型 创建时锁定后端."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from dyn.lib.file_format import FORMAT_VERSION, read_project_archive, write_project_archive
from dyn.logging_config import get_logger

log = get_logger(__name__)

class Backend(Enum):
	CB = "cb"
	DF = "df"

# 元素类型标签 -> 类 的反序列化映射 (延迟初始化避免循环导入)
_CB_ELEMENT_CLASSES: dict[str, type] = {}
_DF_ELEMENT_CLASSES: dict[str, type] = {}

def _init_class_maps() -> None:
	if _CB_ELEMENT_CLASSES:
		return
	from .cb import (
		TrajectoryElement as CbTraj,
		FireworkElement as CbFw,
		TrajFireworkElement as CbTF,
	)
	_CB_ELEMENT_CLASSES.update({
		"trajectory": CbTraj,
		"firework": CbFw,
		"traj_firework": CbTF,
	})
	from .df.fireworks import FireworkElement
	from .df.trajectories import TrajectoryElement
	from .df.effects import EffectElement
	from .df.composites import CompositeElement
	_DF_ELEMENT_CLASSES.update({
		"df_firework": FireworkElement,
		"df_trajectory": TrajectoryElement,
		"df_effect": EffectElement,
		"df_composite": CompositeElement,
	})

def _get_type_tag(elem, backend: Backend) -> str:
	"""根据元素实例和后端返回序列化类型标签."""
	if backend == Backend.CB:
		from .cb import (
			TrajectoryElement as CbTraj,
			FireworkElement as CbFw,
			TrajFireworkElement as CbTF,
		)
		if isinstance(elem, CbTF):
			return "traj_firework"
		if isinstance(elem, CbTraj):
			return "trajectory"
		if isinstance(elem, CbFw):
			return "firework"
		log.error(f"未知 CB 元素类型: {type(elem)}, id={getattr(elem, 'id', 'N/A')}, name={getattr(elem, 'name', 'N/A')}")
		raise ValueError(f"Unknown cb element type: {type(elem)}")
	else:
		cat = elem.category
		return f"df_{cat.value}"

def _deserialize_element(backend: Backend, type_tag: str, data: dict):
	"""根据后端和类型标签反序列化元素."""
	_init_class_maps()
	class_map = _CB_ELEMENT_CLASSES if backend == Backend.CB else _DF_ELEMENT_CLASSES
	cls = class_map.get(type_tag)
	if cls is None:
		log.warning(f"未知元素类型标签: type_tag={type_tag}, backend={backend.value}")
		raise ValueError(f"Unknown element type: {type_tag} for backend {backend.value}")
	return cls.from_json(data)

@dataclass
class Project:
	"""项目容器 创建时锁定后端."""

	backend: Backend = Backend.DF
	name: str = "Untitled"
	mc_version: str = "1.21.8"
	bpm: float = 120.0
	time_signature: tuple[Any, ...] = (4, 4)
	ticks_per_beat: int = 20

	elements: list = field(default_factory=list)
	saved_positions: list[dict] = field(default_factory=list)

	timeline_zoom: float = 1.0
	timeline_scroll_offset: int = 0
	playback_cursor_tick: int = 0

	music_data: bytes | None = field(default=None, repr=False, compare=False)
	music_original_name: str = field(default="", repr=False, compare=False)

	audio_offset_ms: float = 0.0

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
		return self.elements

	@property
	def total_duration_ticks(self) -> int:
		return int(self.total_duration * 20)

	@property
	def total_duration(self) -> float:
		if not self.elements:
			return 0.0
		if self.backend == Backend.DF:
			return max(e.end_time for e in self.elements)
		return max(e.end_tick for e in self.elements) / 20.0

	def get_element(self, element_id: str):
		for e in self.elements:
			if e.id == element_id:
				return e
		log.debug(f"元素未找到: id={element_id}")
		return None

	def remove_element(self, element_id: str):
		for i, e in enumerate(self.elements):
			if e.id == element_id:
				removed = self.elements.pop(i)
				log.info(f"移除元素: id={removed.id}, name={removed.name}")
				return removed
		log.warning(f"移除元素未找到: id={element_id}")
		return None

	def add_element(self, elem) -> None:
		log.info(f"添加元素: id={elem.id}, name={elem.name}")
		self.elements.append(elem)

	def to_json(self) -> dict[str, Any]:
		elements_payload: list[dict[str, Any]] = []
		for e in self.elements:
			elements_payload.append({
				"type": _get_type_tag(e, self.backend),
				"id": e.id,
				"data": e.to_json(),
			})

		return {
			"format_version": FORMAT_VERSION,
			"backend": self.backend.value,
			"project": {
				"name": self.name,
				"bpm": self.bpm,
				"time_signature": list(self.time_signature),
				"ticks_per_beat": self.ticks_per_beat,
				"mc_version": self.mc_version,
				"music_original_name": self.music_original_name,
				"audio_offset_ms": self.audio_offset_ms,
			},
			"elements": elements_payload,
			"saved_positions": self.saved_positions,
			"timeline_state": {
				"zoom": self.timeline_zoom,
				"scroll_offset": self.timeline_scroll_offset,
				"playback_cursor_tick": self.playback_cursor_tick,
			},
		}

	@classmethod
	def from_json(cls, data: dict[str, Any]) -> Project:
		proj_data = data.get("project", {})
		ts_data = data.get("timeline_state", {})

		backend_raw = data.get("backend", "df")
		try:
			backend = Backend(backend_raw)
		except ValueError:
			log.warning(f"未知后端类型: {backend_raw}，回退为 df")
			backend = Backend.DF

		elements: list = []
		for entry in data.get("elements", []):
			type_tag = entry["type"]
			elem_data = entry["data"]
			try:
				elements.append(_deserialize_element(backend, type_tag, elem_data))
			except (KeyError, ValueError) as e:
				log.warning(f"元素反序列化失败: {e}, type={type_tag}, id={entry.get('id')}")

		music_name = data.get("music", {}).get("original_name", "") or proj_data.get("music_original_name", "")

		return cls(
			backend=backend,
			name=proj_data.get("name", "Untitled"),
			bpm=proj_data.get("bpm", 120.0),
			time_signature=tuple(proj_data.get("time_signature", [4, 4])),
			ticks_per_beat=proj_data.get("ticks_per_beat", 20),
			mc_version=proj_data.get("mc_version", "1.21.8"),
			music_original_name=music_name,
			audio_offset_ms=proj_data.get("audio_offset_ms", 0.0),
			elements=elements,
			saved_positions=data.get("saved_positions", []),
			timeline_zoom=ts_data.get("zoom", 1.0),
			timeline_scroll_offset=ts_data.get("scroll_offset", 0),
			playback_cursor_tick=ts_data.get("playback_cursor_tick", 0),
		)

	@classmethod
	def from_file(cls, path: str | Path) -> Project:
		path = Path(path)
		log.debug(f"读取项目文件: {path}")
		result = read_project_archive(path)

		manifest = result.manifest
		proj_data = manifest.get("project", {})

		backend_raw = manifest.get("backend", "df")
		try:
			backend = Backend(backend_raw)
		except ValueError:
			log.warning(f"未知后端类型: {backend_raw}，回退为 df")
			backend = Backend.DF

		elements: list = []
		for elem in result.elements:
			type_tag = elem["type"]
			elem_data = elem["data"]
			try:
				elements.append(_deserialize_element(backend, type_tag, elem_data))
			except (KeyError, ValueError) as e:
				log.warning(f"元素反序列化失败: {e}, type={type_tag}, id={elem.get('id')}")

		music_name = ""
		if manifest.get("music"):
			music_name = manifest["music"].get("original_name", "")

		proj = cls(
			backend=backend,
			name=proj_data.get("name", "Untitled"),
			bpm=proj_data.get("bpm", 120.0),
			time_signature=tuple(proj_data.get("time_signature", [4, 4])),
			ticks_per_beat=proj_data.get("ticks_per_beat", 20),
			mc_version=proj_data.get("mc_version", "1.21.8"),
			music_original_name=music_name,
			audio_offset_ms=proj_data.get("audio_offset_ms", 0.0),
			elements=elements,
			saved_positions=result.positions,
			timeline_zoom=result.timeline_state.get("zoom", 1.0),
			timeline_scroll_offset=result.timeline_state.get("scroll_offset", 0),
			playback_cursor_tick=result.timeline_state.get("playback_cursor_tick", 0),
		)

		if result.music_data:
			proj.music_data = result.music_data

		if result.errors:
			log.warning(f"项目文件存在 {len(result.errors)} 个校验问题: {result.errors}")

		log.debug(f"项目加载完成: name={proj.name}, backend={proj.backend.value}, elements={len(elements)}")
		return proj

	def to_file(self, path: str | Path) -> None:
		path = Path(path)
		log.debug(f"写入项目归档: {path}")

		proj_meta = {
			"name": self.name,
			"bpm": self.bpm,
			"time_signature": list(self.time_signature),
			"ticks_per_beat": self.ticks_per_beat,
			"mc_version": self.mc_version,
			"audio_offset_ms": self.audio_offset_ms,
		}

		elements_payload: list[dict[str, Any]] = []
		for e in self.elements:
			elements_payload.append({
				"type": _get_type_tag(e, self.backend),
				"id": e.id,
				"data": e.to_json(),
			})

		ts = {
			"zoom": self.timeline_zoom,
			"scroll_offset": self.timeline_scroll_offset,
			"playback_cursor_tick": self.playback_cursor_tick,
		}

		write_project_archive(
			filepath=path,
			backend=self.backend.value,
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
