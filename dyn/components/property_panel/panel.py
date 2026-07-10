"""属性面板中控 根据元素类型切换表单."""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
	QWidget, QVBoxLayout, QFormLayout,
	QLabel, QLineEdit, QSpinBox, QDoubleSpinBox,
	QCheckBox, QComboBox, QGroupBox, QScrollArea,
)

from dyn.components.property_panel.fw.fw_base import FwBase
from dyn.components.property_panel.fw.fw_clustered import ClusteredForm
from dyn.components.property_panel.fw.fw_directional import DirectionalForm
from dyn.components.property_panel.fw.fw_double_layer import DoubleLayerForm
from dyn.components.property_panel.fw.fw_expanding_sphere import ExpandingSphereForm
from dyn.components.property_panel.fw.fw_single_layer import SingleLayerForm
from dyn.components.property_panel.traj.traj_base import TrajBase
from dyn.components.property_panel.traj.traj_expanding import ExpandingForm
from dyn.components.property_panel.traj.traj_launch import LaunchForm
from dyn.components.property_panel.traj.traj_offset import OffsetForm
from dyn.components.property_panel.traj.traj_spark import SparkForm
from dyn.components.property_panel.traj.traj_thick import ThickForm
from dyn.logging_config import get_logger
from dyn.models.elements import (
	Element, TrajectoryElement, FireworkElement, TrajFireworkElement,
)
from dyn.service.element_controller import ElementController

log = get_logger(__name__)

_TRAJ_TYPE_LABELS = {
	"launch": "基础发射轨迹",
	"spark": "火花轨迹",
	"offset": "随机偏移轨迹",
	"thick": "粗轨迹（偏移）",
	"expanding": "膨胀轨迹（偏移）",
}
_FW_TYPE_LABELS = {
	"single_layer": "单层烟花",
	"double_layer": "双层烟花",
	"directional": "定向烟花",
	"clustered": "集束烟花",
	"expanding_sphere": "膨胀球烟花",
}

_TRAJ_FORMS: dict[str, type[TrajBase]] = {
	"launch": LaunchForm,
	"spark": SparkForm,
	"offset": OffsetForm,
	"thick": ThickForm,
	"expanding": ExpandingForm,
}
_FW_FORMS: dict[str, type[FwBase]] = {
	"single_layer": SingleLayerForm,
	"double_layer": DoubleLayerForm,
	"directional": DirectionalForm,
	"clustered": ClusteredForm,
	"expanding_sphere": ExpandingSphereForm,
}

class PropertyPanel(QScrollArea):
	"""动态参数面板 中控.

	根据元素类型 + 子类型切换表单:
		TrajectoryElement  -> 按 traj_type 选取轨迹表单
		FireworkElement    -> 按 fw_type 选取烟花表单
		TrajFireworkElement -> 两者组合
	"""

	property_changed = Signal(str, str, object, object)
	position_select_requested = Signal(str)
	element_name_changed = Signal(str, str)

	def __init__(self, controller: ElementController, parent: QWidget | None = None) -> None:
		super().__init__(parent)
		self._controller = controller
		self._current_element: Element | None = None
		self._loading: bool = False

		self.setWidgetResizable(True)
		self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

		container = QWidget()
		self.setWidget(container)
		self._layout = QVBoxLayout(container)
		self._layout.setContentsMargins(8, 8, 8, 8)
		self._layout.setSpacing(8)

		self._setup_common()
		self._setup_type_selectors()

		self._traj_forms: dict[str, TrajBase] = {k: cls() for k, cls in _TRAJ_FORMS.items()}
		self._fw_forms: dict[str, FwBase] = {k: cls() for k, cls in _FW_FORMS.items()}

		for f in self._traj_forms.values():
			self._layout.addWidget(f)
			f.hide()
			f.property_changed.connect(self.property_changed)
			f.position_select_requested.connect(self.position_select_requested)
		for f in self._fw_forms.values():
			self._layout.addWidget(f)
			f.hide()
			f.property_changed.connect(self.property_changed)
			f.position_select_requested.connect(self.position_select_requested)

		self._active_traj: TrajBase | None = None
		self._active_fw: FwBase | None = None

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
		form.addRow("起始 Tick:", self._spin_start_tick)

		self._spin_duration = QSpinBox()
		self._spin_duration.setRange(1, 10000)
		self._spin_duration.valueChanged.connect(lambda v: self._emit_change("duration_ticks", v))
		form.addRow("时长:", self._spin_duration)

		self._chk_enabled = QCheckBox("启用")
		self._chk_enabled.setChecked(True)
		self._chk_enabled.toggled.connect(lambda v: self._emit_change("enabled", v))
		form.addRow("", self._chk_enabled)

		self._group_common = grp
		self._layout.addWidget(grp)

	def _setup_type_selectors(self) -> None:
		"""轨迹/烟花类型选择器 显示在公共字段下方."""
		self._combo_traj_type = QComboBox()
		for k, v in _TRAJ_TYPE_LABELS.items():
			self._combo_traj_type.addItem(v, k)
		self._combo_traj_type.currentIndexChanged.connect(self._on_traj_type_combo)
		self._combo_traj_type.hide()

		self._combo_fw_type = QComboBox()
		for k, v in _FW_TYPE_LABELS.items():
			self._combo_fw_type.addItem(v, k)
		self._combo_fw_type.currentIndexChanged.connect(self._on_fw_type_combo)
		self._combo_fw_type.hide()

		self._lbl_traj_type = QLabel("轨迹类型:")
		self._lbl_traj_type.hide()
		self._layout.addWidget(self._lbl_traj_type)
		self._layout.addWidget(self._combo_traj_type)

		self._lbl_fw_type = QLabel("烟花类型:")
		self._lbl_fw_type.hide()
		self._layout.addWidget(self._lbl_fw_type)
		self._layout.addWidget(self._combo_fw_type)

	def _on_traj_type_combo(self, idx: int) -> None:
		if self._loading or self._current_element is None:
			return
		new_type = self._combo_traj_type.itemData(idx)
		old_type = getattr(self._current_element, 'traj_type', None)
		if new_type == old_type:
			return
		log.debug(f"轨迹类型变更: {old_type} -> {new_type}")
		self._current_element.traj_type = new_type
		self._swap_traj_form(new_type)
		self.property_changed.emit(self._current_element.id, "traj_type", new_type, old_type)

	def _on_fw_type_combo(self, idx: int) -> None:
		if self._loading or self._current_element is None:
			return
		new_type = self._combo_fw_type.itemData(idx)
		old_type = getattr(self._current_element, 'fw_type', None)
		if new_type == old_type:
			return
		log.debug(f"烟花类型变更: {old_type} -> {new_type}")
		self._current_element.fw_type = new_type
		self._swap_fw_form(new_type)
		self.property_changed.emit(self._current_element.id, "fw_type", new_type, old_type)

	def _swap_traj_form(self, traj_type: str) -> None:
		if self._active_traj:
			self._active_traj.clear_form()
			self._active_traj = None
		form = self._traj_forms.get(traj_type)
		if form is None:
			return
		self._active_traj = form
		form.load(self._current_element)
		form.show()

	def _swap_fw_form(self, fw_type: str) -> None:
		if self._active_fw:
			self._active_fw.clear_form()
			self._active_fw = None
		form = self._fw_forms.get(fw_type)
		if form is None:
			return
		self._active_fw = form
		read_only = isinstance(self._current_element, TrajFireworkElement)
		form.load(self._current_element, read_only_pos=read_only)
		form.show()

	def load_element(self, elem: Element | None, part: str = "") -> None:
		if self._loading:
			return
		self._loading = True
		try:
			self._do_load_element(elem, part)
		finally:
			self._loading = False

	def _do_load_element(self, elem: Element | None, part: str = "") -> None:
		self._current_element = elem
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

		if self._active_traj:
			self._active_traj.clear_form()
			self._active_traj = None
		if self._active_fw:
			self._active_fw.clear_form()
			self._active_fw = None

		self._lbl_traj_type.hide()
		self._combo_traj_type.hide()
		self._lbl_fw_type.hide()
		self._combo_fw_type.hide()

		if isinstance(elem, TrajFireworkElement):
			if part == "traj":
				self._show_traj_form(elem, elem.traj_type, tf_part=True)
			elif part == "fw":
				self._show_fw_form(elem, elem.fw_type, read_only_pos=True)
			else:
				self._show_traj_form(elem, elem.traj_type, tf_part=True)
				self._show_fw_form(elem, elem.fw_type, read_only_pos=False)
		elif isinstance(elem, TrajectoryElement):
			idx = self._combo_traj_type.findData(elem.traj_type)
			if idx >= 0:
				self._combo_traj_type.setCurrentIndex(idx)
			self._lbl_traj_type.show()
			self._combo_traj_type.show()
			self._show_traj_form(elem, elem.traj_type)
		elif isinstance(elem, FireworkElement):
			idx = self._combo_fw_type.findData(elem.fw_type)
			if idx >= 0:
				self._combo_fw_type.setCurrentIndex(idx)
			self._lbl_fw_type.show()
			self._combo_fw_type.show()
			self._show_fw_form(elem, elem.fw_type)

		self._block_all(False)

	def _show_traj_form(self, elem: Element, traj_type: str, tf_part: bool = False) -> None:
		form = self._traj_forms.get(traj_type)
		if form is None:
			return
		self._active_traj = form
		form.load(elem, tf_part=tf_part)
		form.show()

	def _show_fw_form(self, elem: Element, fw_type: str, read_only_pos: bool = False) -> None:
		form = self._fw_forms.get(fw_type)
		if form is None:
			return
		self._active_fw = form
		form.load(elem, read_only_pos=read_only_pos)
		form.show()

	def _hide_all(self) -> None:
		self._group_common.hide()
		self._lbl_traj_type.hide()
		self._combo_traj_type.hide()
		self._lbl_fw_type.hide()
		self._combo_fw_type.hide()
		for f in self._traj_forms.values():
			f.clear_form()
		for f in self._fw_forms.values():
			f.clear_form()
		self._active_traj = None
		self._active_fw = None

	def _block_all(self, block: bool) -> None:
		for typ in (QSpinBox, QDoubleSpinBox, QComboBox, QCheckBox, QLineEdit):
			for widget in self.findChildren(typ):
				widget.blockSignals(block)
		for f in self._traj_forms.values():
			f.block_signals(block)
		for f in self._fw_forms.values():
			f.block_signals(block)

	def _emit_change(self, key: str, value: object) -> None:
		if self._current_element is None or self._loading:
			return
		e = self._current_element
		old_value = getattr(e, key, None)

		if key == "name":
			setattr(e, key, value)
		elif key == "start_tick":
			e.start_tick = value
		elif key == "duration_ticks":
			if isinstance(e, TrajFireworkElement):
				return
			e.duration_ticks = value
		elif key == "enabled":
			e.enabled = value

		self.property_changed.emit(e.id, key, value, old_value)

	def _on_name_changed(self, text: str) -> None:
		if self._current_element is None or self._loading:
			return
		self._current_element.name = text
		self.element_name_changed.emit(self._current_element.id, text)
