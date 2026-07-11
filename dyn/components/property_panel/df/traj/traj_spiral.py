"""df 螺旋轨迹表单."""
from __future__ import annotations

from PySide6.QtWidgets import QFormLayout, QVBoxLayout, QGroupBox, QDoubleSpinBox, QSpinBox, QCheckBox

from dyn.components.property_panel.color_picker import ColorPicker
from dyn.components.property_panel.df.traj.traj_base import TrajBase
from dyn.models.df.trajectories import TrajectoryElement

class SpiralForm(TrajBase):
	"""螺旋轨迹表单 螺旋参数 + 粒子参数 + 外壳参数."""

	def _setup_type_params(self) -> None:
		self._group_spiral = QGroupBox("螺旋参数")
		form_spiral = QFormLayout(self._group_spiral)
		self._spin_spiral_radius = QDoubleSpinBox()
		self._spin_spiral_radius.setRange(0.1, 50)
		self._spin_spiral_radius.setSingleStep(0.5)
		self._spin_spiral_radius.setDecimals(1)
		self._add_row(form_spiral, "spiral_radius", "螺旋半径:", self._spin_spiral_radius, default=2.0)
		self._spin_spiral_speed = QDoubleSpinBox()
		self._spin_spiral_speed.setRange(0.1, 20)
		self._spin_spiral_speed.setSingleStep(0.5)
		self._spin_spiral_speed.setDecimals(1)
		self._add_row(form_spiral, "spiral_speed", "螺旋速度:", self._spin_spiral_speed, default=3.0)
		self._spin_shrink_exponent = QDoubleSpinBox()
		self._spin_shrink_exponent.setRange(0.1, 10)
		self._spin_shrink_exponent.setSingleStep(0.1)
		self._spin_shrink_exponent.setDecimals(1)
		self._add_row(form_spiral, "shrink_exponent", "收缩指数:", self._spin_shrink_exponent, default=1.0)
		self.layout().addWidget(self._group_spiral)

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

		self._group_shell = QGroupBox("外壳参数")
		shell_layout = QVBoxLayout(self._group_shell)
		self._chk_add_shell = QCheckBox("添加外壳")
		self._chk_add_shell.toggled.connect(self._on_shell_toggled)
		shell_layout.addWidget(self._chk_add_shell)
		self._color_shell = ColorPicker("颜色:")
		self._color_shell.hide()
		shell_layout.addWidget(self._color_shell)
		self._spin_shell_size = QDoubleSpinBox()
		self._spin_shell_size.setRange(0.1, 20)
		self._spin_shell_size.setSingleStep(0.5)
		self._spin_shell_size.setDecimals(1)
		self._spin_shell_size.hide()
		shell_layout.addWidget(self._spin_shell_size)
		self.layout().addWidget(self._group_shell)

		for w in (self._spin_spiral_radius,
		          self._spin_spiral_speed,
		          self._spin_shrink_exponent,
		          self._spin_lifetime,
		          self._spin_particle_count,
		          self._spin_shell_size):
			w.valueChanged.connect(self._on_extra_changed)
		self._color_shell.color_changed.connect(self._on_extra_changed)

		self._sub_groups = [self._group_spiral, self._group_particle, self._group_shell]

	def _load_type_params(self, elem: TrajectoryElement) -> None:
		for grp in self._sub_groups:
			grp.show()
		self._spin_spiral_radius.setValue(elem.spiral_radius)
		self._spin_spiral_speed.setValue(elem.spiral_speed)
		self._spin_shrink_exponent.setValue(elem.shrink_exponent)
		self._spin_lifetime.setValue(elem.lifetime)
		self._spin_particle_count.setValue(elem.particle_count)
		self._chk_add_shell.setChecked(elem.add_shell)
		self._color_shell.set_color(elem.shell_color)
		self._color_shell.setVisible(elem.add_shell)
		self._spin_shell_size.setValue(elem.shell_size)
		self._spin_shell_size.setVisible(elem.add_shell)

	def _on_shell_toggled(self, checked: bool) -> None:
		self._color_shell.setVisible(checked)
		self._spin_shell_size.setVisible(checked)
		self._on_extra_changed()

	def _on_extra_changed(self) -> None:
		if self._loading or self._element is None:
			return
		elem = self._element
		elem.spiral_radius = self._spin_spiral_radius.value()
		elem.spiral_speed = self._spin_spiral_speed.value()
		elem.shrink_exponent = self._spin_shrink_exponent.value()
		elem.lifetime = self._spin_lifetime.value()
		elem.particle_count = self._spin_particle_count.value()
		elem.add_shell = self._chk_add_shell.isChecked()
		elem.shell_color = self._color_shell.color
		elem.shell_size = self._spin_shell_size.value()
		self._emit("extra", None)
