"""DynFirework 主窗口."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

from dyn.logging_config import setup_logging, get_logger

log = get_logger(__name__)

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QTreeView, QFrame, QFileDialog, QMessageBox,
    QMenu, QLabel, QDoubleSpinBox, QLineEdit, QDialog, QFormLayout,
    QDialogButtonBox, QScrollArea, QSpinBox,
)
from PySide6.QtCore import Qt, Signal, Slot, QSettings
from PySide6.QtGui import QAction, QKeySequence

from dyn.models.elements import Element, TrajectoryElement, FireworkElement, TrajFireworkElement
from dyn.models.timeline import Project
from dyn.lib.units import MinecraftPosition

from dyn.service.element_controller import ElementController
from dyn.service.project_manager import ProjectManager
from dyn.service.undo_manager import UndoManager
from dyn.service.export_service import ExportService
from dyn.service.playback_controller import PlaybackController

from dyn.components.element_browser import ElementBrowserModel
from dyn.components.timeline.timeline_widget import TimelineWidget
from dyn.components.property_panel import PropertyPanel
from dyn.components.inspector import Inspector
from dyn.components.transport_bar import TransportBar
from dyn.components.pos_select.pos_select_main import PosSelectMainWindow

from dyn.actions.about import DYNAboutWindow, DYNHelpWindow


class MainWin(QMainWindow):
    """DynFirework 主窗口."""

    def __init__(self) -> None:
        super().__init__()
        log.info("MainWin 初始化开始")
        self.setWindowTitle("DynFirework — Minecraft 烟花设计工具")
        self.resize(1600, 900)

        # ── 服务层 ──────────────────────────────────
        self._controller = ElementController(self)
        self._project_manager = ProjectManager(self)
        self._undo_manager = UndoManager(self._controller, self)
        self._export_service = ExportService(self)
        self._playback = PlaybackController(self)

        # ── UI 组件 ─────────────────────────────────
        self._element_browser_model = ElementBrowserModel(self)
        self._element_browser_model.set_controller(self._controller)

        self._timeline = TimelineWidget()
        self._timeline.set_controller(self._controller)

        self._property_panel = PropertyPanel(self._controller)

        self._inspector = Inspector()

        self._transport_bar = TransportBar(self._playback)

        self._pos_selector = PosSelectMainWindow()
        self._syncing_tree: bool = False

        # ── 构建 UI ─────────────────────────────────
        self._setup_menu()
        self._setup_layout()
        self._setup_statusbar()
        self._connect_signals()
        self._setup_shortcuts()

        # ── 恢复上次会话 ────────────────────────────
        self._restore_window_state()

    # ═══════════════════════════════════════════════════
    # 菜单栏
    # ═══════════════════════════════════════════════════

    def _setup_menu(self) -> None:
        mb = self.menuBar()

        # ── 文件 ────────────────────────────────────
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

        # ── 编辑 ────────────────────────────────────
        edit_menu = mb.addMenu("编辑(&E)")

        act = QAction("新建轨迹(&T)", self)
        act.setShortcut(QKeySequence("Ctrl+Shift+T"))
        act.triggered.connect(lambda: self._on_new_element("trajectory"))
        edit_menu.addAction(act)

        act = QAction("新建烟花(&F)", self)
        act.setShortcut(QKeySequence("Ctrl+Shift+F"))
        act.triggered.connect(lambda: self._on_new_element("firework"))
        edit_menu.addAction(act)

        act = QAction("新建轨迹烟花", self)
        act.setShortcut(QKeySequence("Ctrl+Shift+G"))
        act.triggered.connect(lambda: self._on_new_element("traj_firework"))
        edit_menu.addAction(act)

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

        # ── 视图 ────────────────────────────────────
        view_menu = mb.addMenu("视图(&V)")

        act = QAction("位置选择器(&P)", self)
        act.triggered.connect(self._pos_selector.showNormal)
        view_menu.addAction(act)

        # ── 项目 ────────────────────────────────────
        proj_menu = mb.addMenu("项目(&P)")

        act = QAction("项目设置...", self)
        act.triggered.connect(self._on_project_settings)
        proj_menu.addAction(act)

        # ── 关于 ────────────────────────────────────
        help_menu = mb.addMenu("关于(&H)")

        act = QAction("关于 DynFirework(&A)", self)
        act.triggered.connect(lambda: DYNAboutWindow().exec())
        help_menu.addAction(act)

        act = QAction("帮助(&H)", self)
        act.setShortcut(QKeySequence(Qt.Key_F1))
        act.triggered.connect(lambda: DYNHelpWindow().exec())
        help_menu.addAction(act)

    # ═══════════════════════════════════════════════════
    # 布局
    # ═══════════════════════════════════════════════════

    def _setup_layout(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ── 面板/时间线纵向分割 ──────────────────────
        main_splitter = QSplitter(Qt.Vertical)
        root_layout.addWidget(main_splitter, stretch=1)

        # ── 上部：水平三栏 ───────────────────────────
        top_splitter = QSplitter(Qt.Horizontal)

        # 左：元素列表
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

        # 中：参数面板
        top_splitter.addWidget(self._property_panel)

        # 右：检查器
        right_frame = QFrame()
        right_layout = QVBoxLayout(right_frame)
        right_layout.setContentsMargins(4, 4, 4, 4)
        right_layout.addWidget(self._inspector)
        top_splitter.addWidget(right_frame)
        top_splitter.setSizes([220, 480, 280])

        main_splitter.addWidget(top_splitter)

        # ── 下部：传输条 + 时间线 ─────────────────────
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

    # ═══════════════════════════════════════════════════
    # 信号连接
    # ═══════════════════════════════════════════════════

    def _connect_signals(self) -> None:
        # 元素列表 TreeView 点击 → 选中
        self._tree_view.selectionModel().selectionChanged.connect(
            self._on_tree_selection_changed
        )

        # 元素浏览器模型 → 同步选中
        self._element_browser_model.selection_changed.connect(
            self._controller.select_element
        )

        # 时间线 → 选中同步（主时间线 + 子轨道）
        self._timeline.element_selected.connect(self._on_timeline_select)
        self._timeline._fw_track.element_selected.connect(self._on_timeline_select)
        self._timeline._traj_track.element_selected.connect(self._on_timeline_select)
        # 子轨道拖拽
        self._timeline._fw_track.element_moved.connect(self._on_timeline_element_moved)
        self._timeline._fw_track.element_resized.connect(self._on_timeline_element_resized)
        self._timeline._traj_track.element_moved.connect(self._on_timeline_element_moved)
        self._timeline._traj_track.element_resized.connect(self._on_timeline_element_resized)

        # 控制器的选中变更 → 各个面板
        self._controller.selection_changed.connect(self._on_controller_selection)
        self._controller.element_added.connect(self._on_element_count_changed)
        self._controller.element_removed.connect(self._on_element_count_changed)

        # 参数面板 → 元素属性修改 (通过 undo)
        self._property_panel.property_changed.connect(self._on_property_changed)
        self._property_panel.element_name_changed.connect(
            lambda eid, name: self._controller.set_property(eid, "name", name)
        )
        self._property_panel.position_select_requested.connect(
            self._on_position_select_requested
        )

        # 时间线拖拽 → 元素修改 + 面板刷新
        self._timeline.element_moved.connect(self._on_timeline_element_moved)
        self._timeline.element_resized.connect(self._on_timeline_element_resized)

        # 播放控制 ↔ 时间线双向同步
        self._playback.position_changed.connect(self._timeline.set_playback_tick)
        self._timeline.playback_cursor_changed.connect(self._playback.seek_to_tick)

        # 位置选择器
        self._pos_selector.send_chosen_point.connect(self._on_position_chosen)

        # 导出
        self._export_service.export_finished.connect(self._on_export_finished)
        self._export_service.export_progress.connect(
            lambda p: self.statusBar().showMessage(f"导出中... {p}%")
        )

        # 项目
        self._project_manager.project_opened.connect(self._on_project_opened)

    # ═══════════════════════════════════════════════════
    # 快捷键
    # ═══════════════════════════════════════════════════

    def _setup_shortcuts(self) -> None:
        space_action = QAction(self)
        space_action.setShortcut(QKeySequence("Space"))
        space_action.triggered.connect(self._playback.toggle_play_pause)
        self.addAction(space_action)

    # ═══════════════════════════════════════════════════
    # 槽：文件操作
    # ═══════════════════════════════════════════════════

    def _on_new_project(self) -> None:
        log.info("新建项目")
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
            log.info(f"打开项目: {path}"); proj = self._project_manager.open_project(path)
            self._controller.load_from_project(proj)
            self._element_browser_model.load_elements(self._controller.all_elements)
            self._undo_manager.clear()
            if proj.music_path and Path(proj.music_path).exists():
                self._playback.load_music(proj.music_path)
                self._playback.set_bpm(proj.bpm)
                self._load_waveform(proj.music_path)
                self._transport_bar.set_music_path(proj.music_path)
            self._timeline._on_elements_changed()
            self._tree_view.expandAll()
            self.statusBar().showMessage(f"已打开: {path}")
        except Exception as e:
            QMessageBox.critical(self, "打开失败", str(e))

    def _sync_positions_to_project(self) -> None:
        """将位置选择器的点同步到项目对象."""
        from dataclasses import asdict
        pts = self._pos_selector._points
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
        log.info("保存项目")
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
        self._controller.to_project(self._project_manager.project)
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
        log.info(f"导入音乐: {path}"); self._project_manager.set_music_path(path)
        self._playback.load_music(path)
        self._load_waveform(path)
        self._transport_bar.set_music_path(path)
        self.statusBar().showMessage(f"已导入: {path}")

    def _load_waveform(self, path: str) -> None:
        from dyn.service.audio_service import load_waveform
        samples, sr = load_waveform(path)
        if samples:
            bpm = self._project_manager.project.bpm
            self._timeline.set_waveform_data(samples, sr, bpm)

    def _on_export_datapack(self) -> None:
        import re
        elements = self._controller.all_elements
        if not elements:
            QMessageBox.warning(self, "无元素", "请先创建至少一个轨迹或烟花元素。")
            return

        from dyn.lib.backend_registry import MC_VERSION_MAP, resolve_mc_version
        proj = self._project_manager.project
        mc_ver = proj.mc_version

        # 推导默认pack_format和后端信息
        try:
            info = resolve_mc_version(mc_ver)
            default_fmt = info.pack_format
            backend_label = info.display_name
        except KeyError:
            default_fmt = 15
            backend_label = f"Minecraft {mc_ver} (未知版本)"

        from dyn.ui.dialogs.export_dialog import ExportDialog
        dlg = ExportDialog(proj.name, self)
        dlg.set_pack_format(default_fmt)
        dlg.set_backend_info(backend_label)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        ns = dlg.namespace
        if not re.match(r'^[a-z0-9_\.]+$', ns):
            QMessageBox.warning(self, "无效命名空间", "命名空间仅限小写字母、数字、下划线和点。")
            return

        output_dir = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if not output_dir:
            return

        log.info(f"导出数据包: namespace={ns}, mc_version={mc_ver}"); self._export_service.export_to_datapack(
            elements, output_dir, ns,
            datapack_name=dlg.pack_name, description=dlg.description,
            pack_format=dlg.pack_format, mc_version=mc_ver,
        )

    def _on_export_finished(self, success: bool, message: str) -> None:
        if success:
            QMessageBox.information(self, "导出完成", message)
        else:
            QMessageBox.critical(self, "导出失败", message)

    # ═══════════════════════════════════════════════════
    # 槽：编辑操作
    # ═══════════════════════════════════════════════════

    def _on_new_element(self, elem_type: str) -> None:
        cursor_tick = self._timeline._playback_tick if hasattr(self._timeline, '_playback_tick') else 0
        # 创建元素但不添加到 controller（由 undo 的 redo 完成添加）
        if elem_type == "trajectory":
            log.debug(f"创建轨迹: {cursor_tick}"); elem = TrajectoryElement(
                name=f"轨迹 {self._controller.trajectory_count}", start_tick=cursor_tick
            )
        elif elem_type == "firework":
            log.debug(f"创建烟花: {cursor_tick}"); elem = FireworkElement(
                name=f"烟花 {self._controller.firework_count}", start_tick=cursor_tick
            )
        else:
            log.debug(f"创建轨迹烟花: {cursor_tick}"); elem = TrajFireworkElement(
                name=f"轨迹烟花 {self._controller.traj_firework_count}", start_tick=cursor_tick
            )
        self._undo_manager.push_add_element(elem)
        self._tree_view.expandAll()
        self._controller.select_element(elem.id)
        self.statusBar().showMessage(f"已创建: {elem.name}")

    def _on_clone_element(self) -> None:
        eid = self._controller.selected_id
        if not eid:
            return
        log.info(f"复制元素: {eid}"); cloned = self._controller.clone_element(eid)
        if cloned:
            self._tree_view.expandAll()
            self.statusBar().showMessage(f"已复制: {cloned.name}")

    def _on_delete_selected(self) -> None:
        eid = self._controller.selected_id
        if not eid:
            return
        elem = self._controller.get_element(eid)
        if elem:
            self._undo_manager.push_remove_element(elem)
        self._tree_view.expandAll()
        self.statusBar().showMessage("已删除")

    # ═══════════════════════════════════════════════════
    # 槽：选中同步
    # ═══════════════════════════════════════════════════

    def _on_tree_selection_changed(self, selected, deselected) -> None:
        if self._syncing_tree or not selected.indexes():
            return
        idx = selected.indexes()[0]
        node = idx.internalPointer()
        # 检查是否为 TF 子节点
        if isinstance(node.data, str) and node.data.startswith("_tf_"):
            part = node.data  # "_tf_traj" or "_tf_fw"
            parent_node = node.parent
            parent_elem = parent_node.data
            part_id = "traj" if part == "_tf_traj" else "fw"
            # 先发信号让控制器/面板加载完整元素，再覆盖为部分
            self._controller._selected_id = parent_elem.id
            self._controller.selection_changed.emit(parent_elem.id)
            # 时间线仅高亮对应代理（另一轨设为空）
            if part_id == "traj":
                proxy_id = parent_elem.id
                self._timeline._selected_id = proxy_id
                self._timeline._fw_track.set_selection("")
                self._timeline._traj_track.set_selection(proxy_id)
            else:
                proxy_id = parent_elem.id + "::fw"
                self._timeline._selected_id = proxy_id
                self._timeline._fw_track.set_selection(proxy_id)
                self._timeline._traj_track.set_selection("")
            # 覆盖面板为部分加载
            self._property_panel.load_element(parent_elem, part_id)
            return
        elem = self._element_browser_model.get_element_from_index(idx)
        if elem is not None:
            self._controller.select_element(elem.id)
            self._property_panel.load_element(elem, "")
            # TF 父节点：高亮两个代理
            if hasattr(elem, 'traj_type') and hasattr(elem, 'fw_type'):
                self._timeline._fw_track.set_selection(elem.id + "::fw")
                self._timeline._traj_track.set_selection(elem.id)

    @Slot(str)
    def _on_controller_selection(self, element_id: str) -> None:
        elem = self._controller.get_element(element_id)
        self._property_panel.load_element(elem)
        self._inspector.show_element(elem)

        # 同步 TreeView 选中（用标志位防循环，不用 blockSignals 确保视图刷新）
        self._syncing_tree = True
        try:
            from PySide6.QtCore import QItemSelectionModel
            sel = self._tree_view.selectionModel()
            model_idx = self._element_browser_model.get_index_for_element(element_id)
            if model_idx.isValid():
                sel.select(model_idx, QItemSelectionModel.SelectionFlag.ClearAndSelect | QItemSelectionModel.SelectionFlag.Rows)
            else:
                sel.clearSelection()
        finally:
            self._syncing_tree = False

        if elem:
            self._status_label.setText(f"已选中: {elem.name} (Tick {elem.start_tick})")
        else:
            self._status_label.setText("未选中")

    def _on_element_count_changed(self, *args) -> None:
        count = len(self._controller.all_elements)
        self.statusBar().showMessage(f"共 {count} 个元素", 3000)

    def _on_tree_context_menu(self, pos) -> None:
        from PySide6.QtWidgets import QMenu
        menu = QMenu(self)
        idx = self._tree_view.indexAt(pos)
        elem = self._element_browser_model.get_element_from_index(idx) if idx.isValid() else None

        act_new_traj = menu.addAction("新建轨迹")
        act_new_traj.triggered.connect(lambda: self._on_new_element("trajectory"))
        act_new_fw = menu.addAction("新建烟花")
        act_new_fw.triggered.connect(lambda: self._on_new_element("firework"))
        act_new_tf = menu.addAction("新建轨迹烟花")
        act_new_tf.triggered.connect(lambda: self._on_new_element("traj_firework"))

        if elem is not None:
            menu.addSeparator()
            act_clone = menu.addAction("复制元素")
            act_clone.triggered.connect(self._on_clone_element)
            act_del = menu.addAction("删除元素")
            act_del.triggered.connect(self._on_delete_selected)

        menu.exec(self._tree_view.viewport().mapToGlobal(pos))

    # ═══════════════════════════════════════════════════
    # 槽：时间线拖拽
    # ═══════════════════════════════════════════════════

    def _on_timeline_select(self, element_id: str) -> None:
        """时间线选中 — 代理元素只高亮自身，面板加载父元素."""
        if not element_id:
            self._controller.clear_selection()
            return
        real_id, _ = self._resolve_proxy_id(element_id)
        parent = self._controller.get_element(real_id)
        if parent and hasattr(parent, 'element_type') and str(parent.element_type) == "ElementType.TRAJ_FIREWORK":
            # 仅高亮被点击的代理块
            self._timeline._selected_id = element_id
            self._timeline._fw_track.set_selection(element_id)
            self._timeline._traj_track.set_selection(element_id)
            # 直接加载面板和检查器（不触发 controller.selection_changed 以防止覆盖高亮）
            self._property_panel.load_element(parent)
            self._inspector.show_element(parent)
            self._status_label.setText(f"已选中: {parent.name} (Tick {parent.start_tick})")
            return
        self._controller.select_element(element_id)

    def _on_timeline_element_moved(self, element_id: str, new_tick: int, old_tick: int) -> None:
        log.debug(f"时间线移动: {element_id} tick={new_tick} old={old_tick}")
        real_id, part = self._resolve_proxy_id(element_id)
        key = "start_tick"  # TF 代理移动 → 整体平移
        elem = self._controller.get_element(real_id)
        if elem:
            self._undo_manager.push_property_change(real_id, key, old_tick, new_tick)
            self._controller.element_changed.emit(real_id, "drag", None)
            self._property_panel.load_element(elem)
            self._inspector.refresh(elem)
            self._project_manager.mark_modified()

    def _on_timeline_element_resized(self, element_id: str, new_dur: int, old_dur: int) -> None:
        log.debug(f"时间线缩放: {element_id} dur={new_dur} old={old_dur}")
        real_id, part = self._resolve_proxy_id(element_id)
        if part == "fw": key = "fw_duration_ticks"
        elif part == "traj": key = "traj_duration_ticks"
        else: key = "duration_ticks"
        elem = self._controller.get_element(real_id)
        if elem:
            self._undo_manager.push_property_change(real_id, key, old_dur, new_dur)
            self._controller.element_changed.emit(real_id, "drag", None)
            self._property_panel.load_element(elem)
            self._inspector.refresh(elem)
            self._project_manager.mark_modified()

    def _resolve_proxy_id(self, element_id: str) -> tuple[str, str]:
        if element_id.endswith("::fw"): return (element_id[:-4], "fw")
        if element_id.endswith("::traj"): return (element_id[:-7], "traj")
        return (element_id, "")

    # ═══════════════════════════════════════════════════
    # 槽：属性变更
    # ═══════════════════════════════════════════════════

    def _on_property_changed(self, element_id: str, key: str, value: object) -> None:
        elem = self._controller.get_element(element_id)
        if elem is None:
            return
        old_value = getattr(elem, key, None)
        if key in ("position", "extra", "end_position", "traj_type", "fw_type",
                    "traj_gradient", "inner_gradient", "outer_gradient",
                    "traj_color_start", "traj_color_end",
                    "inner_color_start", "inner_color_end",
                    "outer_color_start", "outer_color_end"):
            # 已在 property_panel 中直接修改，仅刷新
            pass
        else:
            self._controller.set_property(element_id, key, value)
            self._undo_manager.push_property_change(element_id, key, old_value, value)
        self._inspector.refresh(elem)
        self._project_manager.mark_modified()

    # ═══════════════════════════════════════════════════
    # 槽：位置选择
    # ═══════════════════════════════════════════════════

    def _on_position_select_requested(self, which: str) -> None:
        self._pending_position_target = which
        self._pos_selector.showNormal()

    def _on_position_chosen(self, point: MinecraftPosition) -> None:
        elem = self._controller.selected_element
        if elem is None:
            return
        from dyn.models.elements import Position
        pos = Position(x=point.x, y=point.y, z=point.z)
        which = getattr(self, '_pending_position_target', 'firework')
        if which == "end":
            if isinstance(elem, TrajFireworkElement):
                elem.mid_position = pos
            elif isinstance(elem, TrajectoryElement):
                elem.end_position = pos
        else:
            if isinstance(elem, TrajFireworkElement):
                elem.start_position = pos
            elif isinstance(elem, TrajectoryElement):
                elem.start_position = pos
            elif isinstance(elem, FireworkElement):
                elem.position = pos
        self._property_panel.load_element(elem)
        self._inspector.refresh(elem)
        self._project_manager.mark_modified()

    # ═══════════════════════════════════════════════════
    # 槽：项目操作
    # ═══════════════════════════════════════════════════

    def _on_project_opened(self, project: Project) -> None:
        self._element_browser_model.load_elements(self._controller.all_elements)
        self._tree_view.expandAll()
        self._timeline._on_elements_changed()
        # 恢复位置选择器数据
        try:
            saved = project.saved_positions
            if saved:
                pts = [MinecraftPosition(**p) for p in saved]
                self._pos_selector._points.clear()
                self._pos_selector._points.extend(pts)
                self._pos_selector._fastsearch.clear()
                self._pos_selector._fastsearch.update((int(pt.x), int(pt.z)) for pt in pts)
                self._pos_selector.pix_element_list.get_element_list(self._pos_selector._points)
        except Exception:
            pass

    def _on_project_settings(self) -> None:
        from dyn.ui.dialogs.project_settings_dialog import ProjectSettingsDialog
        proj = self._project_manager.project
        dlg = ProjectSettingsDialog(proj.name, proj.bpm, proj.mc_version, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            proj.bpm = dlg.bpm
            proj.name = dlg.project_name
            proj.mc_version = dlg.mc_version
            self._playback.set_bpm(proj.bpm)
            self._transport_bar.set_bpm(proj.bpm)
            self._project_manager.mark_modified()
            self.setWindowTitle(f"DynFirework — {proj.name}")
            self.statusBar().showMessage(f"BPM: {proj.bpm:.0f} | MC {proj.mc_version} | {proj.name}")

    # ═══════════════════════════════════════════════════
    # 窗口状态
    # ═══════════════════════════════════════════════════

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
                self._on_save_project()
                if self._project_manager.is_modified:
                    event.ignore()
                    return
            elif reply == QMessageBox.Cancel:
                event.ignore()
                return

        settings = QSettings("DynFirework", "dyn-gui")
        settings.setValue("mainwin/geometry", self.saveGeometry())
        settings.setValue("mainwin/state", self.saveState())
        log.info("关闭窗口"); super().closeEvent(event)


if __name__ == "__main__":
    setup_logging()
    log.info("===== DynFirework 启动 =====")
    app = QApplication(sys.argv)
    app.setApplicationName("DynFirework")
    app.setOrganizationName("DynFirework")
    win = MainWin()
    win.show()
    sys.exit(app.exec())

# Logging 已在文件头部配置
