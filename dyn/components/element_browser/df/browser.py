"""DynFireworkMod v2.0 元素浏览器 4列 4分类 注册表驱动."""
from __future__ import annotations

from PySide6.QtCore import QModelIndex, Qt

from dyn.models.df.base import ElementCategory, Element as DfElement
from dyn.models.df.registry import get_type_key, get_type_def

from .._base import (
	_BaseBrowserModel, GroupNode, ElementNode,
	_format_time_sec, _format_v1_time,
)

CATEGORY_DISPLAY: dict[ElementCategory, str] = {
	ElementCategory.FIREWORK: "爆炸",
	ElementCategory.TRAJECTORY: "轨迹",
	ElementCategory.EFFECT: "效果",
	ElementCategory.COMPOSITE: "复合",
}

_HEADERS = ("名称", "类型", "起始时间", "时长")

def _type_display_name(elem) -> str:
	if isinstance(elem, DfElement):
		try:
			tk = get_type_key(elem)
			return get_type_def(tk).display_name
		except (KeyError, ValueError):
			return tk
	return "?"

class DfElementBrowserModel(_BaseBrowserModel):
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
		if isinstance(elem, DfElement):
			return elem.category
		return ElementCategory.COMPOSITE

	def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
		if not index.isValid():
			return None
		node = index.internalPointer()
		col = index.column()

		if role == Qt.DisplayRole:
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
					if isinstance(elem, DfElement):
						return _format_time_sec(elem.start_time)
					return _format_v1_time(elem.start_tick)
				elif col == 3:
					if isinstance(elem, DfElement):
						return _format_time_sec(elem.duration)
					return _format_v1_time(elem.duration_ticks)

		return self._style_data(node, role, col)

	def _change_key_column(self, key: str) -> int:
		return {"name": 0, "start_tick": 2, "start_time": 2,
		        "duration_ticks": 3, "duration": 3}.get(key, -1)
