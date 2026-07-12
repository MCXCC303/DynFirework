"""df 喷射效果表单."""
from __future__ import annotations

from PySide6.QtWidgets import QFormLayout, QSpinBox, QDoubleSpinBox, QGroupBox

from dyn.components.df.property_panel.effects.effect_base import EffectBase
from dyn.models.df.values import ColorRGB

class SprayForm(EffectBase):
	"""喷射效果表单."""

	def _setup_type_params(self):
		self._grp_spray_start, self._cp_spray_start_begin, self._cp_spray_start_end, self._chk_spray_start_grad = self._add_color_group("起始颜色")
		self._grp_spray_end, self._cp_spray_end_begin, self._cp_spray_end_end, self._chk_spray_end_grad = self._add_color_group("结束颜色")

		self._grp_speed = QGroupBox("速度")
		form_speed = QFormLayout(self._grp_speed)
		self._spin_spray_min_speed = QDoubleSpinBox()
		self._spin_spray_min_speed.setRange(0.1, 50)
		self._add_row(form_speed, "spray_min_speed", "最小速度:", self._spin_spray_min_speed, 1.0)
		self._spin_spray_max_speed = QDoubleSpinBox()
		self._spin_spray_max_speed.setRange(0.1, 50)
		self._add_row(form_speed, "spray_max_speed", "最大速度:", self._spin_spray_max_speed, 3.0)
		self.layout().addWidget(self._grp_speed)

		self._grp_direction = QGroupBox("方向")
		form_dir = QFormLayout(self._grp_direction)
		self._spin_spray_h_angle = QDoubleSpinBox()
		self._spin_spray_h_angle.setRange(0, 360)
		self._add_row(form_dir, "spray_h_angle", "水平角度:", self._spin_spray_h_angle, 0.0)
		self._spin_spray_v_angle = QDoubleSpinBox()
		self._spin_spray_v_angle.setRange(0, 180)
		self._add_row(form_dir, "spray_v_angle", "垂直角度:", self._spin_spray_v_angle, 0.0)
		self._spin_spray_cone_angle = QDoubleSpinBox()
		self._spin_spray_cone_angle.setRange(1, 180)
		self._add_row(form_dir, "spray_cone_angle", "锥角:", self._spin_spray_cone_angle, 15.0)
		self.layout().addWidget(self._grp_direction)

		self._grp_spray = QGroupBox("喷射")
		form_spray = QFormLayout(self._grp_spray)
		self._spin_spray_duration_ticks = QSpinBox()
		self._spin_spray_duration_ticks.setRange(1, 10000)
		self._add_row(form_spray, "spray_duration_ticks", "持续 tick:", self._spin_spray_duration_ticks, 40)
		self._spin_spray_particles_per_tick = QSpinBox()
		self._spin_spray_particles_per_tick.setRange(1, 100)
		self._add_row(form_spray, "spray_particles_per_tick", "每 tick 粒子:", self._spin_spray_particles_per_tick, 3)
		self._spin_spray_particle_lifetime_ticks = QSpinBox()
		self._spin_spray_particle_lifetime_ticks.setRange(1, 200)
		self._add_row(form_spray, "spray_particle_lifetime_ticks", "粒子寿命 tick:", self._spin_spray_particle_lifetime_ticks, 20)
		self.layout().addWidget(self._grp_spray)

		for w in (self._spin_spray_min_speed, self._spin_spray_max_speed,
		          self._spin_spray_h_angle, self._spin_spray_v_angle, self._spin_spray_cone_angle,
		          self._spin_spray_duration_ticks, self._spin_spray_particles_per_tick,
		          self._spin_spray_particle_lifetime_ticks):
			w.valueChanged.connect(self._on_extra_changed)
		self._cp_spray_start_begin.color_changed.connect(self._on_extra_changed)
		self._cp_spray_start_end.color_changed.connect(self._on_extra_changed)
		self._cp_spray_end_begin.color_changed.connect(self._on_extra_changed)
		self._cp_spray_end_end.color_changed.connect(self._on_extra_changed)
		self._chk_spray_start_grad.toggled.connect(self._on_extra_changed)
		self._chk_spray_end_grad.toggled.connect(self._on_extra_changed)

		self._sub_groups = [
			self._grp_spray_start, self._grp_spray_end,
			self._grp_speed, self._grp_direction, self._grp_spray,
		]

	def _load_type_params(self, elem):
		self._grp_spray_start.show()
		self._grp_spray_end.show()
		self._grp_speed.show()
		self._grp_direction.show()
		self._grp_spray.show()

		self._cp_spray_start_begin.set_color(elem.spray_start_color.start)
		self._cp_spray_start_end.set_color(elem.spray_start_color.end)
		self._cp_spray_end_begin.set_color(elem.spray_end_color.start)
		self._cp_spray_end_end.set_color(elem.spray_end_color.end)
		self._chk_spray_start_grad.setChecked(elem.spray_start_color.use_gradient)
		self._cp_spray_end_end.setEnabled(elem.spray_start_color.use_gradient)
		self._chk_spray_end_grad.setChecked(elem.spray_end_color.use_gradient)
		self._cp_spray_end_end.setEnabled(elem.spray_end_color.use_gradient)
		self._spin_spray_min_speed.setValue(elem.spray_min_speed)
		self._spin_spray_max_speed.setValue(elem.spray_max_speed)
		self._spin_spray_h_angle.setValue(elem.spray_h_angle)
		self._spin_spray_v_angle.setValue(elem.spray_v_angle)
		self._spin_spray_cone_angle.setValue(elem.spray_cone_angle)
		self._spin_spray_duration_ticks.setValue(elem.spray_duration_ticks)
		self._spin_spray_particles_per_tick.setValue(elem.spray_particles_per_tick)
		self._spin_spray_particle_lifetime_ticks.setValue(elem.spray_particle_lifetime_ticks)

	def _on_extra_changed(self):
		if self._loading or self._element is None:
			return
		e = self._element
		c = self._cp_spray_start_begin.color; e.spray_start_color.start = ColorRGB(r=c.r, g=c.g, b=c.b)
		c = self._cp_spray_start_end.color; e.spray_start_color.end = ColorRGB(r=c.r, g=c.g, b=c.b)
		c = self._cp_spray_end_begin.color; e.spray_end_color.start = ColorRGB(r=c.r, g=c.g, b=c.b)
		c = self._cp_spray_end_end.color; e.spray_end_color.end = ColorRGB(r=c.r, g=c.g, b=c.b)
		e.spray_start_color.use_gradient = self._chk_spray_start_grad.isChecked()
		e.spray_end_color.use_gradient = self._chk_spray_end_grad.isChecked()
		e.spray_min_speed = self._spin_spray_min_speed.value()
		e.spray_max_speed = self._spin_spray_max_speed.value()
		e.spray_h_angle = self._spin_spray_h_angle.value()
		e.spray_v_angle = self._spin_spray_v_angle.value()
		e.spray_cone_angle = self._spin_spray_cone_angle.value()
		e.spray_duration_ticks = self._spin_spray_duration_ticks.value()
		e.spray_particles_per_tick = self._spin_spray_particles_per_tick.value()
		e.spray_particle_lifetime_ticks = self._spin_spray_particle_lifetime_ticks.value()
		self._emit("extra", None)
