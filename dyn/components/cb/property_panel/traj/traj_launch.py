"""基础发射轨迹表单."""
from __future__ import annotations

from PySide6.QtWidgets import (
	QFormLayout, QSpinBox, QDoubleSpinBox, QGroupBox,
)

from dyn.components.cb.property_panel.traj.traj_base import TrajBase
from dyn.models.cb import Element, TrajectoryElement

class LaunchForm(TrajBase):
	"""基础发射轨迹 k, m0, rho."""

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
		self._spin_rho = QSpinBox()
		self._spin_rho.setRange(1, 100)
		self._spin_rho.setValue(1)
		self._add_row(form, "rho", "粒子密度 rho:", self._spin_rho, 1)

		self.layout().addWidget(self._group_physics)
		self._sub_groups = [self._group_physics]

		for w in (self._spin_k, self._spin_m0, self._spin_rho):
			w.valueChanged.connect(self._on_extra_changed)

	def _load_type_params(self, e: Element) -> None:
		self._group_physics.show()
		if isinstance(e, TrajectoryElement):
			self._spin_k.setValue(e.k)
			self._spin_m0.setValue(e.m0)
			self._spin_rho.setValue(e.rho)

	def _on_extra_changed(self) -> None:
		if self._loading or self._element is None:
			return
		e = self._element
		if not isinstance(e, TrajectoryElement):
			return
		e.k = self._spin_k.value()
		e.m0 = self._spin_m0.value()
		e.rho = self._spin_rho.value()
		self._emit("extra", None)
