"""SubExpandingForm - 膨胀球子表单 固定 expanding_sphere 类型."""
from __future__ import annotations

from PySide6.QtWidgets import (
	QFormLayout, QSpinBox, QDoubleSpinBox, QCheckBox, QGroupBox,
)

from dyn.models.df.composites import CompositeElement
from dyn.models.df.values import ColorRGB
from ..composite_base import CompositeBase

class SubExpandingForm(CompositeBase):
	"""膨胀球子表单 无类型选择器 固定显示 expanding_sphere 参数."""

	def __init__(self, parent=None) -> None:
		super().__init__(parent, has_position=False)

	def _setup_type_params(self) -> None:
		self._group_params = QGroupBox("膨胀球参数")
		form = QFormLayout(self._group_params)

		self._spin_radius = QDoubleSpinBox()
		self._spin_radius.setRange(0.1, 100)
		self._add_row(form, "radius", "半径:", self._spin_radius, 3.0)
		self._spin_radial_speed = QDoubleSpinBox()
		self._spin_radial_speed.setRange(0.1, 50)
		self._add_row(form, "radial_speed", "径向速度:", self._spin_radial_speed, 2.0)
		self._spin_count = QSpinBox()
		self._spin_count.setRange(1, 10000)
		self._add_row(form, "count", "粒子数:", self._spin_count, 100)
		self._chk_flicker = QCheckBox("启用闪烁")
		form.addRow("", self._chk_flicker)
		self.layout().addWidget(self._group_params)

		self._sphere_color_group, self._color_start, self._color_end, self._chk_gradient = \
			self._add_color_group("颜色")

		for w in (
				self._spin_radius, self._spin_radial_speed, self._spin_count,
		):
			w.valueChanged.connect(self._on_extra_changed)

		self._chk_flicker.toggled.connect(self._on_extra_changed)
		self._color_start.color_changed.connect(lambda c: self._on_extra_changed())
		self._color_end.color_changed.connect(lambda c: self._on_extra_changed())
		self._chk_gradient.toggled.connect(self._on_extra_changed)

		self._sub_groups = [
			self._group_params,
			self._sphere_color_group,
		]

	def _load_type_params(self, elem: CompositeElement) -> None:
		self._group_params.show()
		self._sphere_color_group.show()

		self._spin_radius.setValue(elem.ce_sphere_radius)
		self._spin_radial_speed.setValue(elem.ce_sphere_radial_speed)
		self._spin_count.setValue(elem.ce_sphere_count)
		self._chk_flicker.setChecked(elem.ce_flicker)

		c = elem.ce_sphere_color
		self._color_start.set_color(c.start)
		self._color_end.set_color(c.end)
		self._chk_gradient.setChecked(c.use_gradient)
		self._color_end.setEnabled(c.use_gradient)

	def _on_extra_changed(self) -> None:
		if self._loading or self._element is None:
			return
		e = self._element

		c = e.ce_sphere_color
		c.use_gradient = self._chk_gradient.isChecked()
		sc = self._color_start.color
		c.start = ColorRGB(r=sc.r, g=sc.g, b=sc.b)
		ec = self._color_end.color
		c.end = ColorRGB(r=ec.r, g=ec.g, b=ec.b)

		e.ce_sphere_radius = self._spin_radius.value()
		e.ce_sphere_radial_speed = self._spin_radial_speed.value()
		e.ce_sphere_count = self._spin_count.value()
		e.ce_flicker = self._chk_flicker.isChecked()

		self._emit("extra", None)
