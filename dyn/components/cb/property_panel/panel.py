"""ColorBlock 属性面板中控 tick 单位."""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
	QWidget, QVBoxLayout, QFormLayout,
	QLabel, QLineEdit, QSpinBox, QCheckBox, QComboBox, QGroupBox, QScrollArea,
)

from dyn.logging_config import get_logger
from dyn.models.cb import Element, ElementType, TrajectoryElement, TrajFireworkElement
from dyn.service.element_controller import ElementController

log = get_logger(__name__)

_TRAJ_TYPES: list[tuple[str, str]] = [
	("launch", "发射轨迹"),
	("spark", "火花轨迹"),
	("offset", "偏移轨迹"),
	("thick", "粗轨迹"),
	("expanding", "膨胀轨迹"),
]

_FW_TYPES: list[tuple[str, str]] = [
	("single_layer", "单层烟花"),
	("double_layer", "双层烟花"),
	("directional", "定向烟花"),
	("clustered", "集束烟花"),
	("expanding_sphere", "膨胀球烟花"),
]

class CbPropertyPanel(QScrollArea):
	"""ColorBlock 属性面板中控 tick 单位.

	根据 ElementType 路由:
		TrajectoryElement  -> 按 traj_type 选取轨迹表单
		FireworkElement    -> 按 fw_type 选取烟花表单
		TrajFireworkElement -> 按 part 决定显示轨迹或烟花表单
	"""

	property_changed = Signal(str, str, object, object)
	position_select_requested = Signal(str)
	element_name_changed = Signal(str, str)

	def __init__(self, controller: ElementController, parent: QWidget | None = None) -> None:
		super().__init__(parent)
		self._controller = controller
		self._current_element: Element | None = None
		self._current_part: str = ""
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

		self._setup_common()
		self._setup_type_selector()
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

		self._spin_start_tick = QSpinBox()
		self._spin_start_tick.setRange(0, 100000)
		self._spin_start_tick.valueChanged.connect(lambda v: self._emit_change("start_tick", v))
		form.addRow("起始 tick:", self._spin_start_tick)

		self._spin_duration = QSpinBox()
		self._spin_duration.setRange(1, 100000)
		self._spin_duration.valueChanged.connect(lambda v: self._emit_change("duration_ticks", v))
		form.addRow("时长(tick):", self._spin_duration)

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

	def _on_type_changed(self, idx: int) -> None:
		if self._loading or self._current_element is None:
			return
		new_type = self._combo_type.itemData(idx)
		if new_type is None:
			return
		e = self._current_element
		old_key = self._current_type_key(e)
		if new_type == old_key:
			return
		log.debug(f"类型变更: {old_key} -> {new_type}")
		if isinstance(e, TrajFireworkElement) and self._current_part == "traj":
			e.traj_type = new_type
		elif isinstance(e, TrajectoryElement):
			e.traj_type = new_type
		else:
			e.fw_type = new_type
		self._swap_form(new_type)
		self.property_changed.emit(e.id, "element_type", new_type, old_key)

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
			e = self._current_element
			if isinstance(e, TrajFireworkElement):
				if self._current_part == "traj":
					form.load(e, tf_part=True)
				else:
					form.load(e, read_only_pos=True)
			else:
				form.load(e)
		form.show()

	def _get_or_create_form(self, type_key: str) -> QWidget | None:
		if type_key in self._forms:
			return self._forms[type_key]
		form = self._create_form(type_key)
		if form is None:
			log.warning(f"未找到 type_key={type_key} 的 CB 表单")
			return None
		form.property_changed.connect(self.property_changed)
		if hasattr(form, 'position_select_requested'):
			form.position_select_requested.connect(self.position_select_requested)
		self._layout.addWidget(form)
		form.hide()
		self._forms[type_key] = form
		return form

	@staticmethod
	def _create_form(type_key: str) -> QWidget | None:
		if type_key in ("launch", "spark", "offset", "thick", "expanding"):
			from dyn.components.cb.property_panel.traj import (
				traj_launch, traj_spark, traj_offset, traj_thick, traj_expanding,
			)
			_map = {
				"launch": traj_launch.LaunchForm,
				"spark": traj_spark.SparkForm,
				"offset": traj_offset.OffsetForm,
				"thick": traj_thick.ThickForm,
				"expanding": traj_expanding.ExpandingForm,
			}
			cls = _map.get(type_key)
			return cls() if cls else None

		if type_key in ("single_layer", "double_layer", "directional", "clustered", "expanding_sphere"):
			from dyn.components.cb.property_panel.fw import (
				fw_single_layer, fw_double_layer, fw_directional,
				fw_clustered, fw_expanding_sphere,
			)
			_map = {
				"single_layer": fw_single_layer.SingleLayerForm,
				"double_layer": fw_double_layer.DoubleLayerForm,
				"directional": fw_directional.DirectionalForm,
				"clustered": fw_clustered.ClusteredForm,
				"expanding_sphere": fw_expanding_sphere.ExpandingSphereForm,
			}
			cls = _map.get(type_key)
			return cls() if cls else None

		return None

	# 公共接口

	def load_element(self, elem: Element | None, part: str = "") -> None:
		if self._loading:
			return
		log.debug(f"加载元素: type={type(elem).__name__ if elem else 'None'}, "
		          f"name={getattr(elem, 'name', 'N/A') if elem else 'N/A'}, part={part}")
		self._loading = True
		try:
			self._do_load_element(elem, part)
		finally:
			self._loading = False

	def _do_load_element(self, elem: Element | None, part: str) -> None:
		self._current_element = elem
		self._current_part = part
		if elem is None:
			self._hide_all()
			self.setEnabled(False)
			return

		self.setEnabled(True)
		self._block_all(True)

		self._edit_name.setText(elem.name)
		self._spin_start_tick.setValue(elem.start_tick)
		if isinstance(elem, TrajFireworkElement):
			self._spin_duration.setValue(elem.traj_duration_ticks + elem.fw_duration_ticks)
			self._spin_duration.setReadOnly(True)
		else:
			self._spin_duration.setValue(elem.duration_ticks)
			self._spin_duration.setReadOnly(False)
		self._chk_enabled.setChecked(elem.enabled)
		self._group_common.show()

		if self._active_form:
			if hasattr(self._active_form, 'clear_form'):
				self._active_form.clear_form()
			self._active_form.hide()
			self._active_form = None

		# 按 element 类型 + part 确定显示轨迹还是烟花类型
		try:
			if isinstance(elem, TrajFireworkElement) and part == "traj":
				type_key = elem.traj_type
				cat = ElementType.TRAJECTORY
			elif isinstance(elem, TrajectoryElement):
				type_key = elem.traj_type
				cat = ElementType.TRAJECTORY
			else:
				type_key = elem.fw_type if hasattr(elem, 'fw_type') else "single_layer"
				cat = ElementType.FIREWORK
			types = _TRAJ_TYPES if cat == ElementType.TRAJECTORY else _FW_TYPES

			self._lbl_type.setText("轨迹类型:" if cat == ElementType.TRAJECTORY else "烟花类型:")
			self._combo_type.blockSignals(True)
			self._combo_type.clear()
			for key, display in types:
				self._combo_type.addItem(display, key)
			idx = self._combo_type.findData(type_key)
			if idx >= 0:
				self._combo_type.setCurrentIndex(idx)
			self._combo_type.blockSignals(False)
			self._lbl_type.show()
			self._combo_type.show()

			self._swap_form(type_key)
		except Exception:
			log.error(f"加载元素类型分发失败: elem={elem}, part={part}", exc_info=True)
		self._block_all(False)

	def _current_type_key(self, elem: Element) -> str:
		if isinstance(elem, TrajFireworkElement) and self._current_part == "traj":
			return elem.traj_type
		if isinstance(elem, TrajectoryElement):
			return elem.traj_type
		return elem.fw_type if hasattr(elem, 'fw_type') else "single_layer"

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
		for typ in (QSpinBox, QComboBox, QCheckBox, QLineEdit):
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
