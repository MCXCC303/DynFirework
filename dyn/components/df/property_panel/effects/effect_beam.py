"""df 光束效果表单."""
from __future__ import annotations

from PySide6.QtWidgets import QFormLayout, QSpinBox, QDoubleSpinBox, QGroupBox

from dyn.components.df.property_panel.effects.effect_base import EffectBase
from dyn.models.df.values import ColorRGB

class BeamForm(EffectBase):
	"""光束效果表单."""

	def _setup_type_params(self):
		self._grp_beam_start, self._cp_beam_start_begin, self._cp_beam_start_end, self._chk_beam_start_grad = self._add_color_group("起始颜色")
		self._grp_beam_end, self._cp_beam_end_begin, self._cp_beam_end_end, self._chk_beam_end_grad = self._add_color_group("结束颜色")

		self._grp_speed = QGroupBox("速度")
		form_speed = QFormLayout(self._grp_speed)
		self._spin_beam_min_speed = QDoubleSpinBox()
		self._spin_beam_min_speed.setRange(0.1, 50)
		self._add_row(form_speed, "beam_min_speed", "最小速度:", self._spin_beam_min_speed, 1.0)
		self._spin_beam_max_speed = QDoubleSpinBox()
		self._spin_beam_max_speed.setRange(0.1, 50)
		self._add_row(form_speed, "beam_max_speed", "最大速度:", self._spin_beam_max_speed, 3.0)
		self.layout().addWidget(self._grp_speed)

		self._grp_direction = QGroupBox("方向")
		form_dir = QFormLayout(self._grp_direction)
		self._spin_beam_h_angle = QDoubleSpinBox()
		self._spin_beam_h_angle.setRange(0, 360)
		self._add_row(form_dir, "beam_h_angle", "水平角度:", self._spin_beam_h_angle, 0.0)
		self._spin_beam_v_angle = QDoubleSpinBox()
		self._spin_beam_v_angle.setRange(0, 180)
		self._add_row(form_dir, "beam_v_angle", "垂直角度:", self._spin_beam_v_angle, 0.0)
		self._spin_beam_spread_angle = QDoubleSpinBox()
		self._spin_beam_spread_angle.setRange(1, 180)
		self._add_row(form_dir, "beam_spread_angle", "散布角度:", self._spin_beam_spread_angle, 15.0)
		self.layout().addWidget(self._grp_direction)

		self._grp_particle = QGroupBox("粒子")
		form_part = QFormLayout(self._grp_particle)
		self._spin_beam_count = QSpinBox()
		self._spin_beam_count.setRange(1, 500)
		self._add_row(form_part, "beam_count", "数量:", self._spin_beam_count, 8)
		self._spin_beam_particles_per = QSpinBox()
		self._spin_beam_particles_per.setRange(1, 100)
		self._add_row(form_part, "beam_particles_per", "每粒子数:", self._spin_beam_particles_per, 10)
		self._spin_beam_lifetime = QDoubleSpinBox()
		self._spin_beam_lifetime.setRange(0.1, 60)
		self._add_row(form_part, "beam_lifetime", "生命周期:", self._spin_beam_lifetime, 2.0)
		self.layout().addWidget(self._grp_particle)

		for w in (self._spin_beam_min_speed, self._spin_beam_max_speed,
		          self._spin_beam_h_angle, self._spin_beam_v_angle, self._spin_beam_spread_angle,
		          self._spin_beam_count, self._spin_beam_particles_per, self._spin_beam_lifetime):
			w.valueChanged.connect(self._on_extra_changed)
		self._cp_beam_start_begin.color_changed.connect(self._on_extra_changed)
		self._cp_beam_start_end.color_changed.connect(self._on_extra_changed)
		self._cp_beam_end_begin.color_changed.connect(self._on_extra_changed)
		self._cp_beam_end_end.color_changed.connect(self._on_extra_changed)
		self._chk_beam_start_grad.toggled.connect(self._on_extra_changed)
		self._chk_beam_end_grad.toggled.connect(self._on_extra_changed)

		self._sub_groups = [
			self._grp_beam_start, self._grp_beam_end,
			self._grp_speed, self._grp_direction, self._grp_particle,
		]

	def _load_type_params(self, elem):
		self._grp_beam_start.show()
		self._grp_beam_end.show()
		self._grp_speed.show()
		self._grp_direction.show()
		self._grp_particle.show()

		self._cp_beam_start_begin.set_color(elem.beam_start_color.start)
		self._cp_beam_start_end.set_color(elem.beam_start_color.end)
		self._cp_beam_end_begin.set_color(elem.beam_end_color.start)
		self._cp_beam_end_end.set_color(elem.beam_end_color.end)
		self._chk_beam_start_grad.setChecked(elem.beam_start_color.use_gradient)
		self._cp_beam_end_end.setEnabled(elem.beam_start_color.use_gradient)
		self._chk_beam_end_grad.setChecked(elem.beam_end_color.use_gradient)
		self._cp_beam_end_end.setEnabled(elem.beam_end_color.use_gradient)
		self._spin_beam_min_speed.setValue(elem.beam_min_speed)
		self._spin_beam_max_speed.setValue(elem.beam_max_speed)
		self._spin_beam_h_angle.setValue(elem.beam_h_angle)
		self._spin_beam_v_angle.setValue(elem.beam_v_angle)
		self._spin_beam_spread_angle.setValue(elem.beam_spread_angle)
		self._spin_beam_count.setValue(elem.beam_count)
		self._spin_beam_particles_per.setValue(elem.beam_particles_per)
		self._spin_beam_lifetime.setValue(elem.beam_lifetime)

	def _on_extra_changed(self):
		if self._loading or self._element is None:
			return
		e = self._element
		c = self._cp_beam_start_begin.color; e.beam_start_color.start = ColorRGB(r=c.r, g=c.g, b=c.b)
		c = self._cp_beam_start_end.color; e.beam_start_color.end = ColorRGB(r=c.r, g=c.g, b=c.b)
		c = self._cp_beam_end_begin.color; e.beam_end_color.start = ColorRGB(r=c.r, g=c.g, b=c.b)
		c = self._cp_beam_end_end.color; e.beam_end_color.end = ColorRGB(r=c.r, g=c.g, b=c.b)
		e.beam_start_color.use_gradient = self._chk_beam_start_grad.isChecked()
		e.beam_end_color.use_gradient = self._chk_beam_end_grad.isChecked()
		e.beam_min_speed = self._spin_beam_min_speed.value()
		e.beam_max_speed = self._spin_beam_max_speed.value()
		e.beam_h_angle = self._spin_beam_h_angle.value()
		e.beam_v_angle = self._spin_beam_v_angle.value()
		e.beam_spread_angle = self._spin_beam_spread_angle.value()
		e.beam_count = self._spin_beam_count.value()
		e.beam_particles_per = self._spin_beam_particles_per.value()
		e.beam_lifetime = self._spin_beam_lifetime.value()
		self._emit("extra", None)
