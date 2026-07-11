"""导出服务 将项目元素生成为 Minecraft 数据包."""
from __future__ import annotations

import json
from pathlib import Path

from PySide6.QtCore import QObject, Signal
from PySide6.QtCore import QRunnable, QThreadPool

from dyn.lib import global_storage, export_mcfunction
from dyn.lib import trajectories as traj, fireworks as fw
from dyn.lib.backend_registry import set_backend, resolve_mc_version, BackendType
from dyn.lib.export_helpers import (
	TRAJ_FUNC_MAP, FW_FUNC_MAP, build_traj_kwargs, fill_fw_kwargs,
)
from dyn.logging_config import get_logger

log = get_logger(__name__)

from dyn.models.elements import (
	Element,
	TrajectoryElement,
	FireworkElement,
	Position,
)

class _TaskSignals(QObject):
	"""QRunnable 信号容器."""
	finished = Signal(bool, str)  # success, message
	progress = Signal(int)

class _ExportTask(QRunnable):
	"""后台导出任务 不阻塞 UI."""

	def __init__(self, elements: list[Element], output_dir: str, namespace: str,
	             datapack_name: str = "DynFirework", description: str = "",
	             pack_format: int = 6, mc_version: str = "1.20.1") -> None:
		super().__init__()
		self._elements = elements
		self._output_dir = output_dir
		self._namespace = namespace
		self._datapack_name = datapack_name
		self._description = description
		self._pack_format = pack_format
		self._mc_version = mc_version
		self.signals = _TaskSignals()

	def run(self) -> None:
		try:
			log.debug(f"导出开始: {self._output_dir}, namespace={self._namespace}, elements={len(self._elements)}")
			self._do_export()
			self.signals.finished.emit(True, f"导出完成: {self._output_dir}")
		except Exception as e:
			log.exception("导出失败")
			self.signals.finished.emit(False, f"导出失败: {e}")

	def _do_export(self) -> None:

		# 根据MC版本设置后端
		try:
			info = resolve_mc_version(self._mc_version)
			set_backend(info.backend)
			log.debug(f"导出后端: {info.backend.value}, MC版本: {self._mc_version}, pack_format: {info.pack_format}")
		except KeyError:
			log.warning(f"未知MC版本: {self._mc_version}, 使用默认DFP后端")
			set_backend(BackendType.DFP)

		# 清空全局存储
		global_storage.commands_by_tick.clear()
		global_storage.MAX_TICK = 0

		total = len(self._elements)
		log.debug(f"开始导出 {total} 个元素, namespace={self._namespace}, mc_version={self._mc_version}")
		for i, elem in enumerate(self._elements):
			if not elem.enabled:
				log.debug(f"跳过禁用元素: id={elem.id}, name={elem.name}")
				continue

			if isinstance(elem, TrajectoryElement):
				log.debug(f"导出轨迹 [{i + 1}/{total}]: id={elem.id}, name={elem.name}, type={elem.traj_type}")
				self._export_trajectory(elem, traj)
			elif isinstance(elem, FireworkElement):
				log.debug(f"导出烟花 [{i + 1}/{total}]: id={elem.id}, name={elem.name}, type={elem.fw_type}")
				self._export_firework(elem, fw)
			elif hasattr(elem, 'traj_type') and hasattr(elem, 'fw_type'):
				# TrajFireworkElement 导出轨迹 + 烟花
				log.debug(f"导出轨迹烟花 [{i + 1}/{total}]: id={elem.id}, name={elem.name}")
				self._export_tf(elem, traj, fw)

			self.signals.progress.emit(int((i + 1) / total * 100))

		# 创建完整数据包结构
		cmd_count = sum(len(v) for v in global_storage.commands_by_tick.values())
		log.debug(f"命令生成完成: {cmd_count} 条命令, MAX_TICK={global_storage.MAX_TICK}")
		pack_dir = Path(self._output_dir) / self._datapack_name
		func_dir = pack_dir / "data" / self._namespace / "functions"
		func_dir.mkdir(parents=True, exist_ok=True)

		# 写入 pack.mcmeta
		mcmeta = {"pack": {"pack_format": self._pack_format, "description": self._description}}
		(pack_dir / "pack.mcmeta").write_text(json.dumps(mcmeta, ensure_ascii=False, indent=2), encoding="utf-8")

		# 写入 function 文件
		export_mcfunction.export_mcfunction(str(func_dir), self._namespace)

		# 生成 auto_exec.mcfunction
		export_mcfunction.generate_auto_exec_file(str(func_dir), self._namespace)

	def _export_tf(self, elem, traj, fw) -> None:
		"""导出 TrajFireworkElement 分别导出轨迹和烟花部分."""
		pos = elem.start_position or Position()
		end = elem.mid_position or Position()

		func = getattr(traj, TRAJ_FUNC_MAP.get(elem.traj_type, "launch_trajectory"), None)
		if func:
			kwargs = build_traj_kwargs(elem, pos.x, pos.y, pos.z,
			                           end.x, end.y, end.z,
			                           elem.traj_duration_ticks)
			func(elem.start_tick, **kwargs)

		fw_func = getattr(fw, FW_FUNC_MAP.get(elem.fw_type, "basic_single_layer_firework"), None)
		if fw_func:
			fw_kwargs = {
				"tick": elem.fw_start_tick,
				"x": end.x, "y": end.y, "z": end.z,
				"duration": elem.fw_duration_ticks / 20,
				"lifetime": elem.fw_duration_ticks / 20,
			}
			fill_fw_kwargs(elem, fw_kwargs)
			fw_func(**fw_kwargs)

	def _export_trajectory(self, elem: TrajectoryElement, traj) -> None:
		func = getattr(traj, TRAJ_FUNC_MAP.get(elem.traj_type, "launch_trajectory"), None)
		if func is None:
			return

		pos = elem.start_position
		end = elem.end_position
		kwargs = build_traj_kwargs(elem, pos.x, pos.y, pos.z,
		                           end.x, end.y, end.z,
		                           elem.duration_ticks)
		func(elem.start_tick, **kwargs)

	def _export_firework(self, elem: FireworkElement, fw) -> None:
		func = getattr(fw, FW_FUNC_MAP.get(elem.fw_type, "basic_single_layer_firework"), None)
		if func is None:
			return

		pos = elem.position
		kwargs: dict = {
			"tick": elem.start_tick,
			"x": pos.x, "y": pos.y, "z": pos.z,
			"duration": elem.duration_ticks / 20,
			"lifetime": elem.duration_ticks / 20,
		}
		fill_fw_kwargs(elem, kwargs)
		func(**kwargs)

class ExportService(QObject):
	"""导出服务入口."""

	export_finished = Signal(bool, str)
	export_progress = Signal(int)

	def __init__(self, parent: QObject | None = None) -> None:
		super().__init__(parent)

	def export_to_datapack(
			self,
			elements: list[Element],
			output_dir: str,
			namespace: str = "fireworks1",
			datapack_name: str = "DynFirework",
			description: str = "",
			pack_format: int = 6,
			mc_version: str = "1.20.1",
	) -> None:
		task = _ExportTask(elements, output_dir, namespace,
		                   datapack_name, description, pack_format, mc_version)
		task.signals.finished.connect(self.export_finished)
		task.signals.progress.connect(self.export_progress)
		QThreadPool.globalInstance().start(task)
