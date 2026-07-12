"""df 双螺旋效果表单."""
from __future__ import annotations

from PySide6.QtWidgets import QFormLayout, QSpinBox, QDoubleSpinBox, QGroupBox

from dyn.components.df.property_panel.effects.effect_base import EffectBase
from dyn.models.df.values import ColorRGB

class DoubleHelixForm(EffectBase):
	"""双螺旋效果表单."""

	def _setup_type_params(self):
		self._grp_color1, self._cp_color1_begin, self._cp_color1_end, self._chk_color1_grad = self._add_color_group("颜色1")
		self._grp_color2, self._cp_color2_begin, self._cp_color2_end, self._chk_color2_grad = self._add_color_group("颜色2")

		self._grp_helix = QGroupBox("螺旋参数")
		form_helix = QFormLayout(self._grp_helix)
		self._spin_dh_radius = QDoubleSpinBox()
		self._spin_dh_radius.setRange(0.1, 50)
		self._spin_dh_radius.setSingleStep(0.5)
		self._add_row(form_helix, "dh_radius", "半径:", self._spin_dh_radius, 2.0)
		self._spin_dh_rise_speed = QDoubleSpinBox()
		self._spin_dh_rise_speed.setRange(0.1, 30)
		self._add_row(form_helix, "dh_rise_speed", "上升速度:", self._spin_dh_rise_speed, 3.0)
		self._spin_dh_rotation_speed = QDoubleSpinBox()
		self._spin_dh_rotation_speed.setRange(0.1, 30)
		self._add_row(form_helix, "dh_rotation_speed", "旋转速度:", self._spin_dh_rotation_speed, 5.0)
		self._spin_dh_density = QSpinBox()
		self._spin_dh_density.setRange(1, 200)
		self._add_row(form_helix, "dh_density", "密度:", self._spin_dh_density, 20)
		self.layout().addWidget(self._grp_helix)

		self._grp_vy = QGroupBox("垂直速度")
		form_vy = QFormLayout(self._grp_vy)
		self._spin_dh_min_vy = QDoubleSpinBox()
		self._spin_dh_min_vy.setRange(-50, 50)
		self._spin_dh_min_vy.setSingleStep(0.5)
		self._add_row(form_vy, "dh_min_vy", "最小垂直速度:", self._spin_dh_min_vy, 0.0)
		self._spin_dh_max_vy = QDoubleSpinBox()
		self._spin_dh_max_vy.setRange(-50, 50)
		self._spin_dh_max_vy.setSingleStep(0.5)
		self._add_row(form_vy, "dh_max_vy", "最大垂直速度:", self._spin_dh_max_vy, 1.0)
		self.layout().addWidget(self._grp_vy)

		self._grp_time = QGroupBox("时间")
		form_time = QFormLayout(self._grp_time)
		self._spin_dh_lifetime = QDoubleSpinBox()
		self._spin_dh_lifetime.setRange(0.1, 60)
		self._add_row(form_time, "dh_lifetime", "粒子寿命:", self._spin_dh_lifetime, 2.0)
		self._spin_dh_duration_ticks = QSpinBox()
		self._spin_dh_duration_ticks.setRange(1, 10000)
		self._add_row(form_time, "dh_duration_ticks", "持续 tick:", self._spin_dh_duration_ticks, 100)
		self.layout().addWidget(self._grp_time)

		for w in (self._spin_dh_radius, self._spin_dh_rise_speed, self._spin_dh_rotation_speed,
		          self._spin_dh_density, self._spin_dh_min_vy, self._spin_dh_max_vy,
		          self._spin_dh_lifetime, self._spin_dh_duration_ticks):
			w.valueChanged.connect(self._on_extra_changed)
		self._cp_color1_begin.color_changed.connect(self._on_extra_changed)
		self._cp_color1_end.color_changed.connect(self._on_extra_changed)
		self._cp_color2_begin.color_changed.connect(self._on_extra_changed)
		self._cp_color2_end.color_changed.connect(self._on_extra_changed)
		self._chk_color1_grad.toggled.connect(self._on_extra_changed)
		self._chk_color2_grad.toggled.connect(self._on_extra_changed)

		self._sub_groups = [
			self._grp_color1, self._grp_color2,
			self._grp_helix, self._grp_vy, self._grp_time,
		]

	def _load_type_params(self, elem):
		self._grp_color1.show()
		self._grp_color2.show()
		self._grp_helix.show()
		self._grp_vy.show()
		self._grp_time.show()

		self._cp_color1_begin.set_color(elem.dh_color1.start)
		self._cp_color1_end.set_color(elem.dh_color1.end)
		self._cp_color2_begin.set_color(elem.dh_color2.start)
		self._cp_color2_end.set_color(elem.dh_color2.end)
		self._chk_color1_grad.setChecked(elem.dh_color1.use_gradient)
		self._cp_color1_end.setEnabled(elem.dh_color1.use_gradient)
		self._chk_color2_grad.setChecked(elem.dh_color2.use_gradient)
		self._cp_color2_end.setEnabled(elem.dh_color2.use_gradient)
		self._spin_dh_radius.setValue(elem.dh_radius)
		self._spin_dh_rise_speed.setValue(elem.dh_rise_speed)
		self._spin_dh_rotation_speed.setValue(elem.dh_rotation_speed)
		self._spin_dh_density.setValue(elem.dh_density)
		self._spin_dh_min_vy.setValue(elem.dh_min_vy)
		self._spin_dh_max_vy.setValue(elem.dh_max_vy)
		self._spin_dh_lifetime.setValue(elem.dh_lifetime)
		self._spin_dh_duration_ticks.setValue(elem.dh_duration_ticks)

	def _on_extra_changed(self):
		if self._loading or self._element is None:
			return
		e = self._element
		c = self._cp_color1_begin.color; e.dh_color1.start = ColorRGB(r=c.r, g=c.g, b=c.b)
		c = self._cp_color1_end.color; e.dh_color1.end = ColorRGB(r=c.r, g=c.g, b=c.b)
		c = self._cp_color2_begin.color; e.dh_color2.start = ColorRGB(r=c.r, g=c.g, b=c.b)
		c = self._cp_color2_end.color; e.dh_color2.end = ColorRGB(r=c.r, g=c.g, b=c.b)
		e.dh_color1.use_gradient = self._chk_color1_grad.isChecked()
		e.dh_color2.use_gradient = self._chk_color2_grad.isChecked()
		e.dh_radius = self._spin_dh_radius.value()
		e.dh_rise_speed = self._spin_dh_rise_speed.value()
		e.dh_rotation_speed = self._spin_dh_rotation_speed.value()
		e.dh_density = self._spin_dh_density.value()
		e.dh_min_vy = self._spin_dh_min_vy.value()
		e.dh_max_vy = self._spin_dh_max_vy.value()
		e.dh_lifetime = self._spin_dh_lifetime.value()
		e.dh_duration_ticks = self._spin_dh_duration_ticks.value()
		self._emit("extra", None)
