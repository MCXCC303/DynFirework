"""导出服务   将项目元素生成为 Minecraft 数据包."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QObject, Signal
from PySide6.QtCore import QRunnable, QThreadPool

from dyn.logging_config import get_logger

log = get_logger(__name__)

from dyn.models.elements import (
	Element,
	TrajectoryElement,
	FireworkElement,
	Position,
)

# 映射 gui 模板名或元素类型到实际函数
_TRAJ_FUNC_MAP = {
	"launch": "launch_trajectory",
	"spark": "launch_spark_trajectory",
	"offset": "trajectory_with_random_offset",
	"thick": "thick_trajectory_with_random_offset",
	"expanding": "expanding_trajectory_with_random_offset",
}

_FW_FUNC_MAP = {
	"single_layer": "basic_single_layer_firework",
	"double_layer": "basic_double_layer_firework",
	"directional": "directional_firework",
	"clustered": "clustered_firework",
	"expanding_sphere": "expanding_sphere_firework",
}

class _TaskSignals(QObject):
	"""QRunnable 信号容器."""
	finished = Signal(bool, str)  # success, message
	progress = Signal(int)

class _ExportTask(QRunnable):
	"""后台导出任务   不阻塞 UI."""

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
				# TrajFireworkElement   导出轨迹 + 烟花
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
		"""导出 TrajFireworkElement   分别导出轨迹和烟花部分."""
		# 轨迹部分
		pos = elem.start_position or Position()
		end = elem.mid_position or Position()
		color = elem.traj_color
		func = getattr(traj_mod, _TRAJ_FUNC_MAP.get(elem.traj_type, "launch_trajectory"), None)
		if func:
			kwargs = {
				"x0": pos.x, "y0": pos.y, "z0": pos.z,
				"x1": end.x, "y1": end.y, "z1": end.z,
				"start_color": color.start.as_tuple(),
				"end_color": color.end.as_tuple() if color.use_gradient else color.start.as_tuple(),
				"duration": elem.traj_duration_ticks / 20,
				"k": elem.k, "m0": elem.m0,
				"lifetime": elem.traj_duration_ticks / 20,
			}
			if elem.traj_type == "launch":
				kwargs["rho"] = elem.rho
			elif elem.traj_type in ("spark",):
				kwargs["particle_count"] = 1
			func(elem.start_tick, **kwargs)

		# 烟花部分
		fw_func = getattr(fw_mod, _FW_FUNC_MAP.get(elem.fw_type, "basic_single_layer_firework"), None)
		if fw_func:
			fw_kwargs = {
				"tick": elem.fw_start_tick,
				"x": end.x, "y": end.y, "z": end.z,
				"duration": elem.fw_duration_ticks / 20,
				"lifetime": elem.fw_duration_ticks / 20,
				"horizontal_angle_step": elem.horizontal_angle,
				"vertical_angle_step": elem.vertical_angle,
			}
			self._fill_fw_kwargs(elem, fw_kwargs)
			fw_func(**fw_kwargs)

	@staticmethod
	def _fill_fw_kwargs(elem, kwargs: dict) -> None:
		"""填充烟花导出参数."""
		if elem.fw_type == "single_layer":
			kwargs["start_color"] = elem.inner_color.start.as_tuple()
			kwargs["end_color"] = elem.inner_color.start.as_tuple()
			kwargs["speed"] = elem.speed
		elif elem.fw_type == "double_layer":
			kwargs["inner_start_color"] = elem.inner_color.start.as_tuple()
			kwargs["inner_end_color"] = elem.inner_color.start.as_tuple()
			kwargs["outer_start_color"] = elem.outer_color.start.as_tuple()
			kwargs["outer_end_color"] = elem.outer_color.start.as_tuple()
			kwargs["inner_speed"] = elem.inner_speed
			kwargs["outer_speed"] = elem.outer_speed
		elif elem.fw_type in ("directional", "clustered"):
			kwargs["start_color"] = elem.inner_color.start.as_tuple()
			kwargs["end_color"] = elem.inner_color.start.as_tuple()
			kwargs["speed"] = elem.speed
			kwargs["spread_angle"] = elem.spread_angle
			kwargs["track_count"] = elem.track_count
			if elem.fw_type == "directional":
				kwargs["direction_horizontal_angle"] = elem.horizontal_angle
				kwargs["direction_vertical_angle"] = elem.vertical_angle
		elif elem.fw_type == "expanding_sphere":
			kwargs["start_color"] = elem.inner_color.start.as_tuple()
			kwargs["end_color"] = elem.inner_color.start.as_tuple()
			kwargs["radius"] = getattr(elem, 'radius', 5.0) if hasattr(elem, 'radius') else 5.0
			kwargs["particle_count"] = elem.track_count
			kwargs["radial_speed"] = getattr(elem, 'radial_speed', 3.0) if hasattr(elem, 'radial_speed') else 3.0

	def _export_trajectory(self, elem: TrajectoryElement, traj) -> None:
		func = getattr(traj, _TRAJ_FUNC_MAP.get(elem.traj_type, "launch_trajectory"), None)
		if func is None:
			return

		pos = elem.start_position
		end = elem.end_position
		color = elem.traj_color

		kwargs = {
			"x0": pos.x, "y0": pos.y, "z0": pos.z,
			"x1": end.x, "y1": end.y, "z1": end.z,
			"start_color": color.start.as_tuple(),
			"end_color": color.end.as_tuple() if color.use_gradient else color.start.as_tuple(),
			"duration": elem.duration_ticks / 20,
			"k": elem.k, "m0": elem.m0,
			"lifetime": elem.duration_ticks / 20,
		}

		if elem.traj_type == "launch":
			kwargs["rho"] = elem.rho
		elif elem.traj_type in ("spark",):
			kwargs["particle_count"] = elem.particle_count
		elif elem.traj_type in ("offset", "thick", "expanding"):
			kwargs["interval_ticks"] = elem.interval_ticks
			kwargs["points_per_tick"] = elem.points_per_tick
			if elem.traj_type in ("thick", "expanding"):
				kwargs["range_x"] = elem.range_x
				kwargs["range_y"] = elem.range_y
				kwargs["range_z"] = elem.range_z
				kwargs["particle_count"] = elem.particle_count
			if elem.traj_type == "expanding":
				kwargs["speed_factor"] = elem.speed_factor

		func(elem.start_tick, **kwargs)

	def _export_firework(self, elem: FireworkElement, fw) -> None:
		func = getattr(fw, _FW_FUNC_MAP.get(elem.fw_type, "basic_single_layer_firework"), None)
		if func is None:
			return

		pos = elem.position
		kwargs: dict = {
			"tick": elem.start_tick,
			"x": pos.x, "y": pos.y, "z": pos.z,
			"duration": elem.duration_ticks / 20,
			"lifetime": elem.duration_ticks / 20,
			"horizontal_angle_step": elem.horizontal_angle,
			"vertical_angle_step": elem.vertical_angle,
		}

		if elem.fw_type == "single_layer":
			kwargs["start_color"] = elem.inner_color.start.as_tuple()
			kwargs["end_color"] = (
				elem.inner_color.end.as_tuple()
				if elem.inner_color.use_gradient
				else elem.inner_color.start.as_tuple()
			)
			kwargs["speed"] = elem.speed
		elif elem.fw_type == "double_layer":
			kwargs["inner_start_color"] = elem.inner_color.start.as_tuple()
			kwargs["inner_end_color"] = (
				elem.inner_color.end.as_tuple()
				if elem.inner_color.use_gradient
				else elem.inner_color.start.as_tuple()
			)
			kwargs["outer_start_color"] = elem.outer_color.start.as_tuple()
			kwargs["outer_end_color"] = (
				elem.outer_color.end.as_tuple()
				if elem.outer_color.use_gradient
				else elem.outer_color.start.as_tuple()
			)
			kwargs["inner_speed"] = elem.inner_speed
			kwargs["outer_speed"] = elem.outer_speed
		elif elem.fw_type in ("directional", "clustered"):
			kwargs["start_color"] = elem.inner_color.start.as_tuple()
			kwargs["end_color"] = (
				elem.inner_color.end.as_tuple()
				if elem.inner_color.use_gradient
				else elem.inner_color.start.as_tuple()
			)
			kwargs["speed"] = elem.speed
			kwargs["spread_angle"] = elem.spread_angle
			kwargs["track_count"] = elem.track_count
			if elem.fw_type == "directional":
				kwargs["direction_horizontal_angle"] = elem.horizontal_angle
				kwargs["direction_vertical_angle"] = elem.vertical_angle
		elif elem.fw_type == "expanding_sphere":
			kwargs["start_color"] = elem.inner_color.start.as_tuple()
			kwargs["end_color"] = (
				elem.inner_color.end.as_tuple()
				if elem.inner_color.use_gradient
				else elem.inner_color.start.as_tuple()
			)
			kwargs["radius"] = elem.radius
			kwargs["particle_count"] = elem.track_count
			kwargs["radial_speed"] = elem.radial_speed

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
