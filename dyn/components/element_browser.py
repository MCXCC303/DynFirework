"""元素浏览器 注册表驱动的动态树形模型，展示爆炸/轨迹/效果/复合四类元素."""
from __future__ import annotations

import logging
from typing import Any

from PySide6.QtCore import (
	QAbstractItemModel,
	QModelIndex,
	Qt,
	Signal,
	Slot,
)
from PySide6.QtGui import QFont, QColor

from dyn.models.df.base import ElementCategory, Element as DfElement
from dyn.models.elements import (
	Element,
	ElementType,
	TrajFireworkElement,
)
from dyn.service.element_controller import ElementController

log = logging.getLogger("dyn.components.element_browser")

CATEGORY_DISPLAY: dict[ElementCategory, str] = {
	ElementCategory.FIREWORK: "爆炸",
	ElementCategory.TRAJECTORY: "轨迹",
	ElementCategory.EFFECT: "效果",
	ElementCategory.COMPOSITE: "复合",
}

V1_TO_CATEGORY = {
	ElementType.TRAJECTORY: ElementCategory.TRAJECTORY,
	ElementType.FIREWORK: ElementCategory.FIREWORK,
	ElementType.TRAJ_FIREWORK: ElementCategory.COMPOSITE,
}

def _format_time_sec(tick: int) -> str:
	"""V1 tick 转换为秒显示格式."""
	return f"{tick / 20.0:.2f}s"

def _format_duration_sec(tick: int) -> str:
	return f"{tick / 20.0:.2f}s"

class _TreeNode:
	"""树节点 内部数据结构."""

	def __init__(
			self,
			label: str,
			data: Any = None,
			parent: _TreeNode | None = None,
	) -> None:
		self.label = label
		self.data = data
		self.parent = parent
		self.children: list[_TreeNode] = []

	@property
	def is_group(self) -> bool:
		return self.data is None or isinstance(self.data, ElementCategory)

	@property
	def row(self) -> int:
		if self.parent:
			return self.parent.children.index(self)
		return 0

class ElementBrowserModel(QAbstractItemModel):
	"""元素浏览器树形模型 注册表驱动.

	结构:
		├── 爆炸 (FIREWORK)
		│   ├── Single F1
		│   └── Double F2
		├── 轨迹 (TRAJECTORY)
		│   ├── Launch T1
		│   └── Spark T2
		├── 效果 (EFFECT)
		└── 复合 (COMPOSITE)
			└── TF-1
				├── 轨迹
				└── 烟花
	"""

	selection_changed = Signal(str)

	def __init__(self, parent=None) -> None:
		super().__init__(parent)
		self._controller: ElementController | None = None
		self._root = _TreeNode("root")
		self._groups: dict[ElementCategory, _TreeNode] = {}
		self._root.children = []
		for cat in ElementCategory:
			display = CATEGORY_DISPLAY.get(cat, cat.value)
			node = _TreeNode(display, data=cat, parent=self._root)
			self._groups[cat] = node
			self._root.children.append(node)
		self._element_nodes: dict[str, _TreeNode] = {}
		self._emitting_selection: bool = False

	def index(self, row: int, column: int, parent: QModelIndex = QModelIndex()) -> QModelIndex:
		if not self.hasIndex(row, column, parent):
			return QModelIndex()
		if not parent.isValid():
			return self.createIndex(row, column, self._root.children[row])
		parent_node: _TreeNode = parent.internalPointer()
		if row < len(parent_node.children):
			return self.createIndex(row, column, parent_node.children[row])
		return QModelIndex()

	def parent(self, index: QModelIndex = QModelIndex()) -> QModelIndex:
		if not index.isValid():
			return QModelIndex()
		node: _TreeNode = index.internalPointer()
		if node.parent is None or node.parent is self._root:
			return QModelIndex()
		grandparent = node.parent
		if grandparent is None or grandparent is self._root:
			return QModelIndex()
		return self.createIndex(grandparent.row, 0, grandparent)

	def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
		if not parent.isValid():
			return len(self._root.children)
		node: _TreeNode = parent.internalPointer()
		return len(node.children)

	def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
		return 3

	def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
		if not index.isValid():
			return None
		node: _TreeNode = index.internalPointer()
		col = index.column()

		if role == Qt.DisplayRole:
			if isinstance(node.data, str) and node.data.startswith("_tf_"):
				parent_elem = node.parent.data
				if node.data == "_tf_traj":
					vals = (node.label, _format_time_sec(parent_elem.start_tick),
					        _format_duration_sec(parent_elem.traj_duration_ticks))
				else:
					vals = (node.label, _format_time_sec(parent_elem.fw_start_tick),
					        _format_duration_sec(parent_elem.fw_duration_ticks))
				return vals[col]
			if node.is_group:
				if col == 0:
					count = sum(1 for c in node.children if not (isinstance(c.data, str) and c.data.startswith("_tf_")))
					return f"{node.label} ({count})"
				return ""
			elem: Element = node.data
			if col == 0:
				return elem.name
			elif col == 1:
				return _format_time_sec(elem.start_tick)
			elif col == 2:
				if elem.element_type == ElementType.TRAJ_FIREWORK:
					return _format_duration_sec(elem.traj_duration_ticks + elem.fw_duration_ticks)
				return _format_duration_sec(elem.duration_ticks)
		elif role == Qt.DecorationRole and col == 0:
			return None
		elif role == Qt.ForegroundRole:
			if node.is_group:
				return QColor(100, 100, 100)
		elif role == Qt.FontRole and node.is_group:
			f = QFont()
			f.setBold(True)
			return f

		return None

	def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole) -> Any:
		if orientation == Qt.Horizontal and role == Qt.DisplayRole:
			return ("名称", "起始时间", "时长")[section]
		return None

	def flags(self, index: QModelIndex) -> Qt.ItemFlags:
		if not index.isValid():
			return Qt.NoItemFlags
		node: _TreeNode = index.internalPointer()
		flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable
		if not node.is_group and not (isinstance(node.data, str) and node.data.startswith("_tf_")):
			flags |= Qt.ItemIsEditable
		return flags

	def set_controller(self, controller: ElementController) -> None:
		self._controller = controller
		controller.element_added.connect(self._on_element_added)
		controller.element_removed.connect(self._on_element_removed)
		controller.element_changed.connect(self._on_element_changed)
		controller.selection_changed.connect(self._on_controller_selection)

	@staticmethod
	def _category_for_element(elem: Element) -> ElementCategory:
		if isinstance(elem, DfElement):
			return elem.category
		return V1_TO_CATEGORY.get(elem.element_type, ElementCategory.COMPOSITE)

	def _group_for_element(self, elem: Element) -> _TreeNode:
		cat = self._category_for_element(elem)
		return self._groups[cat]

	@Slot(Element)
	def _on_element_added(self, elem: Element) -> None:
		log.debug(f"浏览器添加元素: id={elem.id}, name={elem.name}, type={elem.element_type}")
		group = self._group_for_element(elem)
		parent_idx = self._index_for_node(group)
		row = len(group.children)
		self.beginInsertRows(parent_idx, row, row)
		node = _TreeNode(elem.name, data=elem, parent=group)
		group.children.append(node)
		self._element_nodes[elem.id] = node
		self.endInsertRows()
		if elem.element_type == ElementType.TRAJ_FIREWORK:
			self._add_tf_children(node, elem)

	def _add_tf_children(self, parent_node: _TreeNode, elem: TrajFireworkElement) -> None:
		parent_idx = self._index_for_node(parent_node)
		self.beginInsertRows(parent_idx, 0, 1)
		traj_child = _TreeNode("轨迹", data="_tf_traj", parent=parent_node)
		fw_child = _TreeNode("烟花", data="_tf_fw", parent=parent_node)
		parent_node.children = [traj_child, fw_child]
		self._element_nodes[elem.id + "::traj"] = traj_child
		self._element_nodes[elem.id + "::fw"] = fw_child
		self.endInsertRows()

	@Slot(str)
	def _on_element_removed(self, element_id: str) -> None:
		log.debug(f"浏览器移除元素: id={element_id}")
		node = self._element_nodes.pop(element_id, None)
		if node is None:
			return
		for suffix in ("::traj", "::fw"):
			self._element_nodes.pop(element_id + suffix, None)
		parent_idx = self._index_for_node(node.parent)
		row = node.row
		self.beginRemoveRows(parent_idx, row, row)
		node.parent.children.pop(row)
		self.endRemoveRows()

	@Slot(str, str, object)
	def _on_element_changed(self, element_id: str, key: str, value: object) -> None:
		node = self._element_nodes.get(element_id)
		if node is None:
			return
		col_map = {"name": 0, "start_tick": 1, "duration_ticks": 2,
		           "traj_duration_ticks": 2, "fw_duration_ticks": 2}
		col = col_map.get(key, -1)
		if col >= 0:
			idx = self._index_for_node(node, col)
			self.dataChanged.emit(idx, idx, [Qt.DisplayRole])

	@Slot(str)
	def _on_controller_selection(self, element_id: str) -> None:
		if self._emitting_selection:
			return
		self._emitting_selection = True
		try:
			self.selection_changed.emit(element_id)
		finally:
			self._emitting_selection = False

	@staticmethod
	def get_element_from_index(index: QModelIndex) -> Element | None:
		if not index.isValid():
			return None
		node: _TreeNode = index.internalPointer()
		if node.is_group:
			return None
		return node.data

	def get_index_for_element(self, element_id: str) -> QModelIndex:
		node = self._element_nodes.get(element_id)
		if node is None:
			return QModelIndex()
		return self._index_for_node(node)

	def _index_for_node(self, node: _TreeNode, column: int = 0) -> QModelIndex:
		if node is self._root:
			return QModelIndex()
		return self.createIndex(node.row, column, node)

	def load_elements(self, elements: list[Element]) -> None:
		log.debug(f"浏览器批量加载: {len(elements)} 个元素")
		self.beginResetModel()
		for group in self._groups.values():
			group.children.clear()
		self._element_nodes.clear()
		for elem in elements:
			group = self._group_for_element(elem)
			node = _TreeNode(elem.name, data=elem, parent=group)
			group.children.append(node)
			self._element_nodes[elem.id] = node
			if elem.element_type == ElementType.TRAJ_FIREWORK:
				traj_child = _TreeNode("轨迹", data="_tf_traj", parent=node)
				fw_child = _TreeNode("烟花", data="_tf_fw", parent=node)
				node.children = [traj_child, fw_child]
				self._element_nodes[elem.id + "::traj"] = traj_child
				self._element_nodes[elem.id + "::fw"] = fw_child
		self.endResetModel()
