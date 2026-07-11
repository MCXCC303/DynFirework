"""元素浏览器 共享基类."""
from __future__ import annotations

import logging
from enum import Enum
from typing import Any, TYPE_CHECKING

from PySide6.QtCore import (
	QAbstractItemModel,
	QModelIndex,
	Qt,
	Signal,
	Slot,
)
from PySide6.QtGui import QFont, QColor

from dyn.service.element_controller import ElementController

if TYPE_CHECKING:
	from dyn.models.df.base import Element
	from dyn.models.particleex.base import Element as CbElement

log = logging.getLogger("dyn.components.element_browser")

def _format_time_sec(value: float) -> str:
	return f"{value:.2f}s"

def _format_cb_time(tick: int) -> str:
	return f"{tick / 20.0:.2f}s"

# 树节点 按种类分子类，消除 Any

class BaseNode:
	"""树节点基类."""
	__slots__ = ("label", "parent", "children")

	def __init__(
			self,
			label: str,
			parent: BaseNode | None = None,
	) -> None:
		self.label = label
		self.parent = parent
		self.children: list[BaseNode] = []

	@property
	def row(self) -> int:
		if self.parent:
			return self.parent.children.index(self)
		return 0

class GroupNode(BaseNode):
	"""分组节点 data: 分类枚举值."""
	__slots__ = ("data",)

	def __init__(self, label: str, data: Enum, parent: BaseNode | None = None) -> None:
		super().__init__(label, parent)
		self.data: Enum = data

class ElementNode(BaseNode):
	"""元素节点 data: Element | CbElement."""
	__slots__ = ("data",)

	def __init__(self, label: str, data: Element | CbElement, parent: BaseNode | None = None) -> None:
		super().__init__(label, parent)
		self.data: Element | CbElement = data

class ProxyNode(BaseNode):
	"""代理节点 data: 代理标识字符串 ("_tf_traj" / "_tf_fw")."""
	__slots__ = ("data",)

	def __init__(self, label: str, data: str, parent: BaseNode | None = None) -> None:
		super().__init__(label, parent)
		self.data: str = data

class _BaseBrowserModel(QAbstractItemModel):
	"""元素浏览器共享基类 子类提供列定义、分组、数据格式化."""

	selection_changed = Signal(str)

	def __init__(self, parent=None) -> None:
		super().__init__(parent)
		self._controller: ElementController | None = None
		self._root = BaseNode("root")
		self._groups: dict = {}
		self._element_nodes: dict[str, ElementNode] = {}
		self._emitting_selection: bool = False
		self._setup_groups()

	def _setup_groups(self) -> None:
		"""子类实现 创建 GroupNode 存入 self._groups."""
		raise NotImplementedError

	# 抽象方法

	def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
		raise NotImplementedError

	def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
		raise NotImplementedError

	def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole) -> Any:
		raise NotImplementedError

	@staticmethod
	def _category_for_element(elem):
		"""子类实现 返回分组 key."""
		raise NotImplementedError

	# 树结构

	def index(self, row: int, column: int, parent: QModelIndex = QModelIndex()) -> QModelIndex:
		if not self.hasIndex(row, column, parent):
			return QModelIndex()
		if not parent.isValid():
			return self.createIndex(row, column, self._root.children[row])
		parent_node: BaseNode = parent.internalPointer()
		if row < len(parent_node.children):
			return self.createIndex(row, column, parent_node.children[row])
		return QModelIndex()

	def parent(self, index: QModelIndex = QModelIndex()) -> QModelIndex:
		if not index.isValid():
			return QModelIndex()
		node: BaseNode = index.internalPointer()
		if node.parent is None or node.parent is self._root:
			return QModelIndex()
		grandparent = node.parent
		if grandparent is None or grandparent is self._root:
			return QModelIndex()
		return self.createIndex(grandparent.row, 0, grandparent)

	def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
		if not parent.isValid():
			return len(self._root.children)
		node: BaseNode = parent.internalPointer()
		return len(node.children)

	def flags(self, index: QModelIndex) -> Qt.ItemFlags:
		if not index.isValid():
			return Qt.NoItemFlags
		node: BaseNode = index.internalPointer()
		flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable
		if isinstance(node, ElementNode):
			flags |= Qt.ItemIsEditable
		return flags

	# 样式

	@staticmethod
	def _style_data(node: BaseNode, role: int, col: int) -> Any:
		if role == Qt.ForegroundRole and isinstance(node, GroupNode):
			return QColor(100, 100, 100)
		if role == Qt.FontRole and isinstance(node, GroupNode):
			f = QFont()
			f.setBold(True)
			return f
		return None

	# 控制器连接

	def set_controller(self, controller: ElementController) -> None:
		self._controller = controller
		controller.element_added.connect(self._on_element_added)
		controller.element_removed.connect(self._on_element_removed)
		controller.element_changed.connect(self._on_element_changed)
		controller.selection_changed.connect(self._on_controller_selection)

	def _group_for_element(self, elem) -> GroupNode:
		cat = self._category_for_element(elem)
		return self._groups[cat]

	# 元素增删

	@Slot(object)
	def _on_element_added(self, elem) -> None:
		log.debug(f"浏览器添加元素: id={elem.id}, name={elem.name}")
		group = self._group_for_element(elem)
		parent_idx = self._index_for_node(group)
		row = len(group.children)
		self.beginInsertRows(parent_idx, row, row)
		node = ElementNode(elem.name, data=elem, parent=group)
		group.children.append(node)
		self._element_nodes[elem.id] = node
		self.endInsertRows()
		self._on_element_added_extra(node, elem)

	def _on_element_added_extra(self, node: ElementNode, elem) -> None:
		"""子类可重写 添加额外子节点（如 V1 TF 代理节点）."""
		pass

	@Slot(str)
	def _on_element_removed(self, element_id: str) -> None:
		log.debug(f"浏览器移除元素: id={element_id}")
		node = self._element_nodes.pop(element_id, None)
		if node is None:
			return
		self._cleanup_extra_nodes(element_id)
		parent_idx = self._index_for_node(node.parent)
		row = node.row
		self.beginRemoveRows(parent_idx, row, row)
		node.parent.children.pop(row)
		self.endRemoveRows()

	def _cleanup_extra_nodes(self, element_id: str) -> None:
		"""子类可重写 清理额外注册的代理节点."""
		pass

	@Slot(str, str, object)
	def _on_element_changed(self, element_id: str, key: str, value: object) -> None:
		node = self._element_nodes.get(element_id)
		if node is None:
			return
		col = self._change_key_column(key)
		if col >= 0:
			idx = self._index_for_node(node, col)
			self.dataChanged.emit(idx, idx, [Qt.DisplayRole])

	def _change_key_column(self, key: str) -> int:
		"""子类可重写 返回属性 key 对应的列索引."""
		return -1

	# 选中同步

	@Slot(str)
	def _on_controller_selection(self, element_id: str) -> None:
		if self._emitting_selection:
			return
		self._emitting_selection = True
		try:
			self.selection_changed.emit(element_id)
		finally:
			self._emitting_selection = False

	# 查询

	@staticmethod
	def get_element_from_index(index: QModelIndex):
		if not index.isValid():
			return None
		node: BaseNode = index.internalPointer()
		if isinstance(node, ElementNode):
			return node.data
		return None

	def get_index_for_element(self, element_id: str) -> QModelIndex:
		node = self._element_nodes.get(element_id)
		if node is None:
			return QModelIndex()
		return self._index_for_node(node)

	def _index_for_node(self, node: BaseNode, column: int = 0) -> QModelIndex:
		if node is self._root:
			return QModelIndex()
		return self.createIndex(node.row, column, node)

	# 批量加载

	def load_elements(self, elements: list) -> None:
		log.debug(f"浏览器批量加载: {len(elements)} 个元素")
		self.beginResetModel()
		for group in self._groups.values():
			group.children.clear()
		self._element_nodes.clear()
		for elem in elements:
			group = self._group_for_element(elem)
			node = ElementNode(elem.name, data=elem, parent=group)
			group.children.append(node)
			self._element_nodes[elem.id] = node
			self._on_element_added_extra(node, elem)
		self.endResetModel()
