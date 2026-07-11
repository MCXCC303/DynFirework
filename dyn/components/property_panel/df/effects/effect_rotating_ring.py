"""df 旋转光环效果表单."""
from __future__ import annotations

from PySide6.QtWidgets import QFormLayout, QSpinBox, QDoubleSpinBox, QGroupBox

from dyn.components.property_panel.df.effects.effect_base import EffectBase

class RotatingRingForm(EffectBase):
	"""旋转光环效果表单."""

	def _setup_type_params(self):
		self._grp_color, self._cp_color_begin, self._cp_color_end = self._add_color_group("颜色")

		self._grp_ring = QGroupBox("环参数")
		form_ring = QFormLayout(self._grp_ring)
		self._spin_rr_ring_radius = QDoubleSpinBox()
		self._spin_rr_ring_radius.setRange(0.1, 50)
		self._spin_rr_ring_radius.setSingleStep(0.5)
		self._add_row(form_ring, "rr_ring_radius", "环半径:", self._spin_rr_ring_radius, 3.0)
		self._spin_rr_tube_radius = QDoubleSpinBox()
		self._spin_rr_tube_radius.setRange(0.1, 20)
		self._spin_rr_tube_radius.setSingleStep(0.1)
		self._add_row(form_ring, "rr_tube_radius", "管径:", self._spin_rr_tube_radius, 0.5)
		self._spin_rr_rotation_speed = QDoubleSpinBox()
		self._spin_rr_rotation_speed.setRange(0.1, 30)
		self._add_row(form_ring, "rr_rotation_speed", "旋转速度:", self._spin_rr_rotation_speed, 2.0)
		self._spin_rr_density = QSpinBox()
		self._spin_rr_density.setRange(1, 200)
		self._add_row(form_ring, "rr_density", "密度:", self._spin_rr_density, 30)
		self.layout().addWidget(self._grp_ring)

		self._grp_radial = QGroupBox("径向速度")
		form_radial = QFormLayout(self._grp_radial)
		self._spin_rr_radial_velocity = QDoubleSpinBox()
		self._spin_rr_radial_velocity.setRange(0, 30)
		self._spin_rr_radial_velocity.setSingleStep(0.5)
		self._add_row(form_radial, "rr_radial_velocity", "径向速度:", self._spin_rr_radial_velocity, 1.0)
		self.layout().addWidget(self._grp_radial)

		self._grp_time = QGroupBox("时间")
		form_time = QFormLayout(self._grp_time)
		self._spin_rr_lifetime = QDoubleSpinBox()
		self._spin_rr_lifetime.setRange(0.1, 60)
		self._add_row(form_time, "rr_lifetime", "粒子寿命:", self._spin_rr_lifetime, 3.0)
		self._spin_rr_duration_ticks = QSpinBox()
		self._spin_rr_duration_ticks.setRange(1, 10000)
		self._add_row(form_time, "rr_duration_ticks", "持续 tick:", self._spin_rr_duration_ticks, 100)
		self.layout().addWidget(self._grp_time)

		for w in (self._spin_rr_ring_radius, self._spin_rr_tube_radius, self._spin_rr_rotation_speed,
		          self._spin_rr_density, self._spin_rr_radial_velocity,
		          self._spin_rr_lifetime, self._spin_rr_duration_ticks):
			w.valueChanged.connect(self._on_extra_changed)
		self._cp_color_begin.color_changed.connect(self._on_extra_changed)
		self._cp_color_end.color_changed.connect(self._on_extra_changed)

		self._sub_groups = [
			self._grp_color,
			self._grp_ring, self._grp_radial, self._grp_time,
		]

	def _load_type_params(self, elem):
		self._grp_color.show()
		self._grp_ring.show()
		self._grp_radial.show()
		self._grp_time.show()

		self._cp_color_begin.set_color(elem.rr_color.start)
		self._cp_color_end.set_color(elem.rr_color.end)
		self._spin_rr_ring_radius.setValue(elem.rr_ring_radius)
		self._spin_rr_tube_radius.setValue(elem.rr_tube_radius)
		self._spin_rr_rotation_speed.setValue(elem.rr_rotation_speed)
		self._spin_rr_density.setValue(elem.rr_density)
		self._spin_rr_radial_velocity.setValue(elem.rr_radial_velocity)
		self._spin_rr_lifetime.setValue(elem.rr_lifetime)
		self._spin_rr_duration_ticks.setValue(elem.rr_duration_ticks)

	def _on_extra_changed(self):
		if self._loading or self._element is None:
			return
		e = self._element
		e.rr_color.start = self._cp_color_begin.color
		e.rr_color.end = self._cp_color_end.color
		e.rr_ring_radius = self._spin_rr_ring_radius.value()
		e.rr_tube_radius = self._spin_rr_tube_radius.value()
		e.rr_rotation_speed = self._spin_rr_rotation_speed.value()
		e.rr_density = self._spin_rr_density.value()
		e.rr_radial_velocity = self._spin_rr_radial_velocity.value()
		e.rr_lifetime = self._spin_rr_lifetime.value()
		e.rr_duration_ticks = self._spin_rr_duration_ticks.value()
		self._emit("extra", None)
