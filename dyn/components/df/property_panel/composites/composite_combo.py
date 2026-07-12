"""组合 EC 表单 集束 + 膨胀同步烟花."""
from __future__ import annotations

from PySide6.QtWidgets import (
	QFormLayout, QSpinBox, QDoubleSpinBox, QCheckBox, QGroupBox, QPushButton, )

from dyn.components.df.property_panel.composites.composite_base import CompositeBase
from dyn.models.df.composites import CompositeElement
from dyn.models.df.values import ColorRGB

class ComboECForm(CompositeBase):
	"""组合 EC 中心位置 + 集束部分 + 膨胀部分 + 时间."""

	def _setup_type_params(self) -> None:
		self._group_ce_pos = QGroupBox("中心位置")
		form = QFormLayout(self._group_ce_pos)
		self._spin_ce_x = QDoubleSpinBox()
		self._spin_ce_x.setRange(-100000, 100000)
		self._spin_ce_x.setDecimals(2)
		self._add_row(form, "ce_x", "X:", self._spin_ce_x)
		self._spin_ce_y = QDoubleSpinBox()
		self._spin_ce_y.setRange(-64, 320)
		self._spin_ce_y.setDecimals(2)
		self._add_row(form, "ce_y", "Y:", self._spin_ce_y)
		self._spin_ce_z = QDoubleSpinBox()
		self._spin_ce_z.setRange(-100000, 100000)
		self._spin_ce_z.setDecimals(2)
		self._add_row(form, "ce_z", "Z:", self._spin_ce_z)
		btn_ce = QPushButton("在地图上选择...")
		btn_ce.clicked.connect(lambda: self.position_select_requested.emit("ce_pos"))
		form.addRow("", btn_ce)
		self.layout().addWidget(self._group_ce_pos)

		self._group_cluster = QGroupBox("集束部分")
		form = QFormLayout(self._group_cluster)
		self._cluster_color_group, self._cluster_color_start, self._cluster_color_end, self._chk_cluster_grad = self._add_color_group("颜色")
		self._spin_cluster_speed = QDoubleSpinBox()
		self._spin_cluster_speed.setRange(0.1, 100)
		self._add_row(form, "cluster_speed", "速度:", self._spin_cluster_speed, 10.0)
		self._spin_dir_count = QSpinBox()
		self._spin_dir_count.setRange(1, 100)
		self._add_row(form, "dir_count", "方向数:", self._spin_dir_count, 12)
		self._spin_track_count = QSpinBox()
		self._spin_track_count.setRange(1, 100)
		self._add_row(form, "track_count", "轨迹数:", self._spin_track_count, 5)
		self._spin_spread = QDoubleSpinBox()
		self._spin_spread.setRange(1, 180)
		self._add_row(form, "spread", "扩散角:", self._spin_spread, 15.0)
		self.layout().addWidget(self._group_cluster)

		self._group_sphere = QGroupBox("膨胀部分")
		form = QFormLayout(self._group_sphere)
		self._sphere_color_group, self._sphere_color_start, self._sphere_color_end, self._chk_sphere_grad = self._add_color_group("颜色")
		self._spin_sphere_count = QSpinBox()
		self._spin_sphere_count.setRange(1, 10000)
		self._add_row(form, "sphere_count", "粒子数:", self._spin_sphere_count, 100)
		self._chk_flicker = QCheckBox("启用闪烁")
		form.addRow("", self._chk_flicker)
		self.layout().addWidget(self._group_sphere)

		self._group_time = QGroupBox("时间")
		form = QFormLayout(self._group_time)
		self._spin_duration = QDoubleSpinBox()
		self._spin_duration.setRange(0.1, 60)
		self._add_row(form, "duration", "持续时长:", self._spin_duration, 2.0)
		self._spin_lifetime = QDoubleSpinBox()
		self._spin_lifetime.setRange(0.1, 60)
		self._add_row(form, "lifetime", "粒子寿命:", self._spin_lifetime, 2.0)
		self.layout().addWidget(self._group_time)

		for w in (
				self._spin_ce_x, self._spin_ce_y, self._spin_ce_z,
				self._spin_cluster_speed, self._spin_dir_count,
				self._spin_track_count, self._spin_spread,
				self._spin_sphere_count, self._spin_duration, self._spin_lifetime,
		):
			w.valueChanged.connect(self._on_extra_changed)

		self._chk_flicker.toggled.connect(self._on_extra_changed)

		self._cluster_color_start.color_changed.connect(lambda c: self._on_extra_changed())
		self._cluster_color_end.color_changed.connect(lambda c: self._on_extra_changed())
		self._sphere_color_start.color_changed.connect(lambda c: self._on_extra_changed())
		self._sphere_color_end.color_changed.connect(lambda c: self._on_extra_changed())
		self._chk_cluster_grad.toggled.connect(self._on_extra_changed)
		self._chk_sphere_grad.toggled.connect(self._on_extra_changed)

		self._sub_groups = [
			self._group_ce_pos,
			self._group_cluster,
			self._cluster_color_group,
			self._group_sphere,
			self._sphere_color_group,
			self._group_time,
		]

	def _load_type_params(self, elem: CompositeElement) -> None:
		self._group_ce_pos.show()
		self._group_cluster.show()
		self._cluster_color_group.show()
		self._group_sphere.show()
		self._sphere_color_group.show()
		self._group_time.show()

		self._spin_ce_x.setValue(elem.ce_position.x)
		self._spin_ce_y.setValue(elem.ce_position.y)
		self._spin_ce_z.setValue(elem.ce_position.z)

		self._cluster_color_start.set_color(elem.ce_cluster_color.start)
		self._cluster_color_end.set_color(elem.ce_cluster_color.end)
		self._spin_cluster_speed.setValue(elem.ce_cluster_speed)
		self._spin_dir_count.setValue(elem.ce_dir_count)
		self._spin_track_count.setValue(elem.ce_track_count)
		self._spin_spread.setValue(elem.ce_spread)

		self._sphere_color_start.set_color(elem.ce_sphere_color.start)
		self._sphere_color_end.set_color(elem.ce_sphere_color.end)
		self._chk_cluster_grad.setChecked(elem.ce_cluster_color.use_gradient)
		self._cluster_color_end.setEnabled(elem.ce_cluster_color.use_gradient)
		self._chk_sphere_grad.setChecked(elem.ce_sphere_color.use_gradient)
		self._sphere_color_end.setEnabled(elem.ce_sphere_color.use_gradient)
		self._spin_sphere_count.setValue(elem.ce_sphere_count)
		self._chk_flicker.setChecked(elem.ce_flicker)

		self._spin_duration.setValue(elem.ce_duration)
		self._spin_lifetime.setValue(elem.ce_lifetime)

	def _on_extra_changed(self) -> None:
		if self._loading or self._element is None:
			return
		e = self._element

		e.ce_cluster_color.use_gradient = self._chk_cluster_grad.isChecked()
		e.ce_sphere_color.use_gradient = self._chk_sphere_grad.isChecked()
		e.ce_position.x = self._spin_ce_x.value()
		e.ce_position.y = self._spin_ce_y.value()
		e.ce_position.z = self._spin_ce_z.value()

		cc = self._cluster_color_start.color
		e.ce_cluster_color.start = ColorRGB(r=cc.r, g=cc.g, b=cc.b)
		cc = self._cluster_color_end.color
		e.ce_cluster_color.end = ColorRGB(r=cc.r, g=cc.g, b=cc.b)
		e.ce_cluster_speed = self._spin_cluster_speed.value()
		e.ce_dir_count = self._spin_dir_count.value()
		e.ce_track_count = self._spin_track_count.value()
		e.ce_spread = self._spin_spread.value()

		sc = self._sphere_color_start.color
		e.ce_sphere_color.start = ColorRGB(r=sc.r, g=sc.g, b=sc.b)
		sc = self._sphere_color_end.color
		e.ce_sphere_color.end = ColorRGB(r=sc.r, g=sc.g, b=sc.b)
		e.ce_sphere_count = self._spin_sphere_count.value()
		e.ce_flicker = self._chk_flicker.isChecked()

		e.ce_duration = self._spin_duration.value()
		e.ce_lifetime = self._spin_lifetime.value()

		self._emit("extra", None)
