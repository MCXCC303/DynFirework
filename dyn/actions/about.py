"""关于与帮助对话框."""

from __future__ import annotations

import logging
from pathlib import Path

from PySide6 import QtWidgets

from dyn.ui.df_about_ui import Ui_Dialog as DFAboutUI
from dyn.ui.dyn_help_ui import Ui_Dialog as DYNHelpUI

log = logging.getLogger("dyn.actions.about")

# 帮助目录结构
# 树形结构: (显示名称, 文件名, 子节点列表)
_HELP_TREE = [
	("概述", "01-overview.md", []),
	("游戏内粒子机制", "", [
		("2.1  function", "02-01-function.md", []),
		("2.2  Minecraft 数据包", "02-02-datapack.md", []),
		("2.3  Minecraft 命令", "02-03-commands.md", []),
	]),
	("烟花与轨迹", "", [
		("3.1  轨迹", "03-01-trajectory.md", []),
		("3.2  烟花", "03-02-firework.md", []),
		("3.3  轨迹烟花", "03-03-traj-firework.md", []),
	]),
	("参数一览", "", [
		("4.1  轨迹参数", "04-01-trajectory-params.md", []),
		("4.2  烟花参数", "04-02-firework-params.md", []),
	]),
	("使用", "", [
		("5.1  时间线", "05-01-timeline.md", []),
		("5.2  元素列表", "05-02-element-list.md", []),
		("5.3  面板", "05-03-panel.md", []),
		("5.4  检查器", "05-04-inspector.md", []),
		("5.5  导入", "05-05-import.md", []),
		("5.6  导出", "05-06-export.md", []),
		("5.7  实时音频", "05-07-audio.md", []),
		("5.8  位置选择器", "05-08-position-selector.md", []),
		("5.9  其余功能", "05-09-other.md", []),
	]),
	("FAQ", "06-faq.md", []),
	("快捷键", "07-shortcuts.md", []),
	("优秀作品", "08-showcase.md", []),
]

class DYNAboutWindow(QtWidgets.QDialog):
	"""关于 DynFirework 对话框."""

	def __init__(self) -> None:
		super().__init__()
		log.debug("打开关于对话框")
		self.ui = DFAboutUI()
		self.ui.setupUi(self)

class DYNHelpWindow(QtWidgets.QDialog):
	"""帮助对话框   左侧多层树形目录，右侧 Markdown 渲染."""

	_HELP_DIR = Path(__file__).parent.parent / "help"

	def __init__(self) -> None:
		super().__init__()
		log.debug("打开帮助对话框")
		self.ui = DYNHelpUI()
		self.ui.setupUi(self)

		# 左侧：QTreeWidget 多层目录
		self._tree = QtWidgets.QTreeWidget()
		self._tree.setHeaderHidden(True)
		self._tree.setIndentation(16)
		self._tree.setAnimated(True)
		self._tree.setStyleSheet("""
            QTreeWidget { border: none; }
            QTreeWidget::item { padding: 2px 4px; }
        """)
		self._tree.currentItemChanged.connect(self._on_item_changed)

		self._file_map: dict[QtWidgets.QTreeWidgetItem, str] = {}
		self._build_tree(self._tree, _HELP_TREE)
		self._tree.expandAll()

		# 替换左侧占位 label
		left_layout = self.ui.frame.layout()
		if left_layout:
			for i in range(left_layout.count()):
				w = left_layout.itemAt(i).widget()
				if isinstance(w, QtWidgets.QLabel) and w.text() == "敬请期待":
					left_layout.replaceWidget(w, self._tree)
					w.hide()
					break

		# 右侧详情
		self._detail = QtWidgets.QTextBrowser()
		self._detail.setOpenExternalLinks(True)
		self._detail.setStyleSheet(
			"QTextBrowser { border: none; padding: 8px; font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', 'monospace'; }")

		right_layout = self.ui.frame_2.layout()
		if right_layout:
			for i in range(right_layout.count()):
				w = right_layout.itemAt(i).widget()
				if isinstance(w, QtWidgets.QLabel) and w.text() == "敬请期待":
					right_layout.replaceWidget(w, self._detail)
					w.hide()
					break

		# 默认选中第一项
		if self._tree.topLevelItemCount() > 0:
			self._tree.setCurrentItem(self._tree.topLevelItem(0))

	def _build_tree(
			self,
			parent: QtWidgets.QTreeWidget | QtWidgets.QTreeWidgetItem,
			nodes: list,
	) -> None:
		for name, filename, children in nodes:
			item = QtWidgets.QTreeWidgetItem([name])
			if filename:
				self._file_map[item] = filename
			if isinstance(parent, QtWidgets.QTreeWidget):
				parent.addTopLevelItem(item)
			else:
				parent.addChild(item)
			if children:
				self._build_tree(item, children)

	def _on_item_changed(
			self,
			current: QtWidgets.QTreeWidgetItem,
			previous: QtWidgets.QTreeWidgetItem | None,
	) -> None:
		filename = self._file_map.get(current)
		if filename:
			filepath = self._HELP_DIR / filename
			if filepath.exists():
				self._detail.setMarkdown(filepath.read_text(encoding="utf-8"))
			else:
				log.warning(f"帮助文档未找到: {filename}")
				self._detail.setPlainText("文档未找到。")
		else:
			self._detail.setPlainText("")
