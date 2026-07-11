"""单层烟花表单."""
from __future__ import annotations

from PySide6.QtWidgets import (
	QFormLayout, QDoubleSpinBox, QGroupBox,
)

from dyn.components.property_panel.particleex.fw.fw_base import FwBase
from dyn.models.elements import Element, FireworkElement, TrajFireworkElement

class SingleLayerForm(FwBase):
	"""单层烟花 speed, horizontal_angle, vertical_angle."""

	def _setup_type_sections(self) -> None:
		self._group_angle.show()

		self._group_params = QGroupBox("烟花参数")
		form = QFormLayout(self._group_params)
		self._spin_speed = QDoubleSpinBox()
		self._spin_speed.setRange(0.1, 100)
		self._spin_speed.setValue(10)
		self._add_row(form, "speed", "速度:", self._spin_speed, 10.0)
		self.layout().addWidget(self._group_params)
		self._sub_groups = [self._group_params]

		self._spin_speed.valueChanged.connect(self._on_extra_changed)

	def _load_type_sections(self, e: Element) -> None:
		self._group_angle.show()
		self._group_params.show()
		self._spin_h_angle.setValue(e.horizontal_angle)
		self._spin_v_angle.setValue(e.vertical_angle)
		self._spin_speed.setValue(e.speed)

	def _on_extra_changed(self) -> None:
		if self._loading or self._element is None:
			return
		e = self._element
		if not isinstance(e, (FireworkElement, TrajFireworkElement)):
			return
		e.speed = self._spin_speed.value()
		e.horizontal_angle = self._spin_h_angle.value()
		e.vertical_angle = self._spin_v_angle.value()
		self._emit("extra", None)
