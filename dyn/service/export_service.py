"""导出服务 将项目元素生成为 Minecraft 数据包.
V2: 使用 EXPORT_DISPATCH + df_backend，移除 backend_registry 依赖.
"""
from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QObject, Signal
from PySide6.QtCore import QRunnable, QThreadPool

from dyn.lib import global_storage, export_mcfunction
from dyn.lib.export_helpers import export_element
from dyn.logging_config import get_logger

log = get_logger(__name__)

from dyn.models.df.base import Element as DfElement

class _TaskSignals(QObject):
	finished = Signal(bool, str)
	progress = Signal(int)

class _ExportTask(QRunnable):

	def __init__(self, elements: list[DfElement], output_dir: str, namespace: str,
	             datapack_name: str = "DynFirework", description: str = "",
	             pack_format: int = 48, mc_version: str = "1.21.8") -> None:
		super().__init__()
		self._elements = elements
		self._output_dir = output_dir
		self._namespace = namespace
		self._datapack_name = datapack_name
		self._description = description
		self._pack_format = pack_format
		self._mc_version = mc_version
		self.signals = _TaskSignals()

	@property
	def elements(self):
		return self._elements

	def run(self) -> None:
		try:
			log.debug(f"导出开始: {self._output_dir}, namespace={self._namespace}, elements={len(self._elements)}")
			self._do_export()
			self.signals.finished.emit(True, f"导出完成: {self._output_dir}")
		except Exception as e:
			log.exception("导出失败")
			self.signals.finished.emit(False, f"导出失败: {e}")

	def _do_export(self) -> None:
		global_storage.commands_by_tick.clear()
		global_storage.MAX_TICK = 0

		total = len(self._elements)
		for i, elem in enumerate(self._elements):
			if not elem.enabled:
				continue
			export_element(elem)
			self.signals.progress.emit(int((i + 1) / total * 100))

		cmd_count = sum(len(v) for v in global_storage.commands_by_tick.values())
		log.debug(f"命令生成完成: {cmd_count} 条命令, MAX_TICK={global_storage.MAX_TICK}")

		pack_dir = Path(self._output_dir) / self._datapack_name
		export_mcfunction.write_pack_mcmeta(str(pack_dir), self._pack_format, self._description)

		func_dir = pack_dir / "data" / self._namespace / "functions"
		func_dir.mkdir(parents=True, exist_ok=True)

		export_mcfunction.export_mcfunction(str(func_dir), self._namespace)
		export_mcfunction.generate_auto_exec_file(str(func_dir), self._namespace)

class ExportService(QObject):
	export_finished = Signal(bool, str)
	export_progress = Signal(int)

	def __init__(self, parent: QObject | None = None) -> None:
		super().__init__(parent)

	def export_to_datapack(
			self,
			elements: list[DfElement],
			output_dir: str,
			namespace: str = "fireworks1",
			datapack_name: str = "DynFirework",
			description: str = "",
			pack_format: int = 48,
			mc_version: str = "1.21.8",
	) -> None:
		task = _ExportTask(elements, output_dir, namespace,
		                   datapack_name, description, pack_format, mc_version)
		task.signals.finished.connect(self.export_finished)
		task.signals.progress.connect(self.export_progress)
		QThreadPool.globalInstance().start(task)
