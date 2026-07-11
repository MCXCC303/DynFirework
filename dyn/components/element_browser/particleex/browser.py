"""ParticleEx / Colorblock 元素浏览器 3列 3分类 TF 子节点."""
from __future__ import annotations

from PySide6.QtCore import QModelIndex, Qt

from dyn.models.df.base import ElementCategory
from dyn.models.particleex.base import ElementType
from dyn.models.particleex.composites import TrajFireworkElement

from .._base import (
	_BaseBrowserModel, GroupNode, ElementNode, ProxyNode,
	_format_v1_time,
)

CATEGORY_DISPLAY = {
	ElementCategory.TRAJECTORY: "轨迹",
	ElementCategory.FIREWORK: "烟花",
	ElementCategory.COMPOSITE: "轨迹烟花",
}

V1_TO_CATEGORY = {
	ElementType.TRAJECTORY: ElementCategory.TRAJECTORY,
	ElementType.FIREWORK: ElementCategory.FIREWORK,
	ElementType.TRAJ_FIREWORK: ElementCategory.COMPOSITE,
}

_HEADERS = ("名称", "起始时间", "时长")

class ParticleexElementBrowserModel(_BaseBrowserModel):
	"""ParticleEx 元素浏览器 3列 3分类 TF 子节点."""

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
	def _category_for_element(elem) -> ElementCategory:
		if hasattr(elem, 'element_type'):
			return V1_TO_CATEGORY.get(elem.element_type, ElementCategory.COMPOSITE)
		return ElementCategory.COMPOSITE

	def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
		if not index.isValid():
			return None
		node = index.internalPointer()
		col = index.column()

		if role == Qt.DisplayRole:
			if isinstance(node, ProxyNode):
				parent_elem = node.parent.data
				if node.data == "_tf_traj":
					vals = (node.label, _format_v1_time(parent_elem.start_tick),
					        _format_v1_time(parent_elem.traj_duration_ticks))
				else:
					vals = (node.label, _format_v1_time(parent_elem.fw_start_tick),
					        _format_v1_time(parent_elem.fw_duration_ticks))
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
					return _format_v1_time(elem.start_tick)
				elif col == 2:
					if isinstance(elem, TrajFireworkElement):
						return _format_v1_time(elem.traj_duration_ticks + elem.fw_duration_ticks)
					return _format_v1_time(elem.duration_ticks)

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
			self._element_nodes[elem.id + "::traj"] = node  # proxy routing via parent
			self._element_nodes[elem.id + "::fw"] = node
			self.endInsertRows()

	def _cleanup_extra_nodes(self, element_id: str) -> None:
		for suffix in ("::traj", "::fw"):
			self._element_nodes.pop(element_id + suffix, None)
