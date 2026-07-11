"""二级爆炸表单 一级烟花 + 二级爆炸参数."""
from __future__ import annotations

from PySide6.QtWidgets import (
	QFormLayout, QSpinBox, QDoubleSpinBox, QComboBox, QGroupBox, )

from dyn.components.df.property_panel.composites.composite_base import CompositeBase
from dyn.models.df.composites import CompositeElement
from dyn.models.df.values import FireworkType

class SecondaryExplosionForm(CompositeBase):
	"""二级爆炸 初始/中间位置 + 一级烟花 + 二级爆炸."""

	def _setup_type_params(self) -> None:
		self._group_start = QGroupBox("初始位置")
		form = QFormLayout(self._group_start)
		self._spin_start_x = QDoubleSpinBox()
		self._spin_start_x.setRange(-100000, 100000)
		self._spin_start_x.setDecimals(2)
		self._add_row(form, "start_x", "X:", self._spin_start_x)
		self._spin_start_y = QDoubleSpinBox()
		self._spin_start_y.setRange(-64, 320)
		self._spin_start_y.setDecimals(2)
		self._add_row(form, "start_y", "Y:", self._spin_start_y)
		self._spin_start_z = QDoubleSpinBox()
		self._spin_start_z.setRange(-100000, 100000)
		self._spin_start_z.setDecimals(2)
		self._add_row(form, "start_z", "Z:", self._spin_start_z)
		self.layout().addWidget(self._group_start)

		self._group_mid = QGroupBox("中间位置")
		form = QFormLayout(self._group_mid)
		self._spin_mid_x = QDoubleSpinBox()
		self._spin_mid_x.setRange(-100000, 100000)
		self._spin_mid_x.setDecimals(2)
		self._add_row(form, "mid_x", "X:", self._spin_mid_x)
		self._spin_mid_y = QDoubleSpinBox()
		self._spin_mid_y.setRange(-64, 320)
		self._spin_mid_y.setDecimals(2)
		self._add_row(form, "mid_y", "Y:", self._spin_mid_y)
		self._spin_mid_z = QDoubleSpinBox()
		self._spin_mid_z.setRange(-100000, 100000)
		self._spin_mid_z.setDecimals(2)
		self._add_row(form, "mid_z", "Z:", self._spin_mid_z)
		self.layout().addWidget(self._group_mid)

		self._group_primary = QGroupBox("一级烟花")
		form = QFormLayout(self._group_primary)
		self._combo_primary_type = QComboBox()
		self._combo_primary_type.addItem("单层", FireworkType.SINGLE_LAYER)
		self._combo_primary_type.addItem("双层", FireworkType.DOUBLE_LAYER)
		self._combo_primary_type.addItem("定向", FireworkType.DIRECTIONAL)
		self._combo_primary_type.addItem("集束", FireworkType.CLUSTERED)
		self._combo_primary_type.addItem("膨胀球", FireworkType.EXPANDING_SPHERE)
		self._combo_primary_type.addItem("星云", FireworkType.NEBULA)
		self._add_row(form, "primary_type", "类型:", self._combo_primary_type, FireworkType.SINGLE_LAYER)
		self._combo_primary_type.currentIndexChanged.connect(self._on_extra_changed)
		self._primary_color_group, self._primary_color_start, self._primary_color_end = self._add_color_group("颜色")
		self._spin_primary_speed = QDoubleSpinBox()
		self._spin_primary_speed.setRange(0.1, 100)
		self._add_row(form, "primary_speed", "速度:", self._spin_primary_speed, 10.0)
		self._spin_primary_count = QSpinBox()
		self._spin_primary_count.setRange(1, 10000)
		self._add_row(form, "primary_count", "粒子数:", self._spin_primary_count, 100)
		self._spin_primary_duration = QDoubleSpinBox()
		self._spin_primary_duration.setRange(0.1, 60)
		self._add_row(form, "primary_duration", "持续时长:", self._spin_primary_duration, 2.0)
		self._spin_primary_lifetime = QDoubleSpinBox()
		self._spin_primary_lifetime.setRange(0.1, 60)
		self._add_row(form, "primary_lifetime", "粒子寿命:", self._spin_primary_lifetime, 2.0)
		self._spin_primary_track_count = QSpinBox()
		self._spin_primary_track_count.setRange(1, 100)
		self._add_row(form, "primary_track_count", "轨迹数:", self._spin_primary_track_count, 5)
		self._spin_primary_spread = QDoubleSpinBox()
		self._spin_primary_spread.setRange(1, 180)
		self._add_row(form, "primary_spread", "扩散角:", self._spin_primary_spread, 15.0)
		self._spin_primary_h_angle = QDoubleSpinBox()
		self._spin_primary_h_angle.setRange(0, 360)
		self._add_row(form, "primary_h_angle", "水平角:", self._spin_primary_h_angle, 30.0)
		self._spin_primary_v_angle = QDoubleSpinBox()
		self._spin_primary_v_angle.setRange(0, 180)
		self._add_row(form, "primary_v_angle", "垂直角:", self._spin_primary_v_angle, 30.0)
		self.layout().addWidget(self._group_primary)

		self._group_secondary = QGroupBox("二级爆炸")
		form = QFormLayout(self._group_secondary)
		self._combo_secondary_type = QComboBox()
		self._combo_secondary_type.addItem("膨胀球", "expanding")
		self._combo_secondary_type.addItem("单层烟花", "single_layer")
		self._add_row(form, "secondary_type", "类型:", self._combo_secondary_type, "expanding")
		self._combo_secondary_type.currentIndexChanged.connect(self._on_extra_changed)
		self._secondary_color_group, self._secondary_color_start, self._secondary_color_end = self._add_color_group("颜色")
		self._spin_secondary_radius = QDoubleSpinBox()
		self._spin_secondary_radius.setRange(0.1, 100)
		self._add_row(form, "secondary_radius", "半径:", self._spin_secondary_radius, 3.0)
		self._spin_secondary_count = QSpinBox()
		self._spin_secondary_count.setRange(1, 10000)
		self._add_row(form, "secondary_count", "粒子数:", self._spin_secondary_count, 50)
		self._spin_secondary_radial_speed = QDoubleSpinBox()
		self._spin_secondary_radial_speed.setRange(0.1, 50)
		self._add_row(form, "secondary_radial_speed", "径向速度:", self._spin_secondary_radial_speed, 2.0)
		self._spin_secondary_speed = QDoubleSpinBox()
		self._spin_secondary_speed.setRange(0.1, 100)
		self._add_row(form, "secondary_speed", "速度:", self._spin_secondary_speed, 8.0)
		self._spin_secondary_lifetime = QDoubleSpinBox()
		self._spin_secondary_lifetime.setRange(0.1, 60)
		self._add_row(form, "secondary_lifetime", "粒子寿命:", self._spin_secondary_lifetime, 1.5)
		self._spin_secondary_duration = QDoubleSpinBox()
		self._spin_secondary_duration.setRange(0.1, 60)
		self._add_row(form, "secondary_duration", "持续时长:", self._spin_secondary_duration, 1.5)
		self.layout().addWidget(self._group_secondary)

		for w in (
				self._spin_start_x, self._spin_start_y, self._spin_start_z,
				self._spin_mid_x, self._spin_mid_y, self._spin_mid_z,
				self._spin_primary_speed, self._spin_primary_count,
				self._spin_primary_duration, self._spin_primary_lifetime,
				self._spin_primary_track_count, self._spin_primary_spread,
				self._spin_primary_h_angle, self._spin_primary_v_angle,
				self._spin_secondary_radius, self._spin_secondary_count,
				self._spin_secondary_radial_speed, self._spin_secondary_speed,
				self._spin_secondary_lifetime, self._spin_secondary_duration,
		):
			w.valueChanged.connect(self._on_extra_changed)

		self._primary_color_start.color_changed.connect(lambda c: self._on_extra_changed())
		self._primary_color_end.color_changed.connect(lambda c: self._on_extra_changed())
		self._secondary_color_start.color_changed.connect(lambda c: self._on_extra_changed())
		self._secondary_color_end.color_changed.connect(lambda c: self._on_extra_changed())

		self._sub_groups = [
			self._group_start,
			self._group_mid,
			self._group_primary,
			self._primary_color_group,
			self._group_secondary,
			self._secondary_color_group,
		]

	def _load_type_params(self, elem: CompositeElement) -> None:
		self._group_start.show()
		self._group_mid.show()
		self._group_primary.show()
		self._primary_color_group.show()
		self._group_secondary.show()
		self._secondary_color_group.show()

		self._spin_start_x.setValue(elem.se_start_position.x)
		self._spin_start_y.setValue(elem.se_start_position.y)
		self._spin_start_z.setValue(elem.se_start_position.z)

		self._spin_mid_x.setValue(elem.se_mid_position.x)
		self._spin_mid_y.setValue(elem.se_mid_position.y)
		self._spin_mid_z.setValue(elem.se_mid_position.z)

		idx = self._combo_primary_type.findData(elem.se_primary_type)
		if idx >= 0:
			self._combo_primary_type.setCurrentIndex(idx)
		self._primary_color_start.set_color(elem.se_primary_color.start)
		self._primary_color_end.set_color(elem.se_primary_color.end)
		self._spin_primary_speed.setValue(elem.se_primary_speed)
		self._spin_primary_count.setValue(elem.se_primary_count)
		self._spin_primary_duration.setValue(elem.se_primary_duration)
		self._spin_primary_lifetime.setValue(elem.se_primary_lifetime)
		self._spin_primary_track_count.setValue(elem.se_primary_track_count)
		self._spin_primary_spread.setValue(elem.se_primary_spread)
		self._spin_primary_h_angle.setValue(elem.se_primary_h_angle)
		self._spin_primary_v_angle.setValue(elem.se_primary_v_angle)

		idx = self._combo_secondary_type.findData(elem.se_secondary_type)
		if idx >= 0:
			self._combo_secondary_type.setCurrentIndex(idx)
		self._secondary_color_start.set_color(elem.se_secondary_color.start)
		self._secondary_color_end.set_color(elem.se_secondary_color.end)
		self._spin_secondary_radius.setValue(elem.se_secondary_radius)
		self._spin_secondary_count.setValue(elem.se_secondary_count)
		self._spin_secondary_radial_speed.setValue(elem.se_secondary_radial_speed)
		self._spin_secondary_speed.setValue(elem.se_secondary_speed)
		self._spin_secondary_lifetime.setValue(elem.se_secondary_lifetime)
		self._spin_secondary_duration.setValue(elem.se_secondary_duration)

	def _on_extra_changed(self) -> None:
		if self._loading or self._element is None:
			return
		e = self._element

		e.se_start_position.x = self._spin_start_x.value()
		e.se_start_position.y = self._spin_start_y.value()
		e.se_start_position.z = self._spin_start_z.value()

		e.se_mid_position.x = self._spin_mid_x.value()
		e.se_mid_position.y = self._spin_mid_y.value()
		e.se_mid_position.z = self._spin_mid_z.value()

		e.se_primary_type = self._combo_primary_type.currentData()
		e.se_primary_color.start = self._primary_color_start.color
		e.se_primary_color.end = self._primary_color_end.color
		e.se_primary_speed = self._spin_primary_speed.value()
		e.se_primary_count = self._spin_primary_count.value()
		e.se_primary_duration = self._spin_primary_duration.value()
		e.se_primary_lifetime = self._spin_primary_lifetime.value()
		e.se_primary_track_count = self._spin_primary_track_count.value()
		e.se_primary_spread = self._spin_primary_spread.value()
		e.se_primary_h_angle = self._spin_primary_h_angle.value()
		e.se_primary_v_angle = self._spin_primary_v_angle.value()

		e.se_secondary_type = self._combo_secondary_type.currentData()
		e.se_secondary_color.start = self._secondary_color_start.color
		e.se_secondary_color.end = self._secondary_color_end.color
		e.se_secondary_radius = self._spin_secondary_radius.value()
		e.se_secondary_count = self._spin_secondary_count.value()
		e.se_secondary_radial_speed = self._spin_secondary_radial_speed.value()
		e.se_secondary_speed = self._spin_secondary_speed.value()
		e.se_secondary_lifetime = self._spin_secondary_lifetime.value()
		e.se_secondary_duration = self._spin_secondary_duration.value()

		self._emit("extra", None)
