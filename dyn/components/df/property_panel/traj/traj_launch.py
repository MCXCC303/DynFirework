"""df 发射轨迹表单."""
from __future__ import annotations

from PySide6.QtWidgets import QFormLayout, QGroupBox, QDoubleSpinBox, QSpinBox

from dyn.components.df.property_panel.traj.traj_base import TrajBase
from dyn.models.df.trajectories import TrajectoryElement

class LaunchForm(TrajBase):
	"""发射轨迹表单 物理参数 + 粒子参数."""

	def _setup_type_params(self) -> None:
		self._group_physics = QGroupBox("物理参数")
		form_phy = QFormLayout(self._group_physics)
		self._spin_k = QDoubleSpinBox()
		self._spin_k.setRange(0.1, 10)
		self._spin_k.setSingleStep(0.1)
		self._spin_k.setDecimals(1)
		self._add_row(form_phy, "k", "k:", self._spin_k, default=1.2)
		self._spin_m0 = QDoubleSpinBox()
		self._spin_m0.setRange(0.1, 10)
		self._spin_m0.setSingleStep(0.1)
		self._spin_m0.setDecimals(1)
		self._add_row(form_phy, "m0", "m0:", self._spin_m0, default=0.5)
		self._spin_rho = QSpinBox()
		self._spin_rho.setRange(1, 100)
		self._add_row(form_phy, "rho", "rho:", self._spin_rho, default=1)
		self.layout().addWidget(self._group_physics)

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

		for w in (self._spin_k, self._spin_m0, self._spin_rho, self._spin_lifetime, self._spin_particle_count):
			w.valueChanged.connect(self._on_extra_changed)

		self._sub_groups = [self._group_physics, self._group_particle]

	def _load_type_params(self, elem: TrajectoryElement) -> None:
		for grp in self._sub_groups:
			grp.show()
		self._spin_k.setValue(elem.k)
		self._spin_m0.setValue(elem.m0)
		self._spin_rho.setValue(elem.rho)
		self._spin_lifetime.setValue(elem.lifetime)
		self._spin_particle_count.setValue(elem.particle_count)

	def _on_extra_changed(self) -> None:
		if self._loading or self._element is None:
			return
		elem = self._element
		elem.k = self._spin_k.value()
		elem.m0 = self._spin_m0.value()
		elem.rho = self._spin_rho.value()
		elem.lifetime = self._spin_lifetime.value()
		elem.particle_count = self._spin_particle_count.value()
		self._emit("extra", None)
