"""df 烟花表单共享基类 位置 + 内外层颜色 + 角度拨盘 + tail_flicker."""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
	QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
	QLabel, QDoubleSpinBox, QCheckBox, QPushButton, QGroupBox, QDial,
)

from dyn.components.base.color_picker import ColorPicker
from dyn.components.base.form_base import FormBase
from dyn.logging_config import get_logger
from dyn.models.df.fireworks import FireworkElement
from dyn.models.df.values import Position, ColorRGB

log = get_logger(__name__)

class FwBase(FormBase):
	"""df 烟花表单共享基类 子类实现 _setup_type_sections 和 _load_type_sections."""

	property_changed = Signal(str, str, object, object)
	position_select_requested = Signal(str)

	def __init__(self, parent: QWidget | None = None) -> None:
		super().__init__(parent)
		self._element: FireworkElement | None = None
		self._loading: bool = False

		layout = QVBoxLayout(self)
		layout.setContentsMargins(0, 0, 0, 0)
		layout.setSpacing(8)

		self._setup_position()
		self._setup_inner_color()
		self._setup_outer_color()
		self._setup_angle()
		self._setup_tail_flicker()
		self._setup_lifetime()
		self._setup_type_sections()
		layout.addStretch()

		self._hide_all()

	def _setup_position(self) -> None:
		self._group_pos = QGroupBox("爆炸中心")
		form = QFormLayout(self._group_pos)
		self._spin_pos_x = QDoubleSpinBox()
		self._spin_pos_x.setRange(-100000, 100000)
		self._spin_pos_x.setDecimals(2)
		self._add_row(form, "fw_pos_x", "X:", self._spin_pos_x)
		self._spin_pos_y = QDoubleSpinBox()
		self._spin_pos_y.setRange(-64, 320)
		self._spin_pos_y.setDecimals(2)
		self._add_row(form, "fw_pos_y", "Y:", self._spin_pos_y)
		self._spin_pos_z = QDoubleSpinBox()
		self._spin_pos_z.setRange(-100000, 100000)
		self._spin_pos_z.setDecimals(2)
		self._add_row(form, "fw_pos_z", "Z:", self._spin_pos_z)
		for w in (self._spin_pos_x, self._spin_pos_y, self._spin_pos_z):
			w.valueChanged.connect(self._on_pos_changed)
		self._btn_pos_select = QPushButton("在地图上选择...")
		self._btn_pos_select.clicked.connect(lambda: self.position_select_requested.emit("firework"))
		form.addRow("", self._btn_pos_select)
		self.layout().addWidget(self._group_pos)

	def _on_pos_changed(self) -> None:
		if self._loading or self._element is None:
			return
		log.debug(f"烟花位置变更: id={self._element.id[:8]}")
		pos = Position(x=self._spin_pos_x.value(), y=self._spin_pos_y.value(), z=self._spin_pos_z.value())
		self._element.position = pos
		self._emit("position", None)

	def _setup_inner_color(self) -> None:
		self._group_inner = QGroupBox("烟花颜色")
		layout = QVBoxLayout(self._group_inner)
		self._chk_inner_gradient = QCheckBox("使用渐变")
		layout.addWidget(self._chk_inner_gradient)
		self._chk_inner_gradient.toggled.connect(lambda v: self._emit("inner_gradient", v))
		self._color_inner_start = ColorPicker("开始:")
		layout.addWidget(self._color_inner_start)
		self._color_inner_end = ColorPicker("结束:")
		layout.addWidget(self._color_inner_end)
		self._color_inner_start.color_changed.connect(lambda c: self._emit("inner_color_start", ColorRGB(r=c.r, g=c.g, b=c.b)))
		self._color_inner_end.color_changed.connect(lambda c: self._emit("inner_color_end", ColorRGB(r=c.r, g=c.g, b=c.b)))
		self.layout().addWidget(self._group_inner)

	def _setup_outer_color(self) -> None:
		self._group_outer = QGroupBox("外层颜色")
		layout = QVBoxLayout(self._group_outer)
		self._chk_outer_gradient = QCheckBox("使用渐变")
		layout.addWidget(self._chk_outer_gradient)
		self._chk_outer_gradient.toggled.connect(lambda v: self._emit("outer_gradient", v))
		self._color_outer_start = ColorPicker("开始:")
		layout.addWidget(self._color_outer_start)
		self._color_outer_end = ColorPicker("结束:")
		layout.addWidget(self._color_outer_end)
		self._color_outer_start.color_changed.connect(lambda c: self._emit("outer_color_start", ColorRGB(r=c.r, g=c.g, b=c.b)))
		self._color_outer_end.color_changed.connect(lambda c: self._emit("outer_color_end", ColorRGB(r=c.r, g=c.g, b=c.b)))
		self.layout().addWidget(self._group_outer)

	def _setup_angle(self) -> None:
		self._group_angle = QGroupBox("爆炸角度")
		layout = QVBoxLayout(self._group_angle)
		layout.setAlignment(Qt.AlignCenter)

		row = QHBoxLayout()
		row.setAlignment(Qt.AlignCenter)
		row.addStretch()

		h_grp = QVBoxLayout()
		h_grp.setAlignment(Qt.AlignCenter)
		self._dial_h = QDial()
		self._dial_h.setRange(1, 360)
		self._dial_h.setValue(30)
		self._dial_h.setNotchesVisible(True)
		self._dial_h.setFixedSize(80, 80)
		h_grp.addWidget(self._dial_h, alignment=Qt.AlignCenter)
		h_grp.addWidget(QLabel("水平角度"), alignment=Qt.AlignCenter)
		self._spin_h_angle = QDoubleSpinBox()
		self._spin_h_angle.setRange(1, 360)
		self._spin_h_angle.setValue(30)
		self._spin_h_angle.setFixedWidth(80)
		self._dial_h.valueChanged.connect(lambda v: self._spin_h_angle.setValue(v))
		self._spin_h_angle.valueChanged.connect(lambda v: self._dial_h.setValue(int(v)))
		h_grp.addWidget(self._spin_h_angle, alignment=Qt.AlignCenter)
		row.addLayout(h_grp)

		row.addSpacing(30)

		v_grp = QVBoxLayout()
		v_grp.setAlignment(Qt.AlignCenter)
		self._dial_v = QDial()
		self._dial_v.setRange(1, 180)
		self._dial_v.setValue(30)
		self._dial_v.setNotchesVisible(True)
		self._dial_v.setFixedSize(80, 80)
		v_grp.addWidget(self._dial_v, alignment=Qt.AlignCenter)
		v_grp.addWidget(QLabel("垂直角度"), alignment=Qt.AlignCenter)
		self._spin_v_angle = QDoubleSpinBox()
		self._spin_v_angle.setRange(1, 180)
		self._spin_v_angle.setValue(30)
		self._spin_v_angle.setFixedWidth(80)
		self._dial_v.valueChanged.connect(lambda v: self._spin_v_angle.setValue(v))
		self._spin_v_angle.valueChanged.connect(lambda v: self._dial_v.setValue(int(v)))
		v_grp.addWidget(self._spin_v_angle, alignment=Qt.AlignCenter)
		row.addLayout(v_grp)

		row.addStretch()
		layout.addLayout(row)
		self.layout().addWidget(self._group_angle)

	def _setup_tail_flicker(self) -> None:
		self._chk_tail_flicker = QCheckBox("启用尾部闪烁")
		self._chk_tail_flicker.toggled.connect(lambda v: self._emit("enable_tail_flicker", v))
		self.layout().addWidget(self._chk_tail_flicker)

	def _setup_lifetime(self) -> None:
		self._group_lifetime = QGroupBox("粒子参数")
		form = QFormLayout(self._group_lifetime)
		self._spin_fw_lifetime = QDoubleSpinBox()
		self._spin_fw_lifetime.setRange(0.1, 60)
		self._spin_fw_lifetime.setSingleStep(0.5)
		self._spin_fw_lifetime.setDecimals(1)
		self._add_row(form, "fw_lifetime", "粒子生命周期(秒):", self._spin_fw_lifetime, default=2.0)
		self._spin_fw_lifetime.valueChanged.connect(lambda v: self._emit("fw_lifetime", v))
		self.layout().addWidget(self._group_lifetime)

	def _setup_type_sections(self) -> None:
		"""子类重写以添加类型专属参数组."""

	def _hide_all(self) -> None:
		for grp in [self._group_pos, self._group_inner, self._group_outer, self._group_angle, self._group_lifetime]:
			grp.hide()
		self._chk_tail_flicker.hide()
		for grp in getattr(self, '_sub_groups', []):
			grp.hide()

	def load(self, elem: FireworkElement) -> None:
		log.debug(f"加载烟花表单: name={elem.name}, fw_type={elem.fw_type}")
		self._loading = True
		self._element = elem
		self.block_signals(True)

		self._hide_all()
		self._group_pos.show()
		self._group_inner.show()
		self._group_lifetime.show()
		if elem.fw_type.value != "nebula":
			self._chk_tail_flicker.show()

		self._spin_pos_x.setValue(elem.position.x)
		self._spin_pos_y.setValue(elem.position.y)
		self._spin_pos_z.setValue(elem.position.z)

		self._chk_inner_gradient.setChecked(elem.inner_color.use_gradient)
		self._color_inner_end.setEnabled(elem.inner_color.use_gradient)
		self._color_inner_start.set_color(elem.inner_color.start)
		self._color_inner_end.set_color(elem.inner_color.end)

		self._chk_tail_flicker.setChecked(elem.enable_tail_flicker)
		self._spin_fw_lifetime.setValue(elem.fw_lifetime)

		self._load_type_sections(elem)
		self.block_signals(False)
		self._loading = False
		self._update_reset_buttons()

	def _load_type_sections(self, elem: FireworkElement) -> None:
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

		if key == "inner_gradient":
			e.inner_color.use_gradient = value
			self._color_inner_end.setEnabled(value)
		elif key == "outer_gradient":
			e.outer_color.use_gradient = value
			self._color_outer_end.setEnabled(value)
		elif key == "inner_color_start":
			old_value = e.inner_color.start
			e.inner_color.start = value
		elif key == "inner_color_end":
			old_value = e.inner_color.end
			e.inner_color.end = value
		elif key == "outer_color_start":
			old_value = e.outer_color.start
			e.outer_color.start = value
		elif key == "outer_color_end":
			old_value = e.outer_color.end
			e.outer_color.end = value
		elif key == "fw_lifetime":
			old_value = e.fw_lifetime
			e.fw_lifetime = value
		elif key == "position":
			pass
		elif key == "extra":
			log.debug(f"烟花额外属性变更: key={key}, value={value}")
		else:
			pass

		self.property_changed.emit(e.id, key, value, old_value)
