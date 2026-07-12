"""帮助对话框 基于文件系统名的递归树形目录."""
from __future__ import annotations

import logging
from pathlib import Path

from PySide6 import QtCore, QtWidgets

from dyn.ui.dyn_help_ui import Ui_Dialog as DYNHelpUI

log = logging.getLogger("dyn.actions.help")

def _display_name(name: str) -> str:
	"""从文件名提取显示名: '01. 概述/' -> '概述', '01. 什么是DynFirework.md' -> '什么是DynFirework'."""
	stem = name.rsplit('.', 1)[0] if name.endswith('.md') else name
	parts = stem.split('. ', 1) if '. ' in stem else stem.split('-', 1)
	return parts[1] if len(parts) == 2 and parts[0].isdigit() else stem

def _discover_tree(help_dir: Path, base: Path | None = None) -> list[tuple[str, str | list, str | None]]:
	"""递归扫描 help/ 目录，按文件名排序构建树形结构.
	返回 [(显示名, 相对路径 | 子节点列表, dir_path | None), ...]
	目录节点包含其相对路径用于查找 00-XXX 介绍文件.
	"""
	if base is None:
		base = help_dir
	items: list[tuple[str, str | list, str | None]] = []
	entries = sorted(help_dir.iterdir(), key=lambda p: (not p.is_dir(), p.name))
	for entry in entries:
		if entry.name.startswith('.'):
			continue
		if entry.is_dir():
			children = _discover_tree(entry, base)
			if children:
				items.append((_display_name(entry.name), children, str(entry.relative_to(base))))
		elif entry.suffix == '.md':
			prefix = entry.stem.split('-', 1)[0]
			if prefix.isdigit() and int(prefix) == 0:
				continue
			items.append((_display_name(entry.name), str(entry.relative_to(base)), None))
	return items

class DYNHelpWindow(QtWidgets.QDialog):
	"""帮助对话框 左侧多层树形目录，右侧 Markdown 渲染."""

	_HELP_DIR: Path = Path(__file__).parent.parent / "help"

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
		self._build_tree(self._tree, _discover_tree(self._HELP_DIR))
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
			else:
				log.warning("帮助: 未找到占位标签")

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
			else:
				log.warning("帮助: 未找到占位标签")

		# 用 QSplitter 替换固定 grid 列拉伸，允许拖拽调节左右比例
		self.ui.gridLayout.removeWidget(self.ui.label_3)
		self.ui.gridLayout.removeWidget(self.ui.frame)
		self.ui.gridLayout.removeWidget(self.ui.frame_2)

		left_container = QtWidgets.QWidget()
		left_inner = QtWidgets.QVBoxLayout(left_container)
		left_inner.setContentsMargins(0, 0, 0, 0)
		left_inner.setSpacing(4)
		left_inner.addWidget(self.ui.label_3)
		left_inner.addWidget(self.ui.frame)

		self._splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
		self._splitter.addWidget(left_container)
		self._splitter.addWidget(self.ui.frame_2)
		self._splitter.setStretchFactor(0, 0)
		self._splitter.setStretchFactor(1, 1)
		self._splitter.setSizes([180, 420])

		self.ui.gridLayout.addWidget(self._splitter, 0, 0, 2, 2)

		# 默认选中第一项
		self._select_first_leaf()

	def _select_first_leaf(self) -> None:
		def _find(node: QtWidgets.QTreeWidgetItem) -> QtWidgets.QTreeWidgetItem | None:
			if node in self._file_map:
				return node
			for i in range(node.childCount()):
				child = node.child(i)
				if child is None:
					continue
				result = _find(child)
				if result:
					return result
			return None

		for i in range(self._tree.topLevelItemCount()):
			item = self._tree.topLevelItem(i)
			if item is None:
				continue
			leaf = _find(item)
			if leaf:
				self._tree.setCurrentItem(leaf)
				return

	def _build_tree(
			self,
			parent: QtWidgets.QTreeWidget | QtWidgets.QTreeWidgetItem,
			nodes: list[tuple[str, str | list, str | None]],
	) -> None:
		for display, value, dir_path in nodes:
			item = QtWidgets.QTreeWidgetItem([display])
			if isinstance(parent, QtWidgets.QTreeWidget):
				parent.addTopLevelItem(item)
			else:
				parent.addChild(item)
			if isinstance(value, list):
				# 目录节点：查找 00. 介绍文件并映射到该节点
				if dir_path:
					intro_dir = self._HELP_DIR / dir_path
					for f in sorted(intro_dir.glob('00-*.md')):
						self._file_map[item] = str(f.relative_to(self._HELP_DIR))
						break
				self._build_tree(item, value)
			else:
				self._file_map[item] = value

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
