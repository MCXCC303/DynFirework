"""SubSecondaryForm - 二级爆炸子表单 expanding / single_layer 两种类型."""
from __future__ import annotations

from PySide6.QtWidgets import (
	QFormLayout, QSpinBox, QDoubleSpinBox, QComboBox, QGroupBox,
)

from dyn.logging_config import get_logger
from dyn.models.df.composites import CompositeElement
from dyn.models.df.values import ColorRGB
from ..composite_base import CompositeBase

log = get_logger(__name__)

class SubSecondaryForm(CompositeBase):
	"""二级爆炸子表单 两种爆炸类型 expanding / single_layer 动态切换."""

	def __init__(self, parent=None) -> None:
		super().__init__(parent, has_position=False)

	def _setup_type_params(self) -> None:
		self._group_type_selector = QGroupBox("二级爆炸类型")
		form = QFormLayout(self._group_type_selector)
		self._combo_type = QComboBox()
		self._combo_type.addItem("膨胀球", "expanding")
		self._combo_type.addItem("单层烟花", "single_layer")
		self._add_row(form, "type", "类型:", self._combo_type, "expanding")
		self._combo_type.currentIndexChanged.connect(self._on_type_changed)
		self.layout().addWidget(self._group_type_selector)

		self._secondary_color_group, self._color_start, self._color_end, self._chk_gradient = \
			self._add_color_group("颜色")

		self._setup_expanding_group()
		self._setup_single_layer_group()

		for w in (
				self._spin_exp_radius, self._spin_exp_radial_speed,
				self._spin_exp_count, self._spin_exp_lifetime, self._spin_exp_duration,
				self._spin_sl_speed, self._spin_sl_count,
				self._spin_sl_lifetime, self._spin_sl_duration,
		):
			w.valueChanged.connect(self._on_extra_changed)

		self._color_start.color_changed.connect(lambda c: self._on_extra_changed())
		self._color_end.color_changed.connect(lambda c: self._on_extra_changed())
		self._chk_gradient.toggled.connect(self._on_extra_changed)

		self._sub_groups = [
			self._group_type_selector,
			self._secondary_color_group,
			self._group_exp,
			self._group_sl,
		]

	def _setup_expanding_group(self) -> None:
		self._group_exp = QGroupBox("膨胀球参数")
		form = QFormLayout(self._group_exp)
		self._spin_exp_radius = QDoubleSpinBox()
		self._spin_exp_radius.setRange(0.1, 100)
		self._add_row(form, "exp_radius", "半径:", self._spin_exp_radius, 3.0)
		self._spin_exp_radial_speed = QDoubleSpinBox()
		self._spin_exp_radial_speed.setRange(0.1, 50)
		self._add_row(form, "exp_radial_speed", "径向速度:", self._spin_exp_radial_speed, 2.0)
		self._spin_exp_count = QSpinBox()
		self._spin_exp_count.setRange(1, 10000)
		self._add_row(form, "exp_count", "粒子数:", self._spin_exp_count, 50)
		self._spin_exp_lifetime = QDoubleSpinBox()
		self._spin_exp_lifetime.setRange(0.1, 60)
		self._add_row(form, "exp_lifetime", "粒子寿命:", self._spin_exp_lifetime, 1.5)
		self._spin_exp_duration = QDoubleSpinBox()
		self._spin_exp_duration.setRange(0.1, 60)
		self._add_row(form, "exp_duration", "持续时长:", self._spin_exp_duration, 1.5)
		self.layout().addWidget(self._group_exp)

	def _setup_single_layer_group(self) -> None:
		self._group_sl = QGroupBox("单层烟花参数")
		form = QFormLayout(self._group_sl)
		self._spin_sl_speed = QDoubleSpinBox()
		self._spin_sl_speed.setRange(0.1, 100)
		self._add_row(form, "sl_speed", "速度:", self._spin_sl_speed, 8.0)
		self._spin_sl_count = QSpinBox()
		self._spin_sl_count.setRange(1, 10000)
		self._add_row(form, "sl_count", "粒子数:", self._spin_sl_count, 50)
		self._spin_sl_lifetime = QDoubleSpinBox()
		self._spin_sl_lifetime.setRange(0.1, 60)
		self._add_row(form, "sl_lifetime", "粒子寿命:", self._spin_sl_lifetime, 1.5)
		self._spin_sl_duration = QDoubleSpinBox()
		self._spin_sl_duration.setRange(0.1, 60)
		self._add_row(form, "sl_duration", "持续时长:", self._spin_sl_duration, 1.5)
		self.layout().addWidget(self._group_sl)

	def _on_type_changed(self) -> None:
		if self._loading:
			return
		self._hide_all()
		self._group_type_selector.show()
		self._secondary_color_group.show()
		st = self._combo_type.currentData()
		log.debug(f"二级爆炸类型切换: {st}")
		if st == "expanding":
			self._group_exp.show()
		elif st == "single_layer":
			self._group_sl.show()
		if self._element is not None:
			self._element.se_secondary_type = st
		self._update_reset_buttons()

	def _load_type_params(self, elem: CompositeElement) -> None:
		self._group_type_selector.show()
		self._secondary_color_group.show()

		idx = self._combo_type.findData(elem.se_secondary_type)
		if idx >= 0:
			self._combo_type.setCurrentIndex(idx)

		c = elem.se_secondary_color
		self._color_start.set_color(c.start)
		self._color_end.set_color(c.end)
		self._chk_gradient.setChecked(c.use_gradient)
		self._color_end.setEnabled(c.use_gradient)

		self._spin_exp_radius.setValue(elem.se_secondary_radius)
		self._spin_exp_radial_speed.setValue(elem.se_secondary_radial_speed)
		self._spin_exp_count.setValue(elem.se_secondary_count)
		self._spin_exp_lifetime.setValue(elem.se_secondary_lifetime)
		self._spin_exp_duration.setValue(elem.se_secondary_duration)

		self._spin_sl_speed.setValue(elem.se_secondary_speed)
		self._spin_sl_count.setValue(elem.se_secondary_count)
		self._spin_sl_lifetime.setValue(elem.se_secondary_lifetime)
		self._spin_sl_duration.setValue(elem.se_secondary_duration)

		st = elem.se_secondary_type
		if st == "expanding":
			self._group_exp.show()
		elif st == "single_layer":
			self._group_sl.show()

	def _on_extra_changed(self) -> None:
		if self._loading or self._element is None:
			return
		log.debug(f"二级爆炸参数变更: type={self._combo_type.currentData()}")
		e = self._element

		c = e.se_secondary_color
		c.use_gradient = self._chk_gradient.isChecked()
		sc = self._color_start.color
		c.start = ColorRGB(r=sc.r, g=sc.g, b=sc.b)
		ec = self._color_end.color
		c.end = ColorRGB(r=ec.r, g=ec.g, b=ec.b)

		st = self._combo_type.currentData()
		if st == "expanding":
			e.se_secondary_radius = self._spin_exp_radius.value()
			e.se_secondary_radial_speed = self._spin_exp_radial_speed.value()
			e.se_secondary_count = self._spin_exp_count.value()
			e.se_secondary_lifetime = self._spin_exp_lifetime.value()
			e.se_secondary_duration = self._spin_exp_duration.value()
		elif st == "single_layer":
			e.se_secondary_speed = self._spin_sl_speed.value()
			e.se_secondary_count = self._spin_sl_count.value()
			e.se_secondary_lifetime = self._spin_sl_lifetime.value()
			e.se_secondary_duration = self._spin_sl_duration.value()

		self._emit("extra", None)
