"""DynFirework 主窗口."""
from __future__ import annotations

import re
import sys
from pathlib import Path

from dyn.logging_config import setup_logging, get_logger

log = get_logger(__name__)

from PySide6.QtCore import QItemSelectionModel, Qt, Slot, QSettings
from PySide6.QtGui import QAction, QColor, QKeySequence
from PySide6.QtWidgets import (
	QApplication, QMainWindow, QWidget, QVBoxLayout, QSplitter, QTreeView, QFrame, QFileDialog, QMessageBox,
	QMenu, QLabel, QDialog, QScrollArea,
)

from dyn.lib.units import MinecraftPosition
from dyn.models.df.base import ElementCategory
from dyn.models.df.composites import CompositeElement
from dyn.models import Project

from dyn.service.audio_service import load_waveform, load_waveform_from_bytes
from dyn.service.element_controller import ElementController, CATEGORY_DISPLAY
from dyn.service.export_service import ExportService
from dyn.service.playback_controller import PlaybackController
from dyn.service.project_manager import ProjectManager
from dyn.service.undo_manager import UndoManager

from dyn.components.element_browser import ElementBrowserModel, ProxyNode
from dyn.components.inspector import Inspector
from dyn.components.property_panel import PropertyPanel
from dyn.components.df.timeline import DFTimelineWidget
from dyn.components.df.timeline.theme import TICKS_PER_SECOND
from dyn.components.transport_bar import TransportBar
from dyn.components.pos_select.select_center import PosSelectMainWindow

from dyn.actions.about import DYNAboutWindow, DYNHelpWindow
from dyn.ui.dialogs.export_dialog import ExportDialog
from dyn.ui.dialogs.project_settings_dialog import ProjectSettingsDialog

_CATEGORY_ICONS: dict[ElementCategory, str] = {
	ElementCategory.FIREWORK: "*",
	ElementCategory.TRAJECTORY: "/",
	ElementCategory.EFFECT: "-",
	ElementCategory.COMPOSITE: "+",
}

class MainWin(QMainWindow):
	"""DynFirework 主窗口 V2."""

	def __init__(self) -> None:
		super().__init__()
		log.debug("MainWin 初始化开始")
		self.setWindowTitle("DynFirework   Minecraft 烟花设计工具")
		self.resize(1600, 900)

		# 服务层
		self._controller = ElementController(self)
		self._project_manager = ProjectManager(self)
		self._undo_manager = UndoManager(self._controller, self)
		self._export_service = ExportService(self)
		self._playback = PlaybackController(self)

		# UI 组件
		self._element_browser_model = ElementBrowserModel(self)
		self._element_browser_model.set_controller(self._controller)

		self._timeline = DFTimelineWidget()
		self._timeline.set_controller(self._controller)

		self._property_panel = PropertyPanel(self._controller)

		self._inspector = Inspector()

		self._transport_bar = TransportBar(self._playback)

		self._pos_selector = PosSelectMainWindow()
		self._syncing_tree: bool = False

		# 构建 UI
		self._setup_menu()
		self._setup_layout()
		self._setup_statusbar()
		self._connect_signals()
		self._setup_shortcuts()

		# 恢复上次会话
		self._restore_window_state()

	# 菜单栏

	def _setup_menu(self) -> None:
		mb = self.menuBar()

		# 文件
		file_menu = mb.addMenu("文件(&F)")

		act = QAction("新建项目(&N)", self)
		act.setShortcut(QKeySequence.New)
		act.triggered.connect(self._on_new_project)
		file_menu.addAction(act)

		act = QAction("打开项目(&O)", self)
		act.setShortcut(QKeySequence.Open)
		act.triggered.connect(self._on_open_project)
		file_menu.addAction(act)

		file_menu.addSeparator()

		act = QAction("保存(&S)", self)
		act.setShortcut(QKeySequence.Save)
		act.triggered.connect(self._on_save_project)
		file_menu.addAction(act)

		act = QAction("另存为...", self)
		act.setShortcut(QKeySequence.SaveAs)
		act.triggered.connect(self._on_save_as_project)
		file_menu.addAction(act)

		file_menu.addSeparator()

		act = QAction("导入音乐...", self)
		act.triggered.connect(self._on_import_music)
		file_menu.addAction(act)

		file_menu.addSeparator()

		act = QAction("导出数据包...", self)
		act.setShortcut(QKeySequence("Ctrl+E"))
		act.triggered.connect(self._on_export_datapack)
		file_menu.addAction(act)

		file_menu.addSeparator()

		act = QAction("退出(&Q)", self)
		act.setShortcut(QKeySequence.Quit)
		act.triggered.connect(self.close)
		file_menu.addAction(act)

		# 编辑
		edit_menu = mb.addMenu("编辑(&E)")

		new_menu = edit_menu.addMenu("新建元素")
		for cat in ElementCategory:
			icon = _CATEGORY_ICONS.get(cat, "")
			label = CATEGORY_DISPLAY.get(cat, cat.value)
			act = QAction(f"{icon} 新建{label}", self)
			act.triggered.connect(lambda checked, c=cat: self._on_new_element(c))
			new_menu.addAction(act)

		edit_menu.addSeparator()

		undo_act = QAction("撤销(&U)", self)
		undo_act.setShortcut(QKeySequence.Undo)
		undo_act.triggered.connect(self._undo_manager.undo)
		self._undo_manager.can_undo_changed.connect(undo_act.setEnabled)
		self._undo_manager.undo_text_changed.connect(
			lambda t, a=undo_act: a.setText(f"撤销 {t}" if t else "撤销(&U)")
		)
		edit_menu.addAction(undo_act)

		redo_act = QAction("重做(&R)", self)
		redo_act.setShortcut(QKeySequence("Ctrl+Shift+Z"))
		redo_act.triggered.connect(self._undo_manager.redo)
		self._undo_manager.can_redo_changed.connect(redo_act.setEnabled)
		self._undo_manager.redo_text_changed.connect(
			lambda t, a=redo_act: a.setText(f"重做 {t}" if t else "重做(&R)")
		)
		edit_menu.addAction(redo_act)

		edit_menu.addSeparator()

		act = QAction("复制元素(&C)", self)
		act.setShortcut(QKeySequence.Copy)
		act.triggered.connect(self._on_clone_element)
		edit_menu.addAction(act)

		act = QAction("删除元素(&D)", self)
		act.setShortcut(QKeySequence.Delete)
		act.triggered.connect(self._on_delete_selected)
		edit_menu.addAction(act)

		# 视图
		view_menu = mb.addMenu("视图(&V)")

		act = QAction("位置选择器(&P)", self)
		act.triggered.connect(self._pos_selector.showNormal)
		view_menu.addAction(act)

		# 项目
		proj_menu = mb.addMenu("项目(&P)")

		act = QAction("项目设置...", self)
		act.triggered.connect(self._on_project_settings)
		proj_menu.addAction(act)

		# 关于
		help_menu = mb.addMenu("关于(&H)")

		act = QAction("关于 DynFirework(&A)", self)
		act.triggered.connect(lambda: DYNAboutWindow().exec())
		help_menu.addAction(act)

		act = QAction("帮助(&H)", self)
		act.setShortcut(QKeySequence(Qt.Key_F1))
		act.triggered.connect(lambda: DYNHelpWindow().exec())
		help_menu.addAction(act)

	# 布局

	def _setup_layout(self) -> None:
		central = QWidget()
		self.setCentralWidget(central)
		root_layout = QVBoxLayout(central)
		root_layout.setContentsMargins(0, 0, 0, 0)
		root_layout.setSpacing(0)

		main_splitter = QSplitter(Qt.Vertical)
		root_layout.addWidget(main_splitter, stretch=1)

		top_splitter = QSplitter(Qt.Horizontal)

		# 左: 元素列表
		left_frame = QFrame()
		left_layout = QVBoxLayout(left_frame)
		left_layout.setContentsMargins(4, 4, 4, 4)
		left_layout.addWidget(QLabel("元素列表"))
		self._tree_view = QTreeView()
		self._tree_view.setModel(self._element_browser_model)
		self._tree_view.setHeaderHidden(False)
		self._tree_view.setAnimated(True)
		self._tree_view.setExpandsOnDoubleClick(False)
		self._tree_view.expandAll()
		self._tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
		self._tree_view.customContextMenuRequested.connect(self._on_tree_context_menu)
		left_layout.addWidget(self._tree_view)
		top_splitter.addWidget(left_frame)

		# 中: 参数面板
		top_splitter.addWidget(self._property_panel)

		# 右: 检查器
		right_frame = QFrame()
		right_layout = QVBoxLayout(right_frame)
		right_layout.setContentsMargins(4, 4, 4, 4)
		right_layout.addWidget(self._inspector)
		top_splitter.addWidget(right_frame)
		top_splitter.setSizes([220, 480, 280])

		main_splitter.addWidget(top_splitter)

		# 下部: 传输条 + 时间线
		bottom_widget = QWidget()
		bottom_layout = QVBoxLayout(bottom_widget)
		bottom_layout.setContentsMargins(0, 0, 0, 0)
		bottom_layout.setSpacing(0)

		bottom_layout.addWidget(self._transport_bar)

		scroll = QScrollArea()
		scroll.setWidgetResizable(True)
		scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
		scroll.setWidget(self._timeline)
		bottom_layout.addWidget(scroll, stretch=1)

		main_splitter.addWidget(bottom_widget)
		main_splitter.setSizes([450, 250])

	def _setup_statusbar(self) -> None:
		self._status_label = QLabel("就绪")
		self.statusBar().addWidget(self._status_label)
		self.statusBar().showMessage("就绪", 5000)

	# 信号连接

	def _connect_signals(self) -> None:
		self._tree_view.selectionModel().selectionChanged.connect(
			self._on_tree_selection_changed
		)

		self._element_browser_model.selection_changed.connect(
			self._controller.select_element
		)

		# 时间线选中
		# (去重) 时间线选中直连 track 级别
		all_tracks = [
			self._timeline.fw_track, self._timeline.traj_track,
			self._timeline.effect_track, self._timeline.composite_track,
		]
		for track in all_tracks:
			track.element_selected.connect(self._on_timeline_select)
			track.element_moved.connect(self._on_timeline_element_moved)
			track.element_resized.connect(self._on_timeline_element_resized)
			track.drag_undo_begin.connect(
				lambda: self._undo_manager.begin_macro("拖拽修改"))
			track.drag_undo_end.connect(self._undo_manager.end_macro)

		self._controller.selection_changed.connect(self._on_controller_selection)
		self._controller.element_added.connect(self._on_element_count_changed)
		self._controller.element_removed.connect(self._on_element_count_changed)

		self._property_panel.property_changed.connect(self._on_property_changed)
		self._property_panel.element_name_changed.connect(
			lambda eid, name: self._controller.set_property(eid, "name", name)
		)
		self._property_panel.position_select_requested.connect(
			self._on_position_select_requested
		)

		# (去重) timeline element_moved 由 track 级别直连处理
		# (去重) timeline element_resized 由 track 级别直连处理

		# 播放控制 tick <-> second 转换
		self._playback.position_changed.connect(self._on_playback_position)
		self._timeline.playback_cursor_changed.connect(self._on_timeline_cursor)

		self._pos_selector.send_chosen_point.connect(self._on_position_chosen)

		self._export_service.export_finished.connect(self._on_export_finished)
		self._export_service.export_progress.connect(
			lambda p: self.statusBar().showMessage(f"导出中... {p}%")
		)

		self._project_manager.project_opened.connect(self._on_project_opened)

	# 快捷键

	def _setup_shortcuts(self) -> None:
		space_action = QAction(self)
		space_action.setShortcut(QKeySequence("Space"))
		space_action.triggered.connect(self._playback.toggle_play_pause)
		self.addAction(space_action)

	# 槽: 文件操作

	def _on_new_project(self) -> None:
		log.debug("新建项目")
		if self._project_manager.is_modified:
			reply = QMessageBox.question(
				self, "新建项目", "当前项目未保存，是否继续？",
				QMessageBox.Yes | QMessageBox.No,
			)
			if reply == QMessageBox.No:
				return
		proj = self._project_manager.new_project()
		self._controller.load_from_project(proj)
		self._element_browser_model.load_elements([])
		self._undo_manager.clear()
		self._playback.stop()
		self.statusBar().showMessage("已创建新项目")

	def _on_open_project(self) -> None:
		path, _ = QFileDialog.getOpenFileName(
			self, "打开项目", "", "DynFirework 项目 (*.dyn);;所有文件 (*.*)"
		)
		if not path:
			return
		try:
			log.debug(f"打开项目: {path}");
			proj = self._project_manager.open_project(path)
			self._playback.stop()
			self._controller.load_from_project(proj)
			self._element_browser_model.load_elements(self._controller.all_elements)
			self._undo_manager.clear()
			if proj.has_music:
				music_path = self._project_manager.get_music_temp_path()
				if music_path:
					self._playback.load_music(music_path)
					self._playback.set_bpm(proj.bpm)
					self._load_waveform(music_path)
					self._transport_bar.set_music_path(proj.music_original_name)
			self._timeline.on_elements_changed()
			self._tree_view.expandAll()
			self.statusBar().showMessage(f"已打开: {path}")
		except Exception as e:
			log.error(f"打开项目失败: {e}", exc_info=True)
			QMessageBox.critical(self, "打开失败", str(e))

	def _sync_positions_to_project(self) -> None:
		pts = self._pos_selector.points
		self._project_manager.project.saved_positions = [
			{"x": p.x, "y": p.y, "z": p.z, "label": p.label,
			 "color": {"r": p.pix_color.red(), "g": p.pix_color.green(), "b": p.pix_color.blue()}}
			for p in pts
		]

	def _on_save_project(self) -> None:
		self._controller.to_project(self._project_manager.project)
		self._sync_positions_to_project()
		if not self._project_manager.has_file:
			self._on_save_as_project()
			return
		log.debug(f"保存项目: {self._project_manager.file_path}")
		if self._project_manager.save_project():
			self.statusBar().showMessage(f"已保存: {self._project_manager.file_path}")
		else:
			QMessageBox.warning(self, "保存失败", "无法保存项目。")

	def _on_save_as_project(self) -> None:
		path, _ = QFileDialog.getSaveFileName(
			self, "另存为", "untitled.dyn", "DynFirework 项目 (*.dyn)"
		)
		if not path:
			return
		log.debug(f"另存为: {path}")
		self._controller.to_project(self._project_manager.project)
		self._sync_positions_to_project()
		if self._project_manager.save_project(path):
			self.statusBar().showMessage(f"已保存: {path}")
		else:
			QMessageBox.warning(self, "保存失败", "无法保存项目。")

	def _on_import_music(self) -> None:
		path, _ = QFileDialog.getOpenFileName(
			self, "导入音乐", "",
			"音频文件 (*.mp3 *.wav *.ogg *.flac);;所有文件 (*.*)"
		)
		if not path:
			return
		log.debug(f"导入音乐: {path}")
		if not self._project_manager.set_music(path):
			QMessageBox.warning(self, "导入失败", "无法读取音乐文件。")
			return
		self._playback.load_music(path)
		self._load_waveform(path)
		self._transport_bar.set_music_path(Path(path).name)
		self.statusBar().showMessage(f"已导入: {Path(path).name}")

	def _load_waveform(self, path: str) -> None:
		samples, sr = load_waveform(path)
		if samples:
			bpm = self._project_manager.project.bpm
			self._timeline.set_waveform_data(samples, sr, bpm)

	def _load_waveform_from_bytes(self, data: bytes, suffix: str = ".mp3") -> None:
		samples, sr = load_waveform_from_bytes(data, suffix)
		if samples:
			bpm = self._project_manager.project.bpm
			self._timeline.set_waveform_data(samples, sr, bpm)

	def _on_export_datapack(self) -> None:
		elements = self._controller.all_elements
		log.debug(f"导出数据包: {len(elements)} 个元素")
		if not elements:
			QMessageBox.warning(self, "无元素", "请先创建至少一个元素。")
			return

		proj = self._project_manager.project
		dlg = ExportDialog(proj.name, self)
		if dlg.exec() != QDialog.DialogCode.Accepted:
			return

		ns = dlg.namespace
		if not re.match(r'^[a-z0-9_\.]+$', ns):
			QMessageBox.warning(self, "无效命名空间", "命名空间仅限小写字母、数字、下划线和点。")
			return

		output_dir = QFileDialog.getExistingDirectory(self, "选择输出目录")
		if not output_dir:
			return

		log.debug(f"导出数据包: namespace={ns}");
		self._export_service.export_to_datapack(
			elements, output_dir, ns,
			datapack_name=dlg.pack_name, description=dlg.description,
			pack_format=dlg.pack_format, mc_version=proj.mc_version,
		)

	def _on_export_finished(self, success: bool, message: str) -> None:
		if success:
			log.debug(f"导出成功: {message}")
			QMessageBox.information(self, "导出完成", message)
		else:
			log.error(f"导出失败: {message}")
			QMessageBox.critical(self, "导出失败", message)

	# 槽: 编辑操作

	def _on_new_element(self, category: ElementCategory) -> None:
		"""创建 元素."""
		cursor_time = self._timeline.playback_time
		cat_label = CATEGORY_DISPLAY.get(category, category.value)
		count = len(self._controller.get_elements_by_category(category))
		elem = self._controller.create_element(
			category=category,
			name=f"{cat_label} {count}",
			start_time=round(cursor_time, 2),
		)
		log.debug(f"创建元素: category={category.value}, name={elem.name}, id={elem.id}, time={cursor_time:.2f}s")
		self._undo_manager.push_add_element(elem)
		self._tree_view.expandAll()
		self._controller.select_element(elem.id)
		self.statusBar().showMessage(f"已创建: {elem.name}")

	def _on_clone_element(self) -> None:
		eid = self._controller.selected_id
		if not eid:
			return
		cloned = self._controller.clone_element(eid)
		if cloned:
			log.debug(f"复制元素: src={eid} -> new={cloned.id}, name={cloned.name}")
			self._undo_manager.push_add_element(cloned)
			self._tree_view.expandAll()
			self.statusBar().showMessage(f"已复制: {cloned.name}")

	def _on_delete_selected(self) -> None:
		eid = self._controller.selected_id
		if not eid:
			return
		elem = self._controller.get_element(eid)
		log.debug(f"删除元素: id={eid}, name={elem.name if elem else '?'}")
		if elem:
			self._undo_manager.push_remove_element(elem)
		self._tree_view.expandAll()
		self.statusBar().showMessage("已删除")

	# 槽: 选中同步

	def _on_tree_selection_changed(self, selected, deselected) -> None:
		if self._syncing_tree or not selected.indexes():
			return
		idx = selected.indexes()[0]
		node = idx.internalPointer()
		# TF 代理子节点
		if isinstance(node, ProxyNode):
			part = node.data
			parent_node = node.parent
			parent_elem = parent_node.data
			part_id = "traj" if part == "_tf_traj" else "fw"
			self._controller._selected_id = parent_elem.id
			self._controller.selection_changed.emit(parent_elem.id)
			if part_id == "traj":
				self._timeline._selected_id = parent_elem.id
				for t in [self._timeline.fw_track, self._timeline.traj_track,
				          self._timeline.effect_track, self._timeline.composite_track]:
					t.set_selection("")
				self._timeline.traj_track.set_selection(parent_elem.id)
			else:
				proxy_id = parent_elem.id + "::fw"
				self._timeline._selected_id = proxy_id
				for t in [self._timeline.fw_track, self._timeline.traj_track,
				          self._timeline.effect_track, self._timeline.composite_track]:
					t.set_selection("")
				self._timeline.fw_track.set_selection(proxy_id)
			self._property_panel.load_element(parent_elem, part_id)
			return
		elem = self._element_browser_model.get_element_from_index(idx)
		if elem is not None:
			self._controller.select_element(elem.id)
			self._property_panel.load_element(elem, "")
			# CompositeElement 代理选中
			if isinstance(elem, CompositeElement):
				for t in [self._timeline.fw_track, self._timeline.traj_track,
				          self._timeline.effect_track, self._timeline.composite_track]:
					t.set_selection(elem.id)
			elif hasattr(elem, 'traj_type') and hasattr(elem, 'fw_type'):
				# cb TrajFireworkElement
				for t in [self._timeline.fw_track, self._timeline.traj_track,
				          self._timeline.effect_track, self._timeline.composite_track]:
					t.set_selection("")
				self._timeline.fw_track.set_selection(elem.id + "::fw")
				self._timeline.traj_track.set_selection(elem.id)

	@Slot(str)
	def _on_controller_selection(self, element_id: str) -> None:
		elem = self._controller.get_element(element_id)
		if elem:
			cat = elem.category.value if hasattr(elem, 'category') else '?'
			log.debug(f"控制器选中: id={element_id}, name={elem.name}, cat={cat}, time={elem.start_time:.2f}s, dur={elem.duration:.2f}s")
		else:
			log.debug(f"控制器选中: id={element_id} (未找到)")
		self._property_panel.load_element(elem)
		self._inspector.show_element(elem)

		self._syncing_tree = True
		try:
			sel = self._tree_view.selectionModel()
			model_idx = self._element_browser_model.get_index_for_element(element_id)
			if model_idx.isValid():
				sel.select(model_idx, QItemSelectionModel.SelectionFlag.ClearAndSelect | QItemSelectionModel.SelectionFlag.Rows)
			else:
				sel.clearSelection()
		finally:
			self._syncing_tree = False

		if elem:
			self._status_label.setText(f"已选中: {elem.name} ({elem.start_time:.2f}s)")
		else:
			self._status_label.setText("未选中")

	def _on_element_count_changed(self, *args) -> None:
		count = len(self._controller.all_elements)
		log.debug(f"元素数量变更: {count}")
		self.statusBar().showMessage(f"共 {count} 个元素", 3000)

	def _on_tree_context_menu(self, pos) -> None:
		menu = QMenu(self)
		idx = self._tree_view.indexAt(pos)
		elem = self._element_browser_model.get_element_from_index(idx) if idx.isValid() else None

		new_menu = menu.addMenu("新建元素")
		for cat in ElementCategory:
			icon = _CATEGORY_ICONS.get(cat, "")
			label = CATEGORY_DISPLAY.get(cat, cat.value)
			act = new_menu.addAction(f"{icon} {label}")
			act.triggered.connect(lambda checked, c=cat: self._on_new_element(c))

		if elem is not None:
			menu.addSeparator()
			act_clone = menu.addAction("复制元素")
			act_clone.triggered.connect(self._on_clone_element)
			act_del = menu.addAction("删除元素")
			act_del.triggered.connect(self._on_delete_selected)

		menu.exec(self._tree_view.viewport().mapToGlobal(pos))

	# 槽: 时间线拖拽

	def _on_timeline_select(self, element_id: str) -> None:
		"""时间线选中 代理元素只高亮自身，面板加载父元素."""
		log.debug(f"时间线选中: id={element_id}")
		if not element_id:
			self._controller.clear_selection()
			return
		real_id, part = ElementController.resolve_proxy_id(element_id)
		parent = self._controller.get_element(real_id)
		if part:
			self._timeline._selected_id = element_id
			for track in [self._timeline.fw_track, self._timeline.traj_track,
			              self._timeline.effect_track, self._timeline.composite_track]:
				track.set_selection(element_id)
			if parent:
				self._property_panel.load_element(parent)
				self._inspector.show_element(parent)
				if hasattr(parent, 'start_time'):
					self._status_label.setText(f"已选中: {parent.name} ({parent.start_time:.2f}s)")
			return
		self._controller.select_element(element_id)

	def _on_timeline_element_moved(self, element_id: str, new_time: float, old_time: float) -> None:
		real_id, part = ElementController.resolve_proxy_id(element_id)
		elem = self._controller.get_element(real_id)
		log.debug(f"时间线移动: {element_id} time={new_time:.2f}s old={old_time:.2f}s | real_id={real_id} elem={elem is not None}")
		if elem:
			key = "start_time"
			self._undo_manager.push_property_change(real_id, key, old_time, new_time)
			self._controller.element_changed.emit(real_id, "drag", None)
			self._property_panel.load_element(elem)
			self._inspector.refresh(elem)
			self._project_manager.mark_modified()
		else:
			log.warning(f"时间线移动: 元素未找到 real_id={real_id}, element_id={element_id}")

	def _on_timeline_element_resized(self, element_id: str, new_dur: float, old_dur: float) -> None:
		real_id, part = ElementController.resolve_proxy_id(element_id)
		elem = self._controller.get_element(real_id)
		log.debug(f"时间线缩放: {element_id} dur={new_dur:.2f}s old={old_dur:.2f}s | real_id={real_id} part={part} elem={elem is not None}")
		if elem:
			key = "duration"
			self._undo_manager.push_property_change(real_id, key, old_dur, new_dur)
			self._controller.element_changed.emit(real_id, "drag", None)
			self._property_panel.load_element(elem)
			self._inspector.refresh(elem)
			self._project_manager.mark_modified()
		else:
			log.warning(f"时间线缩放: 元素未找到 real_id={real_id}, element_id={element_id}")

	def _on_playback_position(self, tick: int) -> None:
		self._timeline.set_playback_time(tick / TICKS_PER_SECOND)

	def _on_timeline_cursor(self, time_sec: float) -> None:
		self._playback.seek_to_tick(int(time_sec * TICKS_PER_SECOND))

	# 槽: 属性变更

	def _on_property_changed(self, element_id: str, key: str, value: object, old_value: object = None) -> None:
		log.debug(f"属性变更: id={element_id}, {key}={value} (old={old_value})")
		elem = self._controller.get_element(element_id)
		if elem is None:
			return
		is_complex = self._controller.apply_property_change(element_id, key, value, old_value)
		if not is_complex:
			self._undo_manager.push_property_change(element_id, key, old_value, value)
		self._inspector.refresh(elem)
		self._project_manager.mark_modified()

	# 槽: 位置选择

	def _on_position_select_requested(self, which: str) -> None:
		log.debug(f"位置选择请求: target={which}")
		self._pending_position_target = which
		self._pos_selector.showNormal()

	def _on_position_chosen(self, point: MinecraftPosition) -> None:
		log.debug(f"位置已选择: ({point.x}, {point.y}, {point.z}), target={getattr(self, '_pending_position_target', 'position')}")
		which = getattr(self, '_pending_position_target', 'position')
		eid = self._controller.selected_id
		if not eid or not self._controller.set_position(eid, which, point.x, point.y, point.z):
			return
		elem = self._controller.selected_element
		self._property_panel.load_element(elem)
		self._inspector.refresh(elem)
		self._project_manager.mark_modified()

	# 槽: 项目操作

	def _on_project_opened(self, project: Project) -> None:
		log.debug(f"项目已打开: name={project.name}, elements={len(project.all_elements)}, bpm={project.bpm:.0f}")
		self._element_browser_model.load_elements(self._controller.all_elements)
		self._tree_view.expandAll()
		self._timeline.on_elements_changed()
		try:
			saved = project.saved_positions
			if saved:
				pts = []
				for p in saved:
					c = p.get("color", {})
					pts.append(MinecraftPosition(
						x=float(p["x"]), y=float(p["y"]), z=float(p["z"]),
						label=str(p.get("label", "")),
						main_color=QColor(c.get("r", 255), c.get("g", 255), c.get("b", 255)),
					))
				self._pos_selector.points.clear()
				self._pos_selector.points.extend(pts)
				self._pos_selector.fastsearch.clear()
				self._pos_selector.fastsearch.update((int(pt.x), int(pt.z)) for pt in pts)
				self._pos_selector.pix_element_list.get_element_list(self._pos_selector.points)
		except Exception as e:
			log.warning(f"恢复位置点失败: {e}")

	def _on_project_settings(self) -> None:
		proj = self._project_manager.project
		dlg = ProjectSettingsDialog(proj.name, proj.bpm, proj.mc_version, self)
		if dlg.exec() == QDialog.DialogCode.Accepted:
			proj.bpm = dlg.bpm
			proj.name = dlg.project_name
			proj.mc_version = dlg.mc_version
			self._playback.set_bpm(proj.bpm)
			self._transport_bar.set_bpm(proj.bpm)
			self._project_manager.mark_modified()
			log.debug(f"项目设置更新: name={proj.name}, bpm={proj.bpm:.0f}, mc_version={proj.mc_version}")
			self.setWindowTitle(f"DynFirework   {proj.name}")
			self.statusBar().showMessage(f"BPM: {proj.bpm:.0f} | MC {proj.mc_version} | {proj.name}")

	# 窗口状态

	def _restore_window_state(self) -> None:
		settings = QSettings("DynFirework", "dyn-gui")
		geo = settings.value("mainwin/geometry")
		if geo:
			self.restoreGeometry(geo)
		state = settings.value("mainwin/state")
		if state:
			self.restoreState(state)

	def closeEvent(self, event) -> None:
		if self._project_manager.is_modified:
			reply = QMessageBox.question(
				self, "未保存的更改",
				"当前项目有未保存的更改，是否保存？",
				QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
			)
			if reply == QMessageBox.Save:
				log.debug("关闭窗口: 用户选择保存")
				self._on_save_project()
				if self._project_manager.is_modified:
					log.warning("关闭窗口: 保存失败，取消关闭")
					event.ignore()
					return
			elif reply == QMessageBox.Cancel:
				log.debug("关闭窗口: 用户取消")
				event.ignore()
				return
			else:
				log.debug("关闭窗口: 用户选择不保存")

		settings = QSettings("DynFirework", "dyn-gui")
		settings.setValue("mainwin/geometry", self.saveGeometry())
		settings.setValue("mainwin/state", self.saveState())
		log.debug("应用程序关闭");
		super().closeEvent(event)

if __name__ == "__main__":
	setup_logging()
	log.debug("DynFirework 启动")
	app = QApplication(sys.argv)
	app.setApplicationName("DynFirework")
	app.setOrganizationName("DynFirework")
	win = MainWin()
	win.show()
	sys.exit(app.exec())
