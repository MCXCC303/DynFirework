"""元素浏览器 — QAbstractItemModel 树形模型，展示轨迹和烟花元素."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import (
    QAbstractItemModel,
    QModelIndex,
    Qt,
    Signal,
    Slot,
)

from dyn.models.elements import (
    Element,
    ElementType,
    TrajectoryElement,
    FireworkElement,
    TrajFireworkElement,
)
from dyn.service.element_controller import ElementController


class _TreeNode:
    """树节点 — 内部数据结构."""

    def __init__(
        self,
        label: str,
        data: Any = None,
        parent: _TreeNode | None = None,
    ) -> None:
        self.label = label
        self.data = data  # Element | None (None = 分组节点)
        self.parent = parent
        self.children: list[_TreeNode] = []

    @property
    def is_group(self) -> bool:
        return self.data is None

    @property
    def row(self) -> int:
        if self.parent:
            return self.parent.children.index(self)
        return 0


class ElementBrowserModel(QAbstractItemModel):
    """元素浏览器树形模型.

    结构:
        ├── 轨迹 (分组)
        │   ├── Launch T1
        │   └── Spark T2
        └── 烟花 (分组)
            ├── Single F1
            └── Double F2
    """

    selection_changed = Signal(str)  # element_id (空 = 取消选中)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._root = _TreeNode("root")
        self._traj_group = _TreeNode("轨迹", parent=self._root)
        self._fw_group = _TreeNode("烟花", parent=self._root)
        self._tf_group = _TreeNode("轨迹烟花", parent=self._root)
        self._root.children = [self._traj_group, self._fw_group, self._tf_group]
        self._element_nodes: dict[str, _TreeNode] = {}
        self._emitting_selection: bool = False

    # ── QAbstractItemModel 接口 ──────────────────────

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
        if grandparent is None:
            return QModelIndex()
        return self.createIndex(grandparent.row, 0, grandparent)

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if not parent.isValid():
            return len(self._root.children)
        node: _TreeNode = parent.internalPointer()
        return len(node.children)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 3  # 名称, 起始 tick, 时长

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        if not index.isValid():
            return None
        node: _TreeNode = index.internalPointer()
        col = index.column()

        if role == Qt.DisplayRole:
            if isinstance(node.data, str) and node.data.startswith("_tf_"):
                # TF 子节点：从父元素获取时间信息
                parent_elem = node.parent.data
                if node.data == "_tf_traj":
                    return (node.label, str(parent_elem.start_tick), str(parent_elem.traj_duration_ticks))[col]
                else:
                    return (node.label, str(parent_elem.fw_start_tick), str(parent_elem.fw_duration_ticks))[col]
            if node.is_group:
                if col == 0:
                    count = sum(1 for c in node.children if not (isinstance(c.data, str) and c.data.startswith("_tf_")))
                    return f"{node.label} ({count})"
                return ""
            elem: Element = node.data
            if col == 0:
                return elem.name
            elif col == 1:
                return str(elem.start_tick)
            elif col == 2:
                return str(elem.duration_ticks)
        elif role == Qt.DecorationRole and col == 0:
            return None  # 后续可加图标
        elif role == Qt.ForegroundRole:
            if node.is_group:
                from PySide6.QtGui import QColor
                return QColor(100, 100, 100)
        elif role == Qt.FontRole and node.is_group:
            from PySide6.QtGui import QFont
            f = QFont()
            f.setBold(True)
            return f

        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole) -> Any:
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return ("名称", "起始 Tick", "时长")[section]
        return None

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        if not index.isValid():
            return Qt.NoItemFlags
        node: _TreeNode = index.internalPointer()
        flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable
        if not node.is_group and not (isinstance(node.data, str) and node.data.startswith("_tf_")):
            flags |= Qt.ItemIsEditable
        return flags

    # ── 数据操作 ──────────────────────────────────────

    def set_controller(self, controller: ElementController) -> None:
        self._controller = controller
        controller.element_added.connect(self._on_element_added)
        controller.element_removed.connect(self._on_element_removed)
        controller.element_changed.connect(self._on_element_changed)
        controller.selection_changed.connect(self._on_controller_selection)

    def _group_for_element(self, elem: Element) -> _TreeNode:
        if elem.element_type == ElementType.TRAJECTORY:
            return self._traj_group
        elif elem.element_type == ElementType.FIREWORK:
            return self._fw_group
        return self._tf_group

    @Slot(Element)
    def _on_element_added(self, elem: Element) -> None:
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
        node = self._element_nodes.pop(element_id, None)
        if node is None:
            return
        # 清理 TF 子节点
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
        col_map = {"name": 0, "start_tick": 1, "duration_ticks": 2}
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

    # ── 查询 ──────────────────────────────────────────

    def get_element_from_index(self, index: QModelIndex) -> Element | None:
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

    # ── 批量加载 ──────────────────────────────────────

    def load_elements(self, elements: list[Element]) -> None:
        self.beginResetModel()
        self._traj_group.children.clear()
        self._fw_group.children.clear()
        self._tf_group.children.clear()
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
