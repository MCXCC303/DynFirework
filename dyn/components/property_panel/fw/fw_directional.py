"""定向烟花表单."""
from __future__ import annotations

from PySide6.QtWidgets import (
	QFormLayout, QSpinBox, QDoubleSpinBox, QGroupBox,
)

from dyn.components.property_panel.fw.fw_base import FwBase
from dyn.models.elements import Element, FireworkElement, TrajFireworkElement

class DirectionalForm(FwBase):
	"""定向烟花 speed, spread, track_count."""

	def _setup_type_sections(self) -> None:
		self._group_params = QGroupBox("烟花参数")
		form = QFormLayout(self._group_params)
		self._spin_speed = QDoubleSpinBox()
		self._spin_speed.setRange(0.1, 100)
		self._spin_speed.setValue(10)
		self._add_row(form, "speed", "速度:", self._spin_speed, 10.0)
		self._spin_spread = QDoubleSpinBox()
		self._spin_spread.setRange(1, 180)
		self._spin_spread.setValue(15)
		self._add_row(form, "spread", "扩散角:", self._spin_spread, 15.0)
		self._spin_track_count = QSpinBox()
		self._spin_track_count.setRange(1, 100)
		self._spin_track_count.setValue(1)
		self._add_row(form, "track_count", "轨迹数:", self._spin_track_count, 1)
		self.layout().addWidget(self._group_params)
		self._sub_groups = [self._group_params]

		for w in (self._spin_speed, self._spin_spread, self._spin_track_count):
			w.valueChanged.connect(self._on_extra_changed)

	def _load_type_sections(self, e: Element) -> None:
		self._group_params.show()
		self._spin_speed.setValue(e.speed)
		self._spin_spread.setValue(e.spread_angle)
		self._spin_track_count.setValue(e.track_count)

	def _on_extra_changed(self) -> None:
		if self._loading or self._element is None:
			return
		e = self._element
		if not isinstance(e, (FireworkElement, TrajFireworkElement)):
			return
		e.speed = self._spin_speed.value()
		e.spread_angle = self._spin_spread.value()
		e.track_count = self._spin_track_count.value()
		self._emit("extra", None)
