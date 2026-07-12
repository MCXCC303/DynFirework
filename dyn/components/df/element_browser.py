"""DynFireworkMod v2.0 元素浏览器 4列 4分类 注册表驱动."""
from __future__ import annotations

from PySide6.QtCore import QModelIndex, Qt

from dyn.components.base.browser_model import (
	BaseBrowserModel, GroupNode, ElementNode, ProxyNode,
	format_time_sec,
)
from dyn.components.df.property_panel.composites.composite_base import (
	PROXY_DATA_PREFIX, PART_PRIMARY, PART_SECONDARY, PART_CLUSTER, PART_EXPANDING,
)
from dyn.logging_config import get_logger
from dyn.models.df.base import ElementCategory, Element
from dyn.models.df.composites import CompositeElement
from dyn.models.df.registry import get_type_key, get_type_def
from dyn.models.df.values import CompositeType

log = get_logger(__name__)

CATEGORY_DISPLAY: dict[ElementCategory, str] = {
	ElementCategory.FIREWORK: "爆炸",
	ElementCategory.TRAJECTORY: "轨迹",
	ElementCategory.EFFECT: "效果",
	ElementCategory.COMPOSITE: "复合",
}

_HEADERS = ("名称", "类型", "起始时间", "时长")

def _type_display_name(elem) -> str:
	if isinstance(elem, Element):
		try:
			tk = get_type_key(elem)
			return get_type_def(tk).display_name
		except (KeyError, ValueError):
			log.warning(f"未注册的类型键: {tk}")
			return "?"
	return "?"

def _type_display_name_for_fw(fw_type) -> str:
	try:
		return get_type_def(fw_type.value).display_name
	except (KeyError, ValueError):
		return "?"

def _secondary_type_name(st: str) -> str:
	try:
		return get_type_def(st).display_name
	except (KeyError, ValueError):
		return "?"

class DfElementBrowserModel(BaseBrowserModel):
	"""DF 元素浏览器 4列 4分类 含类型列."""

	def _setup_groups(self) -> None:
		self._root.children = []
		for cat in ElementCategory:
			display = CATEGORY_DISPLAY.get(cat, cat.value)
			node = GroupNode(display, data=cat, parent=self._root)
			self._groups[cat] = node
			self._root.children.append(node)

	def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
		return 4

	def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole):
		if orientation == Qt.Horizontal and role == Qt.DisplayRole:
			return _HEADERS[section]
		return None

	@staticmethod
	def _category_for_element(elem) -> ElementCategory:
		if isinstance(elem, Element):
			return elem.category
		log.warning(f"未知元素实例用于分类: {type(elem)}")
		return ElementCategory.COMPOSITE

	def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
		if not index.isValid():
			return None
		node = index.internalPointer()
		col = index.column()

		if role == Qt.DisplayRole:
			if isinstance(node, ProxyNode):
				parent_elem = node.parent.data
				return self._proxy_data(node, col, parent_elem)
			if isinstance(node, GroupNode):
				if col == 0:
					count = sum(1 for c in node.children)
					return f"{node.label} ({count})"
				return ""
			if isinstance(node, ElementNode):
				elem = node.data
				if col == 0:
					return getattr(elem, 'name', '?')
				elif col == 1:
					return _type_display_name(elem)
				elif col == 2:
					return format_time_sec(elem.start_time)
				elif col == 3:
					return format_time_sec(elem.duration)

		return self._style_data(node, role, col)

	@staticmethod
	def _proxy_data(node: ProxyNode, col: int, parent_elem) -> str:
		if col == 0:
			return node.label
		elif col == 1:
			return DfElementBrowserModel._proxy_type_name(node.data, parent_elem)
		elif col == 2:
			return format_time_sec(parent_elem.start_time)
		elif col == 3:
			return format_time_sec(parent_elem.duration)
		return ""

	@staticmethod
	def _proxy_type_name(data: str, elem: CompositeElement) -> str:
		if data == f"{PROXY_DATA_PREFIX}primary":
			return _type_display_name_for_fw(elem.se_primary_type)
		elif data == f"{PROXY_DATA_PREFIX}secondary":
			return _secondary_type_name(elem.se_secondary_type)
		elif data == f"{PROXY_DATA_PREFIX}clustered":
			return "集束烟花"
		elif data == f"{PROXY_DATA_PREFIX}expanding":
			return "膨胀球"
		log.warning(f"未注册的代理类型前缀: {data}")
		return "?"

	def _change_key_column(self, key: str) -> int:
		return {"name": 0, "start_time": 2,
		        "duration": 3}.get(key, -1)

	def _on_element_added_extra(self, node: ElementNode, elem) -> None:
		if isinstance(elem, CompositeElement):
			if elem.composite_type == CompositeType.SECONDARY_EXPLOSION:
				children = [
					ProxyNode("一级烟花", data=f"{PROXY_DATA_PREFIX}{PART_PRIMARY}", parent=node),
					ProxyNode("二级爆炸", data=f"{PROXY_DATA_PREFIX}{PART_SECONDARY}", parent=node),
				]
			elif elem.composite_type == CompositeType.COMBO_EC:
				children = [
					ProxyNode("集束烟花", data=f"{PROXY_DATA_PREFIX}{PART_CLUSTER}", parent=node),
					ProxyNode("膨胀球", data=f"{PROXY_DATA_PREFIX}{PART_EXPANDING}", parent=node),
				]
			else:
				log.warning(f"未知复合类型: {elem.composite_type}, id={elem.id}")
				return
			parent_idx = self._index_for_node(node)
			self.beginInsertRows(parent_idx, 0, len(children) - 1)
			node.children = children
			for i, ch in enumerate(children):
				self._element_nodes[elem.id + "::" + str(i)] = ch
			self.endInsertRows()

	def _cleanup_extra_nodes(self, element_id: str) -> None:
		for suffix in ("::0", "::1"):
			self._element_nodes.pop(element_id + suffix, None)
