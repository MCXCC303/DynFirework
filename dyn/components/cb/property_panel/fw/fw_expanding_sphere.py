"""膨胀球烟花表单."""
from __future__ import annotations

from PySide6.QtWidgets import (
	QFormLayout, QSpinBox, QDoubleSpinBox, QGroupBox,
)

from dyn.components.cb.property_panel.fw.fw_base import FwBase
from dyn.models.cb import Element, FireworkElement, TrajFireworkElement

class ExpandingSphereForm(FwBase):
	"""膨胀球烟花 radius, radial_speed, track_count."""

	def _setup_type_sections(self) -> None:
		self._group_params = QGroupBox("烟花参数")
		form = QFormLayout(self._group_params)
		self._spin_radius = QDoubleSpinBox()
		self._spin_radius.setRange(0.1, 100)
		self._spin_radius.setValue(5)
		self._spin_radius.setSingleStep(0.5)
		self._add_row(form, "radius", "半径:", self._spin_radius, 5.0)
		self._spin_radial_speed = QDoubleSpinBox()
		self._spin_radial_speed.setRange(0.1, 50)
		self._spin_radial_speed.setValue(3)
		self._spin_radial_speed.setSingleStep(0.5)
		self._add_row(form, "radial_speed", "径向速度:", self._spin_radial_speed, 3.0)
		self._spin_track_count = QSpinBox()
		self._spin_track_count.setRange(1, 100)
		self._spin_track_count.setValue(1)
		self._add_row(form, "track_count", "轨迹数:", self._spin_track_count, 1)
		self.layout().addWidget(self._group_params)
		self._sub_groups = [self._group_params]

		for w in (self._spin_radius, self._spin_radial_speed, self._spin_track_count):
			w.valueChanged.connect(self._on_extra_changed)

	def _load_type_sections(self, e: Element) -> None:
		self._group_params.show()
		self._spin_radius.setValue(e.radius)
		self._spin_radial_speed.setValue(e.radial_speed)
		self._spin_track_count.setValue(e.track_count)

	def _on_extra_changed(self) -> None:
		if self._loading or self._element is None:
			return
		e = self._element
		if not isinstance(e, (FireworkElement, TrajFireworkElement)):
			return
		e.radius = self._spin_radius.value()
		e.radial_speed = self._spin_radial_speed.value()
		e.track_count = self._spin_track_count.value()
		self._emit("extra", None)
