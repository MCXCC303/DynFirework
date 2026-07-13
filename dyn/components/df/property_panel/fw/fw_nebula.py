"""df 星云烟花表单."""
from __future__ import annotations

from PySide6.QtWidgets import QFormLayout, QSpinBox, QDoubleSpinBox, QGroupBox

from dyn.components.df.property_panel.fw.fw_base import FwBase
from dyn.models.df.fireworks import FireworkElement

class NebulaForm(FwBase):
	"""星云烟花参数表单."""

	def _setup_type_sections(self) -> None:
		self._group_params = QGroupBox("星云参数")
		form = QFormLayout(self._group_params)

		self._spin_expansion = QDoubleSpinBox()
		self._spin_expansion.setRange(0.1, 20)
		self._spin_expansion.setSingleStep(0.5)
		self._add_row(form, "expansion_speed", "膨胀速度:", self._spin_expansion, default=2.0)

		self._spin_falloff = QDoubleSpinBox()
		self._spin_falloff.setRange(0.1, 10)
		self._spin_falloff.setSingleStep(0.5)
		self._add_row(form, "density_falloff", "密度衰减:", self._spin_falloff, default=2.0)

		self._spin_count = QSpinBox()
		self._spin_count.setRange(1, 10000)
		self._add_row(form, "particle_count", "粒子数:", self._spin_count, default=100)

		self._spin_expansion.valueChanged.connect(self._on_extra_changed)
		self._spin_falloff.valueChanged.connect(self._on_extra_changed)
		self._spin_count.valueChanged.connect(self._on_extra_changed)

		self.layout().addWidget(self._group_params)
		self._sub_groups = [self._group_params]

	def _load_type_sections(self, elem: FireworkElement) -> None:
		self._group_params.show()
		self._spin_expansion.setValue(elem.expansion_speed)
		self._spin_falloff.setValue(elem.density_falloff)
		self._spin_count.setValue(elem.particle_count)

	def _on_extra_changed(self) -> None:
		if self._loading or self._element is None:
			return
		self._element.expansion_speed = self._spin_expansion.value()
		self._element.density_falloff = self._spin_falloff.value()
		self._element.particle_count = self._spin_count.value()
		self._emit("extra", None)
