"""df 集束烟花表单."""
from __future__ import annotations

from PySide6.QtWidgets import QFormLayout, QSpinBox, QDoubleSpinBox, QGroupBox

from dyn.components.df.property_panel.fw.fw_base import FwBase
from dyn.models.df.fireworks import FireworkElement

class ClusteredForm(FwBase):
	"""集束烟花参数表单."""

	def _setup_type_sections(self) -> None:
		self._group_params = QGroupBox("烟花参数")
		form = QFormLayout(self._group_params)

		self._spin_speed = QDoubleSpinBox()
		self._spin_speed.setRange(0.1, 100)
		self._spin_speed.setSingleStep(0.5)
		self._add_row(form, "speed", "速度:", self._spin_speed, default=10.0)

		self._spin_spread = QDoubleSpinBox()
		self._spin_spread.setRange(1, 180)
		self._add_row(form, "spread_angle", "扩散角:", self._spin_spread, default=15.0)

		self._spin_track_count = QSpinBox()
		self._spin_track_count.setRange(1, 100)
		self._add_row(form, "track_count", "轨迹数:", self._spin_track_count, default=5)

		self._spin_speed.valueChanged.connect(self._on_extra_changed)
		self._spin_spread.valueChanged.connect(self._on_extra_changed)
		self._spin_track_count.valueChanged.connect(self._on_extra_changed)
		self._spin_h_angle.valueChanged.connect(self._on_extra_changed)
		self._spin_v_angle.valueChanged.connect(self._on_extra_changed)

		self.layout().addWidget(self._group_params)
		self._sub_groups = [self._group_params]

	def _load_type_sections(self, elem: FireworkElement) -> None:
		self._group_angle.show()
		self._group_params.show()
		self._spin_h_angle.setValue(elem.horizontal_angle)
		self._spin_v_angle.setValue(elem.vertical_angle)
		self._spin_speed.setValue(elem.speed)
		self._spin_spread.setValue(elem.spread_angle)
		self._spin_track_count.setValue(elem.track_count)

	def _on_extra_changed(self) -> None:
		if self._loading or self._element is None:
			return
		self._element.speed = self._spin_speed.value()
		self._element.spread_angle = self._spin_spread.value()
		self._element.track_count = self._spin_track_count.value()
		self._element.horizontal_angle = self._spin_h_angle.value()
		self._element.vertical_angle = self._spin_v_angle.value()
		self._emit("extra", None)
