"""df 扩散轨迹表单."""
from __future__ import annotations

from PySide6.QtWidgets import QFormLayout, QGroupBox, QDoubleSpinBox, QSpinBox

from dyn.components.df.property_panel.traj.traj_base import TrajBase
from dyn.models.df.trajectories import TrajectoryElement

class ExpandingForm(TrajBase):
	"""扩散轨迹表单 扩散参数 + 粒子参数."""

	def _setup_type_params(self) -> None:
		self._group_range = QGroupBox("扩散参数")
		form_range = QFormLayout(self._group_range)
		self._spin_range_x = QDoubleSpinBox()
		self._spin_range_x.setRange(0, 100)
		self._spin_range_x.setSingleStep(0.5)
		self._spin_range_x.setDecimals(1)
		self._add_row(form_range, "range_x", "X 范围:", self._spin_range_x, default=0.0)
		self._spin_range_y = QDoubleSpinBox()
		self._spin_range_y.setRange(0, 100)
		self._spin_range_y.setSingleStep(0.5)
		self._spin_range_y.setDecimals(1)
		self._add_row(form_range, "range_y", "Y 范围:", self._spin_range_y, default=0.0)
		self._spin_range_z = QDoubleSpinBox()
		self._spin_range_z.setRange(0, 100)
		self._spin_range_z.setSingleStep(0.5)
		self._spin_range_z.setDecimals(1)
		self._add_row(form_range, "range_z", "Z 范围:", self._spin_range_z, default=0.0)
		self._spin_speed_factor = QDoubleSpinBox()
		self._spin_speed_factor.setRange(0.1, 20)
		self._spin_speed_factor.setSingleStep(0.5)
		self._spin_speed_factor.setDecimals(1)
		self._add_row(form_range, "speed_factor", "速度因子:", self._spin_speed_factor, default=1.0)
		self.layout().addWidget(self._group_range)

		self._group_particle = QGroupBox("粒子参数")
		form_part = QFormLayout(self._group_particle)
		self._spin_lifetime = QDoubleSpinBox()
		self._spin_lifetime.setRange(0.1, 60)
		self._spin_lifetime.setSingleStep(0.5)
		self._spin_lifetime.setDecimals(1)
		self._add_row(form_part, "lifetime", "生命周期:", self._spin_lifetime, default=3.0)
		self._spin_particle_count = QSpinBox()
		self._spin_particle_count.setRange(1, 10000)
		self._add_row(form_part, "particle_count", "粒子数:", self._spin_particle_count, default=1)
		self.layout().addWidget(self._group_particle)

		for w in (self._spin_range_x,
		          self._spin_range_y,
		          self._spin_range_z,
		          self._spin_speed_factor,
		          self._spin_lifetime,
		          self._spin_particle_count):
			w.valueChanged.connect(self._on_extra_changed)

		self._sub_groups = [self._group_range, self._group_particle]

	def _load_type_params(self, elem: TrajectoryElement) -> None:
		for grp in self._sub_groups:
			grp.show()
		self._spin_range_x.setValue(elem.range_x)
		self._spin_range_y.setValue(elem.range_y)
		self._spin_range_z.setValue(elem.range_z)
		self._spin_speed_factor.setValue(elem.speed_factor)
		self._spin_lifetime.setValue(elem.lifetime)
		self._spin_particle_count.setValue(elem.particle_count)

	def _on_extra_changed(self) -> None:
		if self._loading or self._element is None:
			return
		elem = self._element
		elem.range_x = self._spin_range_x.value()
		elem.range_y = self._spin_range_y.value()
		elem.range_z = self._spin_range_z.value()
		elem.speed_factor = self._spin_speed_factor.value()
		elem.lifetime = self._spin_lifetime.value()
		elem.particle_count = self._spin_particle_count.value()
		self._emit("extra", None)
