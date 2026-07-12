"""膨胀轨迹（偏移）表单."""
from __future__ import annotations

from PySide6.QtWidgets import (
	QFormLayout, QSpinBox, QDoubleSpinBox, QGroupBox,
)

from dyn.components.cb.property_panel.traj.traj_base import TrajBase
from dyn.models.cb import Element, TrajectoryElement

class ExpandingForm(TrajBase):
	"""膨胀轨迹 k, m0, interval_ticks, points_per_tick, particle_count, range_x/y/z, speed_factor."""

	def _setup_type_params(self) -> None:
		self._group_physics = QGroupBox("轨迹物理参数")
		form = QFormLayout(self._group_physics)

		self._spin_k = QDoubleSpinBox()
		self._spin_k.setRange(0.1, 10.0)
		self._spin_k.setValue(1.2)
		self._spin_k.setSingleStep(0.1)
		self._add_row(form, "k", "阻力系数 k:", self._spin_k, 1.2)
		self._spin_m0 = QDoubleSpinBox()
		self._spin_m0.setRange(0.1, 10.0)
		self._spin_m0.setValue(0.5)
		self._spin_m0.setSingleStep(0.1)
		self._add_row(form, "m0", "质量 m0:", self._spin_m0, 0.5)
		self._spin_interval = QSpinBox()
		self._spin_interval.setRange(1, 100)
		self._spin_interval.setValue(5)
		self._add_row(form, "interval_ticks", "偏移间隔:", self._spin_interval, 5)
		self._spin_pts_per_tick = QSpinBox()
		self._spin_pts_per_tick.setRange(1, 100)
		self._spin_pts_per_tick.setValue(1)
		self._add_row(form, "points_per_tick", "每 tick 点数:", self._spin_pts_per_tick, 1)
		self._spin_particle_count = QSpinBox()
		self._spin_particle_count.setRange(1, 1000)
		self._spin_particle_count.setValue(1)
		self._add_row(form, "particle_count", "粒子数量:", self._spin_particle_count, 1)
		self._spin_range_x = QDoubleSpinBox()
		self._spin_range_x.setRange(0, 100)
		self._spin_range_x.setSingleStep(0.1)
		self._add_row(form, "range_x", "扩散 X:", self._spin_range_x, 0.0)
		self._spin_range_y = QDoubleSpinBox()
		self._spin_range_y.setRange(0, 100)
		self._spin_range_y.setSingleStep(0.1)
		self._add_row(form, "range_y", "扩散 Y:", self._spin_range_y, 0.0)
		self._spin_range_z = QDoubleSpinBox()
		self._spin_range_z.setRange(0, 100)
		self._spin_range_z.setSingleStep(0.1)
		self._add_row(form, "range_z", "扩散 Z:", self._spin_range_z, 0.0)
		self._spin_speed_factor = QDoubleSpinBox()
		self._spin_speed_factor.setRange(0.1, 10.0)
		self._spin_speed_factor.setValue(1.0)
		self._spin_speed_factor.setSingleStep(0.1)
		self._add_row(form, "speed_factor", "速度因子:", self._spin_speed_factor, 1.0)

		self.layout().addWidget(self._group_physics)
		self._sub_groups = [self._group_physics]

		for w in (self._spin_k, self._spin_m0, self._spin_interval, self._spin_pts_per_tick,
		          self._spin_particle_count, self._spin_range_x, self._spin_range_y, self._spin_range_z,
		          self._spin_speed_factor):
			w.valueChanged.connect(self._on_extra_changed)

	def _load_type_params(self, e: Element) -> None:
		self._group_physics.show()
		if isinstance(e, TrajectoryElement):
			self._spin_k.setValue(e.k)
			self._spin_m0.setValue(e.m0)
			self._spin_interval.setValue(e.interval_ticks)
			self._spin_pts_per_tick.setValue(e.points_per_tick)
			self._spin_particle_count.setValue(e.particle_count)
			self._spin_range_x.setValue(e.range_x)
			self._spin_range_y.setValue(e.range_y)
			self._spin_range_z.setValue(e.range_z)
			self._spin_speed_factor.setValue(e.speed_factor)

	def _on_extra_changed(self) -> None:
		if self._loading or self._element is None:
			return
		e = self._element
		if not isinstance(e, TrajectoryElement):
			return
		e.k = self._spin_k.value()
		e.m0 = self._spin_m0.value()
		e.interval_ticks = self._spin_interval.value()
		e.points_per_tick = self._spin_pts_per_tick.value()
		e.particle_count = self._spin_particle_count.value()
		e.range_x = self._spin_range_x.value()
		e.range_y = self._spin_range_y.value()
		e.range_z = self._spin_range_z.value()
		e.speed_factor = self._spin_speed_factor.value()
		self._emit("extra", None)
