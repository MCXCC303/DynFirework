"""SubPrimaryForm - 一级烟花子表单 6 种烟花类型动态切换."""
from __future__ import annotations

from PySide6.QtWidgets import (
	QFormLayout, QSpinBox, QDoubleSpinBox, QComboBox, QGroupBox,
)

from dyn.models.df.composites import CompositeElement
from dyn.models.df.values import ColorRGB, FireworkType
from ..composite_base import CompositeBase

class SubPrimaryForm(CompositeBase):
	"""一级烟花子表单 类型 QComboBox + 6 套参数组动态切换."""

	def __init__(self, parent=None) -> None:
		super().__init__(parent, has_position=False)

	def _setup_type_params(self) -> None:
		self._group_type_selector = QGroupBox("一级烟花类型")
		form = QFormLayout(self._group_type_selector)
		self._combo_type = QComboBox()
		self._combo_type.addItem("单层", FireworkType.SINGLE_LAYER)
		self._combo_type.addItem("双层", FireworkType.DOUBLE_LAYER)
		self._combo_type.addItem("定向", FireworkType.DIRECTIONAL)
		self._combo_type.addItem("集束", FireworkType.CLUSTERED)
		self._combo_type.addItem("膨胀球", FireworkType.EXPANDING_SPHERE)
		self._combo_type.addItem("星云", FireworkType.NEBULA)
		self._add_row(form, "type", "类型:", self._combo_type, FireworkType.SINGLE_LAYER)
		self._combo_type.currentIndexChanged.connect(self._on_type_changed)
		self.layout().addWidget(self._group_type_selector)

		self._primary_color_group, self._color_start, self._color_end, self._chk_gradient = \
			self._add_color_group("颜色")

		self._setup_single_layer_group()
		self._setup_double_layer_group()
		self._setup_directional_group()
		self._setup_clustered_group()
		self._setup_expanding_sphere_group()
		self._setup_nebula_group()

		for w in (
				self._spin_sl_speed, self._spin_sl_count,
				self._spin_sl_h_angle, self._spin_sl_v_angle,
				self._spin_dl_speed, self._spin_dl_count,
				self._spin_dl_h_angle, self._spin_dl_v_angle,
				self._spin_dir_speed, self._spin_dir_spread,
				self._spin_dir_track_count,
				self._spin_cl_speed, self._spin_cl_spread,
				self._spin_cl_track_count, self._spin_cl_h_angle, self._spin_cl_v_angle,
				self._spin_es_radius, self._spin_es_radial_speed, self._spin_es_count,
				self._spin_neb_count, self._spin_neb_falloff,
		):
			w.valueChanged.connect(self._on_extra_changed)

		self._color_start.color_changed.connect(lambda c: self._on_extra_changed())
		self._color_end.color_changed.connect(lambda c: self._on_extra_changed())
		self._chk_gradient.toggled.connect(self._on_extra_changed)

		self._sub_groups = [
			self._group_type_selector,
			self._primary_color_group,
			self._group_sl,
			self._group_dl,
			self._group_dir,
			self._group_cl,
			self._group_es,
			self._group_neb,
		]

	def _setup_single_layer_group(self) -> None:
		self._group_sl = QGroupBox("单层参数")
		form = QFormLayout(self._group_sl)
		self._spin_sl_speed = QDoubleSpinBox()
		self._spin_sl_speed.setRange(0.1, 100)
		self._add_row(form, "sl_speed", "速度:", self._spin_sl_speed, 10.0)
		self._spin_sl_count = QSpinBox()
		self._spin_sl_count.setRange(1, 10000)
		self._add_row(form, "sl_count", "粒子数:", self._spin_sl_count, 100)
		self._spin_sl_h_angle = QDoubleSpinBox()
		self._spin_sl_h_angle.setRange(1, 360)
		self._add_row(form, "sl_h_angle", "水平角度:", self._spin_sl_h_angle, 30.0)
		self._spin_sl_v_angle = QDoubleSpinBox()
		self._spin_sl_v_angle.setRange(1, 180)
		self._add_row(form, "sl_v_angle", "垂直角度:", self._spin_sl_v_angle, 30.0)
		self.layout().addWidget(self._group_sl)

	def _setup_double_layer_group(self) -> None:
		self._group_dl = QGroupBox("双层参数")
		form = QFormLayout(self._group_dl)
		self._spin_dl_speed = QDoubleSpinBox()
		self._spin_dl_speed.setRange(0.1, 100)
		self._add_row(form, "dl_speed", "速度:", self._spin_dl_speed, 10.0)
		self._spin_dl_count = QSpinBox()
		self._spin_dl_count.setRange(1, 10000)
		self._add_row(form, "dl_count", "粒子数:", self._spin_dl_count, 100)
		self._spin_dl_h_angle = QDoubleSpinBox()
		self._spin_dl_h_angle.setRange(1, 360)
		self._add_row(form, "dl_h_angle", "水平角度:", self._spin_dl_h_angle, 30.0)
		self._spin_dl_v_angle = QDoubleSpinBox()
		self._spin_dl_v_angle.setRange(1, 180)
		self._add_row(form, "dl_v_angle", "垂直角度:", self._spin_dl_v_angle, 30.0)
		self.layout().addWidget(self._group_dl)

	def _setup_directional_group(self) -> None:
		self._group_dir = QGroupBox("定向参数")
		form = QFormLayout(self._group_dir)
		self._spin_dir_speed = QDoubleSpinBox()
		self._spin_dir_speed.setRange(0.1, 100)
		self._add_row(form, "dir_speed", "速度:", self._spin_dir_speed, 10.0)
		self._spin_dir_spread = QDoubleSpinBox()
		self._spin_dir_spread.setRange(1, 180)
		self._add_row(form, "dir_spread", "扩散角:", self._spin_dir_spread, 15.0)
		self._spin_dir_track_count = QSpinBox()
		self._spin_dir_track_count.setRange(1, 100)
		self._add_row(form, "dir_track_count", "轨迹数:", self._spin_dir_track_count, 5)
		self.layout().addWidget(self._group_dir)

	def _setup_clustered_group(self) -> None:
		self._group_cl = QGroupBox("集束参数")
		form = QFormLayout(self._group_cl)
		self._spin_cl_speed = QDoubleSpinBox()
		self._spin_cl_speed.setRange(0.1, 100)
		self._add_row(form, "cl_speed", "速度:", self._spin_cl_speed, 10.0)
		self._spin_cl_spread = QDoubleSpinBox()
		self._spin_cl_spread.setRange(1, 180)
		self._add_row(form, "cl_spread", "扩散角:", self._spin_cl_spread, 15.0)
		self._spin_cl_track_count = QSpinBox()
		self._spin_cl_track_count.setRange(1, 100)
		self._add_row(form, "cl_track_count", "轨迹数:", self._spin_cl_track_count, 5)
		self._spin_cl_h_angle = QDoubleSpinBox()
		self._spin_cl_h_angle.setRange(1, 360)
		self._add_row(form, "cl_h_angle", "水平角度:", self._spin_cl_h_angle, 30.0)
		self._spin_cl_v_angle = QDoubleSpinBox()
		self._spin_cl_v_angle.setRange(1, 180)
		self._add_row(form, "cl_v_angle", "垂直角度:", self._spin_cl_v_angle, 30.0)
		self.layout().addWidget(self._group_cl)

	def _setup_expanding_sphere_group(self) -> None:
		self._group_es = QGroupBox("膨胀球参数")
		form = QFormLayout(self._group_es)
		self._spin_es_radius = QDoubleSpinBox()
		self._spin_es_radius.setRange(0.1, 100)
		self._add_row(form, "es_radius", "半径:", self._spin_es_radius, 3.0)
		self._spin_es_radial_speed = QDoubleSpinBox()
		self._spin_es_radial_speed.setRange(0.1, 50)
		self._add_row(form, "es_radial_speed", "径向速度:", self._spin_es_radial_speed, 2.0)
		self._spin_es_count = QSpinBox()
		self._spin_es_count.setRange(1, 10000)
		self._add_row(form, "es_count", "粒子数:", self._spin_es_count, 100)
		self.layout().addWidget(self._group_es)

	def _setup_nebula_group(self) -> None:
		self._group_neb = QGroupBox("星云参数")
		form = QFormLayout(self._group_neb)
		self._spin_neb_count = QSpinBox()
		self._spin_neb_count.setRange(1, 10000)
		self._add_row(form, "neb_count", "粒子数:", self._spin_neb_count, 100)
		self._spin_neb_falloff = QDoubleSpinBox()
		self._spin_neb_falloff.setRange(0.1, 10)
		self._add_row(form, "neb_falloff", "密度衰减:", self._spin_neb_falloff, 2.0)
		self.layout().addWidget(self._group_neb)

	def _on_type_changed(self) -> None:
		if self._loading:
			return
		self._hide_all()
		self._group_type_selector.show()
		self._primary_color_group.show()
		ft = self._combo_type.currentData()
		self._show_group_for_type(ft)
		if self._element is not None:
			self._element.se_primary_type = ft
			self._emit("extra", None)
		self._update_reset_buttons()

	def _show_group_for_type(self, ft: FireworkType) -> None:
		if ft == FireworkType.SINGLE_LAYER:
			self._group_sl.show()
		elif ft == FireworkType.DOUBLE_LAYER:
			self._group_dl.show()
		elif ft == FireworkType.DIRECTIONAL:
			self._group_dir.show()
		elif ft == FireworkType.CLUSTERED:
			self._group_cl.show()
		elif ft == FireworkType.EXPANDING_SPHERE:
			self._group_es.show()
		elif ft == FireworkType.NEBULA:
			self._group_neb.show()

	def _load_type_params(self, elem: CompositeElement) -> None:
		self._group_type_selector.show()
		self._primary_color_group.show()

		idx = self._combo_type.findData(elem.se_primary_type)
		if idx >= 0:
			self._combo_type.setCurrentIndex(idx)

		c = elem.se_primary_color
		self._color_start.set_color(c.start)
		self._color_end.set_color(c.end)
		self._chk_gradient.setChecked(c.use_gradient)
		self._color_end.setEnabled(c.use_gradient)

		self._spin_sl_speed.setValue(elem.se_primary_speed)
		self._spin_sl_count.setValue(elem.se_primary_count)
		self._spin_sl_h_angle.setValue(elem.se_primary_h_angle)
		self._spin_sl_v_angle.setValue(elem.se_primary_v_angle)

		self._spin_dl_speed.setValue(elem.se_primary_speed)
		self._spin_dl_count.setValue(elem.se_primary_count)
		self._spin_dl_h_angle.setValue(elem.se_primary_h_angle)
		self._spin_dl_v_angle.setValue(elem.se_primary_v_angle)

		self._spin_dir_speed.setValue(elem.se_primary_speed)
		self._spin_dir_spread.setValue(elem.se_primary_spread)
		self._spin_dir_track_count.setValue(elem.se_primary_track_count)

		self._spin_cl_speed.setValue(elem.se_primary_speed)
		self._spin_cl_spread.setValue(elem.se_primary_spread)
		self._spin_cl_track_count.setValue(elem.se_primary_track_count)
		self._spin_cl_h_angle.setValue(elem.se_primary_h_angle)
		self._spin_cl_v_angle.setValue(elem.se_primary_v_angle)

		self._spin_es_radius.setValue(elem.se_primary_radius)
		self._spin_es_radial_speed.setValue(elem.se_primary_radial_speed)
		self._spin_es_count.setValue(elem.se_primary_count)

		self._spin_neb_count.setValue(elem.se_primary_count)
		self._spin_neb_falloff.setValue(elem.se_primary_density_falloff)

		self._show_group_for_type(elem.se_primary_type)

	def _on_extra_changed(self) -> None:
		if self._loading or self._element is None:
			return
		e = self._element

		c = e.se_primary_color
		c.use_gradient = self._chk_gradient.isChecked()
		sc = self._color_start.color
		c.start = ColorRGB(r=sc.r, g=sc.g, b=sc.b)
		ec = self._color_end.color
		c.end = ColorRGB(r=ec.r, g=ec.g, b=ec.b)

		ft = self._combo_type.currentData()
		if ft == FireworkType.SINGLE_LAYER:
			e.se_primary_speed = self._spin_sl_speed.value()
			e.se_primary_count = self._spin_sl_count.value()
			e.se_primary_h_angle = self._spin_sl_h_angle.value()
			e.se_primary_v_angle = self._spin_sl_v_angle.value()
		elif ft == FireworkType.DOUBLE_LAYER:
			e.se_primary_speed = self._spin_dl_speed.value()
			e.se_primary_count = self._spin_dl_count.value()
			e.se_primary_h_angle = self._spin_dl_h_angle.value()
			e.se_primary_v_angle = self._spin_dl_v_angle.value()
		elif ft == FireworkType.DIRECTIONAL:
			e.se_primary_speed = self._spin_dir_speed.value()
			e.se_primary_spread = self._spin_dir_spread.value()
			e.se_primary_track_count = self._spin_dir_track_count.value()
		elif ft == FireworkType.CLUSTERED:
			e.se_primary_speed = self._spin_cl_speed.value()
			e.se_primary_spread = self._spin_cl_spread.value()
			e.se_primary_track_count = self._spin_cl_track_count.value()
			e.se_primary_h_angle = self._spin_cl_h_angle.value()
			e.se_primary_v_angle = self._spin_cl_v_angle.value()
		elif ft == FireworkType.EXPANDING_SPHERE:
			e.se_primary_radius = self._spin_es_radius.value()
			e.se_primary_radial_speed = self._spin_es_radial_speed.value()
			e.se_primary_count = self._spin_es_count.value()
		elif ft == FireworkType.NEBULA:
			e.se_primary_count = self._spin_neb_count.value()
			e.se_primary_density_falloff = self._spin_neb_falloff.value()

		self._emit("extra", None)
