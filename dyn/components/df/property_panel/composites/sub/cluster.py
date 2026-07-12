"""SubClusterForm - 集束烟花子表单 固定 clustered 类型."""
from __future__ import annotations

from PySide6.QtWidgets import (
	QFormLayout, QSpinBox, QDoubleSpinBox, QGroupBox,
)

from dyn.models.df.composites import CompositeElement
from dyn.models.df.values import ColorRGB
from ..composite_base import CompositeBase

class SubClusterForm(CompositeBase):
	"""集束烟花子表单 无类型选择器 固定显示 clustered 参数."""

	def __init__(self, parent=None) -> None:
		super().__init__(parent, has_position=False)

	def _setup_type_params(self) -> None:
		self._group_params = QGroupBox("集束烟花参数")
		form = QFormLayout(self._group_params)

		self._spin_speed = QDoubleSpinBox()
		self._spin_speed.setRange(0.1, 100)
		self._add_row(form, "speed", "速度:", self._spin_speed, 10.0)
		self._spin_dir_count = QSpinBox()
		self._spin_dir_count.setRange(1, 100)
		self._add_row(form, "dir_count", "方向数:", self._spin_dir_count, 12)
		self._spin_track_count = QSpinBox()
		self._spin_track_count.setRange(1, 100)
		self._add_row(form, "track_count", "轨迹数:", self._spin_track_count, 5)
		self._spin_spread = QDoubleSpinBox()
		self._spin_spread.setRange(1, 180)
		self._add_row(form, "spread", "扩散角:", self._spin_spread, 15.0)
		self.layout().addWidget(self._group_params)

		self._cluster_color_group, self._color_start, self._color_end, self._chk_gradient = \
			self._add_color_group("颜色")

		for w in (
				self._spin_speed, self._spin_dir_count,
				self._spin_track_count, self._spin_spread,
		):
			w.valueChanged.connect(self._on_extra_changed)

		self._color_start.color_changed.connect(lambda c: self._on_extra_changed())
		self._color_end.color_changed.connect(lambda c: self._on_extra_changed())
		self._chk_gradient.toggled.connect(self._on_extra_changed)

		self._sub_groups = [
			self._group_params,
			self._cluster_color_group,
		]

	def _load_type_params(self, elem: CompositeElement) -> None:
		self._group_params.show()
		self._cluster_color_group.show()

		self._spin_speed.setValue(elem.ce_cluster_speed)
		self._spin_dir_count.setValue(elem.ce_dir_count)
		self._spin_track_count.setValue(elem.ce_track_count)
		self._spin_spread.setValue(elem.ce_spread)

		c = elem.ce_cluster_color
		self._color_start.set_color(c.start)
		self._color_end.set_color(c.end)
		self._chk_gradient.setChecked(c.use_gradient)
		self._color_end.setEnabled(c.use_gradient)

	def _on_extra_changed(self) -> None:
		if self._loading or self._element is None:
			return
		e = self._element

		c = e.ce_cluster_color
		c.use_gradient = self._chk_gradient.isChecked()
		sc = self._color_start.color
		c.start = ColorRGB(r=sc.r, g=sc.g, b=sc.b)
		ec = self._color_end.color
		c.end = ColorRGB(r=ec.r, g=ec.g, b=ec.b)

		e.ce_cluster_speed = self._spin_speed.value()
		e.ce_dir_count = self._spin_dir_count.value()
		e.ce_track_count = self._spin_track_count.value()
		e.ce_spread = self._spin_spread.value()

		self._emit("extra", None)
