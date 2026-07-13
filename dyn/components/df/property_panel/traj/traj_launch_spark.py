"""df 发射火花轨迹表单."""
from __future__ import annotations

from PySide6.QtWidgets import QFormLayout, QVBoxLayout, QGroupBox, QDoubleSpinBox, QSpinBox, QCheckBox

from dyn.components.base.color_picker import ColorPicker
from dyn.components.df.property_panel.traj.traj_base import TrajBase
from dyn.models.df.trajectories import TrajectoryElement

class LaunchSparkForm(TrajBase):
	"""发射火花轨迹表单 物理参数 + 外壳参数."""

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
		self._spin_lifetime = QDoubleSpinBox()
		self._spin_lifetime.setRange(0.1, 60)
		self._spin_lifetime.setSingleStep(0.5)
		self._spin_lifetime.setDecimals(1)
		self._add_row(form_phy, "lifetime", "生命周期:", self._spin_lifetime, default=3.0)
		self._spin_particle_count = QSpinBox()
		self._spin_particle_count.setRange(1, 10000)
		self._add_row(form_phy, "particle_count", "粒子数:", self._spin_particle_count, default=1)
		self.layout().addWidget(self._group_physics)

		self._group_shell = QGroupBox("外壳参数")
		shell_layout = QVBoxLayout(self._group_shell)
		self._chk_add_shell = QCheckBox("添加外壳")
		self._chk_add_shell.toggled.connect(self._on_shell_toggled)
		shell_layout.addWidget(self._chk_add_shell)
		self._color_shell = ColorPicker("颜色:")
		self._color_shell.setEnabled(False)
		shell_layout.addWidget(self._color_shell)
		self._spin_shell_size = QDoubleSpinBox()
		self._spin_shell_size.setRange(0.1, 20)
		self._spin_shell_size.setSingleStep(0.5)
		self._spin_shell_size.setDecimals(1)
		self._spin_shell_size.setEnabled(False)
		shell_form = QFormLayout()
		self._add_row(shell_form, "shell_size", "外壳大小:", self._spin_shell_size, default=1.0)
		shell_layout.addLayout(shell_form)
		self.layout().addWidget(self._group_shell)

		for w in (self._spin_k, self._spin_m0, self._spin_lifetime, self._spin_particle_count, self._spin_shell_size):
			w.valueChanged.connect(self._on_extra_changed)
		self._color_shell.color_changed.connect(self._on_extra_changed)

		self._sub_groups = [self._group_physics, self._group_shell]

	def _load_type_params(self, elem: TrajectoryElement) -> None:
		self._group_color.hide()
		for grp in self._sub_groups:
			grp.show()
		self._spin_k.setValue(elem.k)
		self._spin_m0.setValue(elem.m0)
		self._spin_lifetime.setValue(elem.lifetime)
		self._spin_particle_count.setValue(elem.particle_count)
		self._chk_add_shell.setChecked(elem.add_shell)
		self._color_shell.set_color(elem.shell_color)
		self._color_shell.setEnabled(elem.add_shell)
		self._spin_shell_size.setValue(elem.shell_size)
		self._spin_shell_size.setEnabled(elem.add_shell)

	def _on_shell_toggled(self, checked: bool) -> None:
		self._color_shell.setEnabled(checked)
		self._spin_shell_size.setEnabled(checked)
		self._on_extra_changed()

	def _on_extra_changed(self) -> None:
		if self._loading or self._element is None:
			return
		elem = self._element
		elem.k = self._spin_k.value()
		elem.m0 = self._spin_m0.value()
		elem.lifetime = self._spin_lifetime.value()
		elem.particle_count = self._spin_particle_count.value()
		elem.add_shell = self._chk_add_shell.isChecked()
		elem.shell_color = self._color_shell.color
		elem.shell_size = self._spin_shell_size.value()
		self._emit("extra", None)
