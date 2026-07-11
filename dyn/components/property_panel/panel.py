"""属性面板中控 V2 注册表驱动 + 懒加载."""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
	QWidget, QVBoxLayout, QFormLayout,
	QLabel, QLineEdit, QDoubleSpinBox, QCheckBox, QComboBox, QGroupBox, QScrollArea,
)

from dyn.components.df.property_panel import get_form, _init_form_registry
from dyn.logging_config import get_logger
from dyn.models.df.base import ElementCategory
from dyn.models.df.composites import CompositeElement
from dyn.models.df.effects import EffectElement
from dyn.models.df.fireworks import FireworkElement
from dyn.models.df.registry import get_type_key, get_types_by_category
from dyn.models.df.trajectories import TrajectoryElement
from dyn.service.element_controller import ElementController

log = get_logger(__name__)

_CAT_LABELS: dict[ElementCategory, str] = {
	ElementCategory.FIREWORK: "烟花类型:",
	ElementCategory.TRAJECTORY: "轨迹类型:",
	ElementCategory.EFFECT: "效果类型:",
	ElementCategory.COMPOSITE: "复合类型:",
}

def _ensure_registry() -> None:
	_init_form_registry()

class PropertyPanel(QScrollArea):
	"""动态参数面板 中控.

	根据 ElementCategory + sub_type 切换表单:
		FireworkElement   -> 按 fw_type 选取烟花表单
		TrajectoryElement -> 按 traj_type 选取轨迹表单
		EffectElement       -> 按 effect_type 选取效果表单
		CompositeElement    -> 按 composite_type 选取复合表单
	"""

	property_changed = Signal(str, str, object, object)
	position_select_requested = Signal(str)
	element_name_changed = Signal(str, str)

	def __init__(self, controller: ElementController, parent: QWidget | None = None) -> None:
		super().__init__(parent)
		self._controller = controller
		self._current_element = None
		self._loading: bool = False
		self._forms: dict[str, QWidget] = {}
		self._active_form: QWidget | None = None

		self.setWidgetResizable(True)
		self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

		container = QWidget()
		self.setWidget(container)
		self._layout = QVBoxLayout(container)
		self._layout.setContentsMargins(8, 8, 8, 8)
		self._layout.setSpacing(8)

		_ensure_registry()

		self._setup_common()
		self._setup_type_selector()
		self._setup_form_area()

		self._layout.addStretch()
		self._hide_all()
		self.setEnabled(False)

	def _setup_common(self) -> None:
		grp = QGroupBox("基本信息")
		form = QFormLayout(grp)

		self._edit_name = QLineEdit()
		self._edit_name.setPlaceholderText("元素名称")
		self._edit_name.textChanged.connect(lambda t: self._on_name_changed(t))
		form.addRow("名称:", self._edit_name)

		self._spin_start_time = QDoubleSpinBox()
		self._spin_start_time.setRange(0, 10000)
		self._spin_start_time.setDecimals(1)
		self._spin_start_time.setSingleStep(0.5)
		self._spin_start_time.valueChanged.connect(lambda v: self._emit_change("start_time", v))
		form.addRow("起始时间(秒):", self._spin_start_time)

		self._spin_duration = QDoubleSpinBox()
		self._spin_duration.setRange(0.1, 1000)
		self._spin_duration.setDecimals(1)
		self._spin_duration.setSingleStep(0.5)
		self._spin_duration.valueChanged.connect(lambda v: self._emit_change("duration", v))
		form.addRow("时长(秒):", self._spin_duration)

		self._chk_enabled = QCheckBox("启用")
		self._chk_enabled.setChecked(True)
		self._chk_enabled.toggled.connect(lambda v: self._emit_change("enabled", v))
		form.addRow("", self._chk_enabled)

		self._group_common = grp
		self._layout.addWidget(grp)

	def _setup_type_selector(self) -> None:
		self._lbl_type = QLabel("")
		self._combo_type = QComboBox()
		self._combo_type.currentIndexChanged.connect(self._on_type_changed)
		self._lbl_type.hide()
		self._combo_type.hide()
		self._layout.addWidget(self._lbl_type)
		self._layout.addWidget(self._combo_type)

	def _setup_form_area(self) -> None:
		self._form_container = QWidget()
		self._form_layout = QVBoxLayout(self._form_container)
		self._form_layout.setContentsMargins(0, 0, 0, 0)
		self._form_layout.setSpacing(0)
		self._layout.addWidget(self._form_container)

	def _on_type_changed(self, idx: int) -> None:
		if self._loading or self._current_element is None:
			return
		new_type = self._combo_type.itemData(idx)
		if new_type is None:
			return
		old_key = get_type_key(self._current_element)
		if new_type == old_key:
			return
		log.debug(f"类型变更: {old_key} -> {new_type}")
		self._set_element_type(new_type)
		self._swap_form(new_type)
		self.property_changed.emit(self._current_element.id, "element_type", new_type, old_key)

	def _set_element_type(self, type_key: str) -> None:
		e = self._current_element
		if isinstance(e, FireworkElement):
			from dyn.models.df.values import FireworkType
			e.fw_type = FireworkType(type_key)
		elif isinstance(e, TrajectoryElement):
			from dyn.models.df.values import TrajectoryType
			e.traj_type = TrajectoryType(type_key)
		elif isinstance(e, EffectElement):
			from dyn.models.df.values import EffectType
			e.effect_type = EffectType(type_key)
		elif isinstance(e, CompositeElement):
			from dyn.models.df.values import CompositeType
			e.composite_type = CompositeType(type_key)

	def _swap_form(self, type_key: str) -> None:
		if self._active_form:
			if hasattr(self._active_form, 'clear_form'):
				self._active_form.clear_form()
			self._active_form.hide()
			self._active_form = None

		form = self._get_or_create_form(type_key)
		if form is None:
			return
		self._active_form = form
		if hasattr(form, 'load'):
			form.load(self._current_element)
		form.show()

	def _get_or_create_form(self, type_key: str) -> QWidget | None:
		if type_key in self._forms:
			return self._forms[type_key]
		form = get_form(type_key)
		if form is None:
			log.warning(f"未找到 type_key={type_key} 的表单")
			return None
		form.property_changed.connect(self.property_changed)
		if hasattr(form, 'position_select_requested'):
			form.position_select_requested.connect(self.position_select_requested)
		self._form_layout.addWidget(form)
		form.hide()
		self._forms[type_key] = form
		return form

	def load_element(self, elem, part: str = "") -> None:
		# 对V1的兼容签名适配
		if self._loading:
			return
		self._loading = True
		try:
			self._do_load_element(elem)
		finally:
			self._loading = False

	def _do_load_element(self, elem) -> None:
		self._current_element = elem
		if elem is None:
			self._hide_all()
			self.setEnabled(False)
			return

		self.setEnabled(True)
		self._block_all(True)

		self._edit_name.setText(elem.name)
		self._spin_start_time.setValue(elem.start_time)
		self._spin_duration.setValue(elem.duration)
		self._chk_enabled.setChecked(elem.enabled)
		self._group_common.show()

		if self._active_form:
			if hasattr(self._active_form, 'clear_form'):
				self._active_form.clear_form()
			self._active_form.hide()
			self._active_form = None

		cat = elem.category
		type_key = get_type_key(elem)
		types = get_types_by_category(cat)

		self._lbl_type.setText(_CAT_LABELS.get(cat, "类型:"))
		self._combo_type.blockSignals(True)
		self._combo_type.clear()
		for td in types:
			self._combo_type.addItem(td.display_name, td.type_key)
		idx = self._combo_type.findData(type_key)
		if idx >= 0:
			self._combo_type.setCurrentIndex(idx)
		self._combo_type.blockSignals(False)
		self._lbl_type.show()
		self._combo_type.show()

		self._swap_form(type_key)
		self._block_all(False)

	def _hide_all(self) -> None:
		self._group_common.hide()
		self._lbl_type.hide()
		self._combo_type.hide()
		if self._active_form:
			if hasattr(self._active_form, 'clear_form'):
				self._active_form.clear_form()
			self._active_form.hide()
			self._active_form = None

	def _block_all(self, block: bool) -> None:
		for typ in (QDoubleSpinBox, QComboBox, QCheckBox, QLineEdit):
			for widget in self.findChildren(typ):
				widget.blockSignals(block)
		for f in self._forms.values():
			if hasattr(f, 'block_signals'):
				f.block_signals(block)

	def _emit_change(self, key: str, value: object) -> None:
		if self._current_element is None or self._loading:
			return
		e = self._current_element
		old_value = getattr(e, key, None)
		setattr(e, key, value)
		self.property_changed.emit(e.id, key, value, old_value)

	def _on_name_changed(self, text: str) -> None:
		if self._current_element is None or self._loading:
			return
		self._current_element.name = text
		self.element_name_changed.emit(self._current_element.id, text)
