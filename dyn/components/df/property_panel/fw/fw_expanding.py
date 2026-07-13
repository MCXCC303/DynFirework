"""df 膨胀球烟花表单."""
from __future__ import annotations

from PySide6.QtWidgets import QFormLayout, QSpinBox, QDoubleSpinBox, QGroupBox

from dyn.components.df.property_panel.fw.fw_base import FwBase
from dyn.models.df.fireworks import FireworkElement

class ExpandingForm(FwBase):
	"""膨胀球烟花参数表单."""

	def _setup_type_sections(self) -> None:
		self._group_params = QGroupBox("烟花参数")
		form = QFormLayout(self._group_params)

		self._spin_radius = QDoubleSpinBox()
		self._spin_radius.setRange(0.1, 100)
		self._spin_radius.setSingleStep(0.5)
		self._add_row(form, "radius", "半径:", self._spin_radius, default=5.0)

		self._spin_radial_speed = QDoubleSpinBox()
		self._spin_radial_speed.setRange(0.1, 50)
		self._spin_radial_speed.setSingleStep(0.5)
		self._add_row(form, "radial_speed", "径向速度:", self._spin_radial_speed, default=3.0)

		self._spin_count = QSpinBox()
		self._spin_count.setRange(1, 10000)
		self._add_row(form, "particle_count", "粒子数:", self._spin_count, default=100)

		self._spin_radius.valueChanged.connect(self._on_extra_changed)
		self._spin_radial_speed.valueChanged.connect(self._on_extra_changed)
		self._spin_count.valueChanged.connect(self._on_extra_changed)

		self.layout().addWidget(self._group_params)
		self._sub_groups = [self._group_params]

	def _load_type_sections(self, elem: FireworkElement) -> None:
		self._group_params.show()
		self._spin_radius.setValue(elem.radius)
		self._spin_radial_speed.setValue(elem.radial_speed)
		self._spin_count.setValue(elem.particle_count)

	def _on_extra_changed(self) -> None:
		if self._loading or self._element is None:
			return
		self._element.radius = self._spin_radius.value()
		self._element.radial_speed = self._spin_radial_speed.value()
		self._element.particle_count = self._spin_count.value()
		self._emit("extra", None)
