"""df 复合表单共享基类 位置."""
from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
	QWidget, QVBoxLayout, QFormLayout,
	QDoubleSpinBox, QPushButton, QGroupBox, QCheckBox,
)

from dyn.components.base.color_picker import ColorPicker
from dyn.components.base.form_base import FormBase
from dyn.models.df.composites import CompositeElement
from dyn.models.df.values import Position

# 子元素 part 标识符 供浏览器 ProxyNode / 面板路由 / 主窗口选中共用
PART_PRIMARY = "primary"
PART_SECONDARY = "secondary"
PART_CLUSTER = "clustered"
PART_EXPANDING = "expanding"

PART_TO_TYPE_KEY: dict[str, str] = {
	PART_PRIMARY: "_comp_primary",
	PART_SECONDARY: "_comp_secondary",
	PART_CLUSTER: "_comp_clustered",
	PART_EXPANDING: "_comp_expanding",
}

PROXY_DATA_PREFIX = "_comp_"

class CompositeBase(FormBase):
	"""df 复合表单共享基类 子类实现 _setup_type_params 和 _load_type_params."""

	property_changed = Signal(str, str, object, object)
	position_select_requested = Signal(str)

	def __init__(self, parent: QWidget | None = None, has_position: bool = True) -> None:
		super().__init__(parent)
		self._element: CompositeElement | None = None
		self._loading: bool = False
		self._prefix: str = ""
		self._has_position: bool = has_position

		layout = QVBoxLayout(self)
		layout.setContentsMargins(0, 0, 0, 0)
		layout.setSpacing(8)

		if has_position:
			self._setup_position()
		self._setup_type_params()
		layout.addStretch()

		self._hide_all()

	def _setup_position(self) -> None:
		self._group_pos = QGroupBox("位置")
		form = QFormLayout(self._group_pos)
		self._spin_pos_x = QDoubleSpinBox()
		self._spin_pos_x.setRange(-100000, 100000)
		self._spin_pos_x.setDecimals(2)
		self._add_row(form, "pos_x", "X:", self._spin_pos_x)
		self._spin_pos_y = QDoubleSpinBox()
		self._spin_pos_y.setRange(-64, 320)
		self._spin_pos_y.setDecimals(2)
		self._add_row(form, "pos_y", "Y:", self._spin_pos_y)
		self._spin_pos_z = QDoubleSpinBox()
		self._spin_pos_z.setRange(-100000, 100000)
		self._spin_pos_z.setDecimals(2)
		self._add_row(form, "pos_z", "Z:", self._spin_pos_z)
		for w in (self._spin_pos_x, self._spin_pos_y, self._spin_pos_z):
			w.valueChanged.connect(self._on_pos_changed)
		self._btn_pos_select = QPushButton("在地图上选择...")
		self._btn_pos_select.clicked.connect(lambda: self.position_select_requested.emit("composite"))
		form.addRow("", self._btn_pos_select)
		self.layout().addWidget(self._group_pos)

	def _on_pos_changed(self) -> None:
		if self._loading or self._element is None:
			return
		pos = Position(x=self._spin_pos_x.value(), y=self._spin_pos_y.value(), z=self._spin_pos_z.value())
		self._element.position = pos
		self._emit("position", None)

	def _setup_type_params(self) -> None:
		"""子类重写以添加类型专属参数组."""

	def _hide_all(self) -> None:
		if self._has_position:
			self._group_pos.hide()
		for grp in getattr(self, '_sub_groups', []):
			grp.hide()

	def load(self, elem: CompositeElement) -> None:
		self._loading = True
		self._element = elem
		self.block_signals(True)

		self._hide_all()
		if self._has_position:
			self._group_pos.show()
			self._spin_pos_x.setValue(elem.position.x)
			self._spin_pos_y.setValue(elem.position.y)
			self._spin_pos_z.setValue(elem.position.z)

		self._load_type_params(elem)
		self.block_signals(False)
		self._loading = False
		self._update_reset_buttons()

	def _load_type_params(self, elem: CompositeElement) -> None:
		"""子类重写以加载类型专属数据."""

	def clear_form(self) -> None:
		self._element = None
		self._hide_all()
		self.hide()

	def _emit(self, key: str, value: object) -> None:
		if self._element is None or self._loading:
			return
		e = self._element
		old_value = getattr(e, key, None)
		self.property_changed.emit(e.id, key, value, old_value)

	def _get(self, name: str, default=None):
		"""读取带前缀的 CompositeElement 属性."""
		if self._element is None:
			return default
		return getattr(self._element, self._prefix + name, default)

	def _set(self, name: str, value) -> None:
		"""写入带前缀的 CompositeElement 属性."""
		if self._element is None:
			return
		full = self._prefix + name
		old = getattr(self._element, full, None)
		if hasattr(self._element, full):
			setattr(self._element, full, value)
		self.property_changed.emit(self._element.id, full, value, old)

	def _add_color_group(self, title: str) -> tuple[QGroupBox, ColorPicker, ColorPicker, QCheckBox]:
		"""创建颜色组 返回 (group, start_picker, end_picker, gradient_checkbox)."""
		grp = QGroupBox(title)
		layout = QVBoxLayout(grp)
		chk = QCheckBox("使用渐变")
		layout.addWidget(chk)
		start_cp = ColorPicker("开始:")
		layout.addWidget(start_cp)
		end_cp = ColorPicker("结束:")
		layout.addWidget(end_cp)
		chk.toggled.connect(lambda v: end_cp.setEnabled(v))
		self.layout().addWidget(grp)
		return grp, start_cp, end_cp, chk
