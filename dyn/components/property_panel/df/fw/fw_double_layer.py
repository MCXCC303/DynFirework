"""df 双层烟花表单."""
from __future__ import annotations

from PySide6.QtWidgets import QFormLayout, QSpinBox, QDoubleSpinBox, QGroupBox

from dyn.components.property_panel.df.fw.fw_base import FwBase
from dyn.models.df.fireworks import FireworkElement as FireworkElementV2

class DoubleLayerForm(FwBase):
	"""双层烟花参数表单."""

	def _setup_type_sections(self) -> None:
		self._group_params = QGroupBox("烟花参数")
		form = QFormLayout(self._group_params)

		self._spin_inner_speed = QDoubleSpinBox()
		self._spin_inner_speed.setRange(0.1, 100)
		self._spin_inner_speed.setSingleStep(0.5)
		self._add_row(form, "inner_speed", "内层速度:", self._spin_inner_speed, default=8.0)

		self._spin_outer_speed = QDoubleSpinBox()
		self._spin_outer_speed.setRange(0.1, 100)
		self._spin_outer_speed.setSingleStep(0.5)
		self._add_row(form, "outer_speed", "外层速度:", self._spin_outer_speed, default=10.0)

		self._spin_inner_count = QSpinBox()
		self._spin_inner_count.setRange(1, 10000)
		self._add_row(form, "inner_count", "内层粒子数:", self._spin_inner_count, default=80)

		self._spin_outer_count = QSpinBox()
		self._spin_outer_count.setRange(1, 10000)
		self._add_row(form, "outer_count", "外层粒子数:", self._spin_outer_count, default=120)

		self._spin_inner_speed.valueChanged.connect(self._on_extra_changed)
		self._spin_outer_speed.valueChanged.connect(self._on_extra_changed)
		self._spin_inner_count.valueChanged.connect(self._on_extra_changed)
		self._spin_outer_count.valueChanged.connect(self._on_extra_changed)
		self._spin_h_angle.valueChanged.connect(self._on_extra_changed)
		self._spin_v_angle.valueChanged.connect(self._on_extra_changed)

		self.layout().addWidget(self._group_params)
		self._sub_groups = [self._group_params]

	def _load_type_sections(self, elem: FireworkElementV2) -> None:
		self._group_angle.show()
		self._group_outer.show()
		self._group_params.show()
		self._spin_h_angle.setValue(elem.horizontal_angle)
		self._spin_v_angle.setValue(elem.vertical_angle)
		self._chk_outer_gradient.setChecked(elem.outer_color.use_gradient)
		self._color_outer_end.setEnabled(elem.outer_color.use_gradient)
		self._color_outer_start.set_color(elem.outer_color.start)
		self._color_outer_end.set_color(elem.outer_color.end)
		self._spin_inner_speed.setValue(elem.inner_speed)
		self._spin_outer_speed.setValue(elem.outer_speed)
		self._spin_inner_count.setValue(elem.inner_count)
		self._spin_outer_count.setValue(elem.outer_count)

	def _on_extra_changed(self) -> None:
		if self._loading or self._element is None:
			return
		self._element.inner_speed = self._spin_inner_speed.value()
		self._element.outer_speed = self._spin_outer_speed.value()
		self._element.inner_count = self._spin_inner_count.value()
		self._element.outer_count = self._spin_outer_count.value()
		self._element.horizontal_angle = self._spin_h_angle.value()
		self._element.vertical_angle = self._spin_v_angle.value()
		self._emit("extra", None)
