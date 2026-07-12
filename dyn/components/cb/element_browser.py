"""ColorBlock 元素浏览器 3列 3分类 TF 子节点."""
from __future__ import annotations

from PySide6.QtCore import QModelIndex, Qt

from dyn.components.base.browser_model import (
	BaseBrowserModel, GroupNode, ElementNode, ProxyNode,
	format_cb_time,
)
from dyn.logging_config import get_logger
from dyn.models.cb.base import ElementType
from dyn.models.cb.composites import TrajFireworkElement

log = get_logger(__name__)

class _CB_Category:
	TRAJECTORY = "trajectory"
	FIREWORK = "firework"
	COMPOSITE = "composite"

CATEGORY_DISPLAY = {
	_CB_Category.TRAJECTORY: "轨迹",
	_CB_Category.FIREWORK: "烟花",
	_CB_Category.COMPOSITE: "轨迹烟花",
}

CB_TO_CATEGORY = {
	ElementType.TRAJECTORY: _CB_Category.TRAJECTORY,
	ElementType.FIREWORK: _CB_Category.FIREWORK,
	ElementType.TRAJ_FIREWORK: _CB_Category.COMPOSITE,
}

_HEADERS = ("名称", "起始时间", "时长")

class CbElementBrowserModel(BaseBrowserModel):
	"""ColorBlock 元素浏览器 3列 3分类 TF 子节点."""

	def _setup_groups(self) -> None:
		self._root.children = []
		for cat, display in CATEGORY_DISPLAY.items():
			node = GroupNode(display, data=cat, parent=self._root)
			self._groups[cat] = node
			self._root.children.append(node)

	def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
		return 3

	def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole):
		if orientation == Qt.Horizontal and role == Qt.DisplayRole:
			return _HEADERS[section]
		return None

	@staticmethod
	def _category_for_element(elem) -> str:
		if hasattr(elem, 'element_type'):
			return CB_TO_CATEGORY.get(elem.element_type, _CB_Category.COMPOSITE)
		return _CB_Category.COMPOSITE

	def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
		if not index.isValid():
			return None
		node = index.internalPointer()
		col = index.column()

		if role == Qt.DisplayRole:
			if isinstance(node, ProxyNode):
				parent_elem = node.parent.data
				if node.data == "_tf_traj":
					vals = (node.label, format_cb_time(parent_elem.start_tick),
					        format_cb_time(parent_elem.traj_duration_ticks))
				else:
					vals = (node.label, format_cb_time(parent_elem.fw_start_tick),
					        format_cb_time(parent_elem.fw_duration_ticks))
				return vals[col]
			if isinstance(node, GroupNode):
				if col == 0:
					count = sum(1 for c in node.children if isinstance(c, ElementNode))
					return f"{node.label} ({count})"
				return ""
			if isinstance(node, ElementNode):
				elem = node.data
				if col == 0:
					return getattr(elem, 'name', '?')
				elif col == 1:
					return format_cb_time(elem.start_tick)
				elif col == 2:
					if isinstance(elem, TrajFireworkElement):
						return format_cb_time(elem.traj_duration_ticks + elem.fw_duration_ticks)
					return format_cb_time(elem.duration_ticks)

		return self._style_data(node, role, col)

	def _change_key_column(self, key: str) -> int:
		return {"name": 0, "start_tick": 1,
		        "duration_ticks": 2, "traj_duration_ticks": 2,
		        "fw_duration_ticks": 2}.get(key, -1)

	def _on_element_added_extra(self, node: ElementNode, elem) -> None:
		if isinstance(elem, TrajFireworkElement):
			parent_idx = self._index_for_node(node)
			self.beginInsertRows(parent_idx, 0, 1)
			traj_child = ProxyNode("轨迹", data="_tf_traj", parent=node)
			fw_child = ProxyNode("烟花", data="_tf_fw", parent=node)
			node.children = [traj_child, fw_child]
			self._element_nodes[elem.id + "::traj"] = node
			self._element_nodes[elem.id + "::fw"] = node
			self.endInsertRows()
		log.debug(f"为 TF 元素创建代理节点: id={elem.id}")

	def _cleanup_extra_nodes(self, element_id: str) -> None:
		log.debug(f"清理 TF 代理节点: id={element_id}")
		for suffix in ("::traj", "::fw"):
			self._element_nodes.pop(element_id + suffix, None)
