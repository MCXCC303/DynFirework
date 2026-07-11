"""双层烟花表单."""
from __future__ import annotations

from PySide6.QtWidgets import (
	QFormLayout, QDoubleSpinBox, QGroupBox,
)

from dyn.components.property_panel.particleex.fw.fw_base import FwBase
from dyn.models.elements import Element, FireworkElement, TrajFireworkElement

class DoubleLayerForm(FwBase):
	"""双层烟花 inner_speed, outer_speed, horizontal_angle, vertical_angle, 外层颜色."""

	def _setup_type_sections(self) -> None:
		self._group_angle.show()

		self._group_params = QGroupBox("烟花参数")
		form = QFormLayout(self._group_params)
		self._spin_inner_speed = QDoubleSpinBox()
		self._spin_inner_speed.setRange(0.1, 100)
		self._spin_inner_speed.setValue(8)
		self._add_row(form, "inner_speed", "内层速度:", self._spin_inner_speed, 8.0)
		self._spin_outer_speed = QDoubleSpinBox()
		self._spin_outer_speed.setRange(0.1, 100)
		self._spin_outer_speed.setValue(10)
		self._add_row(form, "outer_speed", "外层速度:", self._spin_outer_speed, 10.0)
		self.layout().addWidget(self._group_params)
		self._sub_groups = [self._group_params]

		for w in (self._spin_inner_speed, self._spin_outer_speed):
			w.valueChanged.connect(self._on_extra_changed)

	def _load_type_sections(self, e: Element) -> None:
		self._group_angle.show()
		self._group_outer.show()
		self._group_params.show()

		self._chk_outer_gradient.setChecked(e.outer_color.use_gradient)
		self._color_outer_end.setEnabled(e.outer_color.use_gradient)
		self._color_outer_start.set_color(e.outer_color.start)
		self._color_outer_end.set_color(e.outer_color.end)
		self._spin_h_angle.setValue(e.horizontal_angle)
		self._spin_v_angle.setValue(e.vertical_angle)
		self._spin_inner_speed.setValue(e.inner_speed)
		self._spin_outer_speed.setValue(e.outer_speed)

	def _on_extra_changed(self) -> None:
		if self._loading or self._element is None:
			return
		e = self._element
		if not isinstance(e, (FireworkElement, TrajFireworkElement)):
			return
		e.inner_speed = self._spin_inner_speed.value()
		e.outer_speed = self._spin_outer_speed.value()
		e.horizontal_angle = self._spin_h_angle.value()
		e.vertical_angle = self._spin_v_angle.value()
		self._emit("extra", None)
