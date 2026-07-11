"""轨迹表单共享基类 提供位置/终点/颜色."""
from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
	QWidget, QVBoxLayout, QFormLayout,
	QDoubleSpinBox, QCheckBox, QPushButton, QGroupBox,
)

from dyn.components.property_panel._base import _FormBase
from dyn.components.property_panel.color_picker import ColorPicker
from dyn.models.elements import Element, TrajectoryElement, TrajFireworkElement, Position, ColorRGB

class TrajBase(_FormBase):
	"""轨迹表单共享基类 子类只需在 _setup_type_params 中添加类型专属参数."""

	property_changed = Signal(str, str, object, object)
	position_select_requested = Signal(str)

	def __init__(self, parent: QWidget | None = None) -> None:
		super().__init__(parent)
		self._element: Element | None = None
		self._loading: bool = False

		layout = QVBoxLayout(self)
		layout.setContentsMargins(0, 0, 0, 0)
		layout.setSpacing(8)

		self._setup_position()
		self._setup_end_position()
		self._setup_color()
		self._setup_type_params()
		layout.addStretch()

		self._hide_all()

	def _setup_position(self) -> None:
		self._group_pos = QGroupBox("起始位置")
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
		self._spin_pos_x.valueChanged.connect(self._on_pos_changed)
		self._spin_pos_y.valueChanged.connect(self._on_pos_changed)
		self._spin_pos_z.valueChanged.connect(self._on_pos_changed)
		self._btn_pos_select = QPushButton("在地图上选择...")
		self._btn_pos_select.clicked.connect(lambda: self.position_select_requested.emit("firework"))
		form.addRow("", self._btn_pos_select)
		self.layout().addWidget(self._group_pos)

	def _on_pos_changed(self) -> None:
		if self._loading:
			return
		e = self._element
		if e is None:
			return
		pos = Position(x=self._spin_pos_x.value(), y=self._spin_pos_y.value(), z=self._spin_pos_z.value())
		if isinstance(e, TrajFireworkElement):
			e.start_position = pos
		elif isinstance(e, TrajectoryElement):
			e.start_position = pos
		self._emit("position", None)

	def _setup_end_position(self) -> None:
		self._group_endpos = QGroupBox("结束位置")
		form = QFormLayout(self._group_endpos)
		self._spin_end_x = QDoubleSpinBox()
		self._spin_end_x.setRange(-100000, 100000)
		self._spin_end_x.setDecimals(2)
		self._add_row(form, "end_x", "X:", self._spin_end_x)
		self._spin_end_y = QDoubleSpinBox()
		self._spin_end_y.setRange(-64, 320)
		self._spin_end_y.setDecimals(2)
		self._add_row(form, "end_y", "Y:", self._spin_end_y)
		self._spin_end_z = QDoubleSpinBox()
		self._spin_end_z.setRange(-100000, 100000)
		self._spin_end_z.setDecimals(2)
		self._add_row(form, "end_z", "Z:", self._spin_end_z)
		self._spin_end_x.valueChanged.connect(self._on_end_pos_changed)
		self._spin_end_y.valueChanged.connect(self._on_end_pos_changed)
		self._spin_end_z.valueChanged.connect(self._on_end_pos_changed)
		self._btn_end_select = QPushButton("在地图上选择...")
		self._btn_end_select.clicked.connect(lambda: self.position_select_requested.emit("end"))
		form.addRow("", self._btn_end_select)
		self.layout().addWidget(self._group_endpos)

	def _on_end_pos_changed(self) -> None:
		if self._loading:
			return
		e = self._element
		if e is None:
			return
		pos = Position(x=self._spin_end_x.value(), y=self._spin_end_y.value(), z=self._spin_end_z.value())
		if isinstance(e, TrajFireworkElement):
			e.mid_position = pos
		elif isinstance(e, TrajectoryElement):
			e.end_position = pos
		self._emit("end_position", None)

	def _setup_color(self) -> None:
		self._group_color = QGroupBox("轨迹颜色")
		layout = QVBoxLayout(self._group_color)
		self._chk_gradient = QCheckBox("使用渐变")
		self._chk_gradient.toggled.connect(lambda v: self._emit("traj_gradient", v))
		layout.addWidget(self._chk_gradient)
		self._color_start = ColorPicker("开始:")
		layout.addWidget(self._color_start)
		self._color_end = ColorPicker("结束:")
		layout.addWidget(self._color_end)
		self._color_start.color_changed.connect(lambda c: self._emit("traj_color_start", ColorRGB(r=c[0], g=c[1], b=c[2])))
		self._color_end.color_changed.connect(lambda c: self._emit("traj_color_end", ColorRGB(r=c[0], g=c[1], b=c[2])))
		self.layout().addWidget(self._group_color)

	def _setup_type_params(self) -> None:
		"""子类重写以添加类型专属参数组."""

	def _hide_all(self) -> None:
		for grp in [self._group_pos, self._group_endpos, self._group_color]:
			grp.hide()
		for grp in getattr(self, '_sub_groups', []):
			grp.hide()

	def load(self, e: Element, tf_part: bool = False) -> None:
		self._loading = True
		self._element = e
		self.block_signals(True)

		self._hide_all()
		self._group_pos.show()
		self._group_endpos.show()
		self._group_color.show()

		self._spin_pos_x.setValue(e.start_position.x)
		self._spin_pos_y.setValue(e.start_position.y)
		self._spin_pos_z.setValue(e.start_position.z)
		self._spin_pos_x.setReadOnly(False)
		self._spin_pos_y.setReadOnly(False)
		self._spin_pos_z.setReadOnly(False)
		self._btn_pos_select.show()

		if isinstance(e, TrajFireworkElement):
			self._spin_end_x.setValue(e.mid_position.x)
			self._spin_end_y.setValue(e.mid_position.y)
			self._spin_end_z.setValue(e.mid_position.z)
		else:
			self._spin_end_x.setValue(e.end_position.x)
			self._spin_end_y.setValue(e.end_position.y)
			self._spin_end_z.setValue(e.end_position.z)
		self._spin_end_x.setReadOnly(False)
		self._spin_end_y.setReadOnly(False)
		self._spin_end_z.setReadOnly(False)
		self._btn_end_select.show()

		self._chk_gradient.setChecked(e.traj_color.use_gradient)
		self._color_end.setEnabled(e.traj_color.use_gradient)
		self._color_start.set_color(e.traj_color.start)
		self._color_end.set_color(e.traj_color.end)

		self._load_type_params(e)
		self.block_signals(False)
		self._loading = False
		self._update_reset_buttons()

	def _load_type_params(self, e: Element) -> None:
		"""子类重写以加载类型专属参数."""

	def clear_form(self) -> None:
		self._element = None
		self._hide_all()
		self.hide()

	def _emit(self, key: str, value: object) -> None:
		if self._element is None or self._loading:
			return
		e = self._element
		old_value = getattr(e, key, None)

		if key == "traj_gradient":
			e.traj_color.use_gradient = value
			self._color_end.setEnabled(value)
		elif key == "traj_color_start":
			old_value = e.traj_color.start
			e.traj_color.start = value
		elif key == "traj_color_end":
			old_value = e.traj_color.end
			e.traj_color.end = value
		elif key not in ("position", "end_position", "extra"):
			pass

		self.property_changed.emit(e.id, key, value, old_value)
