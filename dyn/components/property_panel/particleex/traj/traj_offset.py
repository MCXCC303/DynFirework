"""随机偏移轨迹表单."""
from __future__ import annotations

from PySide6.QtWidgets import (
	QFormLayout, QSpinBox, QDoubleSpinBox, QGroupBox,
)

from dyn.components.property_panel.particleex.traj.traj_base import TrajBase
from dyn.models.elements import Element, TrajectoryElement

class OffsetForm(TrajBase):
	"""随机偏移轨迹 k, m0, interval_ticks, points_per_tick."""

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

		self.layout().addWidget(self._group_physics)
		self._sub_groups = [self._group_physics]

		for w in (self._spin_k, self._spin_m0, self._spin_interval, self._spin_pts_per_tick):
			w.valueChanged.connect(self._on_extra_changed)

	def _load_type_params(self, e: Element) -> None:
		self._group_physics.show()
		if isinstance(e, TrajectoryElement):
			self._spin_k.setValue(e.k)
			self._spin_m0.setValue(e.m0)
			self._spin_interval.setValue(e.interval_ticks)
			self._spin_pts_per_tick.setValue(e.points_per_tick)

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
		self._emit("extra", None)
