"""基础参数面板   根据元素类型动态显示/隐藏参数."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
	QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
	QLabel, QLineEdit, QSpinBox, QDoubleSpinBox,
	QCheckBox, QComboBox, QPushButton,
	QGroupBox, QScrollArea, QColorDialog, QDial,
)

from dyn.logging_config import get_logger
from dyn.models.elements import (
	Element,
	TrajectoryElement,
	FireworkElement,
	TrajFireworkElement,
	ColorRGB,
	Position,
)
from dyn.service.element_controller import ElementController

log = get_logger(__name__)

class ColorPicker(QWidget):
	"""颜色选择组件."""
	color_changed = Signal(ColorRGB)

	def __init__(self, label: str = "", parent: QWidget | None = None) -> None:
		super().__init__(parent)
		self._color = ColorRGB()
		self._setup_ui(label)

	def _setup_ui(self, label: str) -> None:
		layout = QHBoxLayout(self)
		layout.setContentsMargins(0, 0, 0, 0)
		layout.setSpacing(4)
		if label:
			lbl = QLabel(label);
			lbl.setFixedWidth(40);
			layout.addWidget(lbl)
		self._btn = QPushButton();
		self._btn.setFixedSize(52, 28)
		self._btn.setToolTip("点击选择颜色")
		self._btn.clicked.connect(self._on_pick_color)
		layout.addWidget(self._btn)
		for ch in ("R", "G", "B"):
			lbl = QLabel(ch);
			lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter);
			lbl.setFixedWidth(14)
			layout.addWidget(lbl)
			spin = QSpinBox();
			spin.setRange(0, 255);
			spin.setFixedWidth(48)
			layout.addWidget(spin)
			if ch == "R":
				self._spin_r = spin
			elif ch == "G":
				self._spin_g = spin
			else:
				self._spin_b = spin
		self._spin_r.valueChanged.connect(self._on_spin_changed)
		self._spin_g.valueChanged.connect(self._on_spin_changed)
		self._spin_b.valueChanged.connect(self._on_spin_changed)
		self._update_button()

	def _on_pick_color(self) -> None:
		init = QColor(self._color.r, self._color.g, self._color.b)
		qcolor = QColorDialog.getColor(init, self, "选择颜色")
		if qcolor.isValid():
			self._color = ColorRGB(r=qcolor.red(), g=qcolor.green(), b=qcolor.blue())
			self._spin_r.setValue(qcolor.red())
			self._spin_g.setValue(qcolor.green())
			self._spin_b.setValue(qcolor.blue())

	def _on_spin_changed(self) -> None:
		self._color = ColorRGB(r=self._spin_r.value(), g=self._spin_g.value(), b=self._spin_b.value())
		self._update_button()
		self.color_changed.emit(self._color)

	def _update_button(self) -> None:
		c = self._color
		self._btn.setStyleSheet(f"QPushButton {{ background-color: rgb({c.r},{c.g},{c.b}); border: 1px solid #888; border-radius: 3px; }}")

	def set_color(self, color: ColorRGB) -> None:
		self._color = color
		self._spin_r.setValue(color.r);
		self._spin_g.setValue(color.g);
		self._spin_b.setValue(color.b)
		self._update_button()

	@property
	def color(self) -> ColorRGB:
		return self._color

class PropertyPanel(QScrollArea):
	"""动态参数面板."""

	property_changed = Signal(str, str, object, object)  # id, key, new_value, old_value
	position_select_requested = Signal(str)
	element_name_changed = Signal(str, str)

	_TRAJ_TYPE_LABELS = {
		"launch": "基础发射轨迹",
		"spark": "火花轨迹",
		"offset": "随机偏移轨迹",
		"thick": "粗轨迹（偏移）",
		"expanding": "膨胀轨迹（偏移）"}
	_FW_TYPE_LABELS = {
		"single_layer": "单层烟花",
		"double_layer": "双层烟花",
		"directional": "定向烟花",
		"clustered": "集束烟花",
		"expanding_sphere": "膨胀球烟花"}

	# 每种轨迹类型需要的额外参数
	_TRAJ_EXTRA_PARAMS = {
		"launch": ["rho"],
		"spark": ["particle_count"],
		"offset": ["interval_ticks", "points_per_tick"],
		"thick": ["interval_ticks", "points_per_tick", "particle_count", "range_x", "range_y", "range_z"],
		"expanding": ["interval_ticks", "points_per_tick", "particle_count", "range_x", "range_y", "range_z", "speed_factor"],
	}
	# 每种烟花类型需要的参数
	_FW_PARAMS = {
		"single_layer": {"speed", "horizontal_angle", "vertical_angle"},
		"double_layer": {"inner_speed", "outer_speed", "horizontal_angle", "vertical_angle"},
		"directional": {"speed", "spread_angle", "track_count"},
		"clustered": {"speed", "spread_angle", "track_count", "horizontal_angle", "vertical_angle"},
		"expanding_sphere": {"radius", "radial_speed", "track_count"},
	}
	# 哪些烟花类型有内/外层颜色
	_FW_COLOR_LAYERS = {
		"single_layer": ["inner"],
		"double_layer": ["inner", "outer"],
		"directional": ["inner"],
		"clustered": ["inner"],
		"expanding_sphere": ["inner"],
	}

	def __init__(self, controller: ElementController, parent: QWidget | None = None) -> None:
		super().__init__(parent)
		self._controller = controller
		self._current_element: Element | None = None
		self._loading: bool = False

		self.setWidgetResizable(True)
		self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

		container = QWidget()
		self.setWidget(container)
		self._layout = QVBoxLayout(container)
		self._layout.setContentsMargins(8, 8, 8, 8)
		self._layout.setSpacing(8)

		self._setup_common_section()
		self._setup_position_section()
		self._setup_traj_color_section()
		self._setup_traj_extra_section()
		self._setup_fw_color_inner()
		self._setup_fw_color_outer()
		self._setup_fw_angle_section()
		self._setup_fw_extra_section()
		self._layout.addStretch()

		self._hide_all()
		self.setEnabled(False)

	#  控件存储：{param_name: (label_widget, input_widget, reset_btn, default_val)}
	_w: dict[str, tuple[QWidget, QWidget, QPushButton | None, object]] = {}
	_DEFAULTS: dict[str, object] = {}

	def _add_row(self, form: QFormLayout, key: str, label: str, widget: QWidget, default: object = None) -> None:
		lbl = QLabel(label)
		row = QHBoxLayout()
		row.setContentsMargins(0, 0, 0, 0);
		row.setSpacing(2)
		row.addWidget(widget)
		btn = None
		if default is not None:
			self._DEFAULTS[key] = default
			btn = QPushButton("↺")
			btn.setFixedSize(20, 20)
			btn.setToolTip("重置为默认值")
			btn.clicked.connect(lambda checked, k=key, d=default, w=widget: self._reset_value(k, d, w))
			btn.hide()
			row.addWidget(btn)
			# 数值变更时自动更新按钮可见性
			if isinstance(widget, QSpinBox):
				widget.valueChanged.connect(lambda v: self._update_reset_buttons())
			elif isinstance(widget, QDoubleSpinBox):
				widget.valueChanged.connect(lambda v: self._update_reset_buttons())
		form.addRow(lbl, row)
		self._w[key] = (lbl, widget, btn, default)

	def _reset_value(self, key: str, default: object, widget: QWidget) -> None:
		if isinstance(widget, (QSpinBox, QDoubleSpinBox)):
			widget.setValue(default)
		elif isinstance(widget, QComboBox):
			idx = widget.findData(default)
			if idx >= 0: widget.setCurrentIndex(idx)

	def _update_reset_buttons(self) -> None:
		for key, (lbl, widget, btn, default) in self._w.items():
			if btn is None or default is None:
				continue
			if isinstance(widget, QSpinBox):
				show = widget.value() != int(default)
			elif isinstance(widget, QDoubleSpinBox):
				show = abs(widget.value() - float(default)) > 0.001
			elif isinstance(widget, QComboBox):
				data = widget.currentData()
				show = data != default
			else:
				continue
			btn.setVisible(show)

	#  基本信息

	def _setup_common_section(self) -> None:
		grp = QGroupBox("基本信息")
		form = QFormLayout(grp)
		self._edit_name = QLineEdit();
		self._edit_name.setPlaceholderText("元素名称")
		self._edit_name.textChanged.connect(lambda t: self._emit_change("name", t))
		self._add_row(form, "name", "名称:", self._edit_name)

		self._spin_start_tick = QSpinBox();
		self._spin_start_tick.setRange(0, 100000)
		self._spin_start_tick.valueChanged.connect(lambda v: self._emit_change("start_tick", v))
		self._add_row(form, "start_tick", "起始 Tick:", self._spin_start_tick)

		self._spin_duration = QSpinBox();
		self._spin_duration.setRange(1, 10000)
		self._spin_duration.valueChanged.connect(lambda v: self._emit_change("duration_ticks", v))
		self._add_row(form, "duration_ticks", "时长:", self._spin_duration)

		self._chk_enabled = QCheckBox("启用");
		self._chk_enabled.setChecked(True)
		self._chk_enabled.toggled.connect(lambda v: self._emit_change("enabled", v))
		form.addRow("", self._chk_enabled)

		self._group_common = grp;
		self._layout.addWidget(grp)

	#  位置 (轨迹始末 + 烟花中心)

	def _setup_position_section(self) -> None:
		self._group_pos = QGroupBox("位置")
		form = QFormLayout(self._group_pos)
		self._spin_pos_x = QDoubleSpinBox();
		self._spin_pos_x.setRange(-100000, 100000);
		self._spin_pos_x.setDecimals(2)
		self._add_row(form, "pos_x", "X:", self._spin_pos_x)
		self._spin_pos_y = QDoubleSpinBox();
		self._spin_pos_y.setRange(-64, 320);
		self._spin_pos_y.setDecimals(2)
		self._add_row(form, "pos_y", "Y:", self._spin_pos_y)
		self._spin_pos_z = QDoubleSpinBox();
		self._spin_pos_z.setRange(-100000, 100000);
		self._spin_pos_z.setDecimals(2)
		self._add_row(form, "pos_z", "Z:", self._spin_pos_z)
		# 位置坐标变更 -> 自动同步元素
		self._spin_pos_x.valueChanged.connect(lambda: self._on_pos_xy_changed())
		self._spin_pos_y.valueChanged.connect(lambda: self._on_pos_xy_changed())
		self._spin_pos_z.valueChanged.connect(lambda: self._on_pos_xy_changed())
		self._btn_pos_select = QPushButton("在地图上选择...")
		self._btn_pos_select.clicked.connect(lambda: self.position_select_requested.emit("firework"))
		form.addRow("", self._btn_pos_select)
		self._layout.addWidget(self._group_pos)

		# 轨迹结束位置（仅轨迹使用）
		self._group_endpos = QGroupBox("结束位置")
		end_form = QFormLayout(self._group_endpos)
		self._spin_end_x = QDoubleSpinBox();
		self._spin_end_x.setRange(-100000, 100000);
		self._spin_end_x.setDecimals(2)
		self._add_row(end_form, "end_x", "X:", self._spin_end_x)
		self._spin_end_y = QDoubleSpinBox();
		self._spin_end_y.setRange(-64, 320);
		self._spin_end_y.setDecimals(2)
		self._add_row(end_form, "end_y", "Y:", self._spin_end_y)
		self._spin_end_z = QDoubleSpinBox();
		self._spin_end_z.setRange(-100000, 100000);
		self._spin_end_z.setDecimals(2)
		self._add_row(end_form, "end_z", "Z:", self._spin_end_z)
		self._spin_end_x.valueChanged.connect(lambda: self._on_end_pos_changed())
		self._spin_end_y.valueChanged.connect(lambda: self._on_end_pos_changed())
		self._spin_end_z.valueChanged.connect(lambda: self._on_end_pos_changed())
		self._btn_end_select = QPushButton("在地图上选择...")
		self._btn_end_select.clicked.connect(lambda: self.position_select_requested.emit("end"))
		end_form.addRow("", self._btn_end_select)
		self._layout.addWidget(self._group_endpos)

	def _on_pos_xy_changed(self) -> None:
		if self._loading: return
		e = self._current_element
		if isinstance(e, TrajFireworkElement):
			e.start_position = Position(x=self._spin_pos_x.value(), y=self._spin_pos_y.value(), z=self._spin_pos_z.value())
		elif hasattr(e, "traj_color"):
			e.start_position = Position(x=self._spin_pos_x.value(), y=self._spin_pos_y.value(), z=self._spin_pos_z.value())
		elif hasattr(e, "fw_type"):
			e.position = Position(x=self._spin_pos_x.value(), y=self._spin_pos_y.value(), z=self._spin_pos_z.value())
		self._emit_change("position", None)

	def _on_end_pos_changed(self) -> None:
		if self._loading: return
		e = self._current_element
		if isinstance(e, TrajFireworkElement):
			e.mid_position = Position(x=self._spin_end_x.value(), y=self._spin_end_y.value(), z=self._spin_end_z.value())
			self._emit_change("end_position", None)
		elif hasattr(e, "traj_color"):
			e.end_position = Position(x=self._spin_end_x.value(), y=self._spin_end_y.value(), z=self._spin_end_z.value())
			self._emit_change("end_position", None)

	#  轨迹颜色

	def _setup_traj_color_section(self) -> None:
		self._group_traj_color = QGroupBox("轨迹颜色")
		layout = QVBoxLayout(self._group_traj_color)

		# 轨迹类型选择
		self._combo_traj_type = QComboBox()
		for k, v in self._TRAJ_TYPE_LABELS.items():
			self._combo_traj_type.addItem(v, k)
		self._combo_traj_type.currentIndexChanged.connect(self._on_traj_type_changed)
		layout.addWidget(QLabel("轨迹类型:"))
		layout.addWidget(self._combo_traj_type)

		self._chk_traj_gradient = QCheckBox("使用渐变")
		self._chk_traj_gradient.toggled.connect(lambda v: self._emit_change("traj_gradient", v))
		layout.addWidget(self._chk_traj_gradient)
		self._color_traj_start = ColorPicker("开始:");
		layout.addWidget(self._color_traj_start)
		self._color_traj_end = ColorPicker("结束:");
		layout.addWidget(self._color_traj_end)
		self._color_traj_start.color_changed.connect(lambda c: self._emit_change("traj_color_start", c))
		self._color_traj_end.color_changed.connect(lambda c: self._emit_change("traj_color_end", c))
		self._layout.addWidget(self._group_traj_color)

	def _on_traj_type_changed(self, idx: int) -> None:
		if not self._loading and isinstance(self._current_element, (TrajectoryElement, TrajFireworkElement)):
			new_type = self._combo_traj_type.itemData(idx)
			log.debug(f"轨迹类型变更: {new_type}, element={self._current_element.name}")
			new_type = self._combo_traj_type.itemData(idx)
			self._current_element.traj_type = new_type
			self._hide_traj_extras()
			extras = self._TRAJ_EXTRA_PARAMS.get(new_type, [])
			for k in extras:
				if k in self._w:
					self._w[k][0].show();
					self._w[k][1].show()
			for k in ("k", "m0"):
				if k in self._w:
					self._w[k][0].show();
					self._w[k][1].show()
			self._emit_change("traj_type", new_type)

	#  轨迹额外参数

	def _setup_traj_extra_section(self) -> None:
		self._group_traj_extra = QGroupBox("轨迹物理参数")
		form = QFormLayout(self._group_traj_extra)

		self._spin_k = QDoubleSpinBox();
		self._spin_k.setRange(0.1, 10.0);
		self._spin_k.setValue(1.2);
		self._spin_k.setSingleStep(0.1)
		self._add_row(form, "k", "阻力系数 k:", self._spin_k, 1.2)
		self._spin_m0 = QDoubleSpinBox();
		self._spin_m0.setRange(0.1, 10.0);
		self._spin_m0.setValue(0.5);
		self._spin_m0.setSingleStep(0.1)
		self._add_row(form, "m0", "质量 m0:", self._spin_m0, 0.5)

		self._spin_rho = QSpinBox();
		self._spin_rho.setRange(1, 100);
		self._spin_rho.setValue(1)
		self._add_row(form, "rho", "粒子密度 rho:", self._spin_rho, 1)
		self._spin_particle_count = QSpinBox();
		self._spin_particle_count.setRange(1, 1000);
		self._spin_particle_count.setValue(1)
		self._add_row(form, "particle_count", "粒子数量:", self._spin_particle_count, 1)
		self._spin_interval = QSpinBox();
		self._spin_interval.setRange(1, 100);
		self._spin_interval.setValue(5)
		self._add_row(form, "interval_ticks", "偏移间隔:", self._spin_interval, 5)
		self._spin_pts_per_tick = QSpinBox();
		self._spin_pts_per_tick.setRange(1, 100);
		self._spin_pts_per_tick.setValue(1)
		self._add_row(form, "points_per_tick", "每 tick 点数:", self._spin_pts_per_tick, 1)
		self._spin_range_x = QDoubleSpinBox();
		self._spin_range_x.setRange(0, 100);
		self._spin_range_x.setSingleStep(0.1)
		self._add_row(form, "range_x", "扩散 X:", self._spin_range_x, 0.0)
		self._spin_range_y = QDoubleSpinBox();
		self._spin_range_y.setRange(0, 100);
		self._spin_range_y.setSingleStep(0.1)
		self._add_row(form, "range_y", "扩散 Y:", self._spin_range_y, 0.0)
		self._spin_range_z = QDoubleSpinBox();
		self._spin_range_z.setRange(0, 100);
		self._spin_range_z.setSingleStep(0.1)
		self._add_row(form, "range_z", "扩散 Z:", self._spin_range_z, 0.0)
		self._spin_speed_factor = QDoubleSpinBox();
		self._spin_speed_factor.setRange(0.1, 10.0);
		self._spin_speed_factor.setValue(1.0);
		self._spin_speed_factor.setSingleStep(0.1)
		self._add_row(form, "speed_factor", "速度因子:", self._spin_speed_factor, 1.0)

		self._layout.addWidget(self._group_traj_extra)
		for w in (self._spin_k, self._spin_m0, self._spin_rho, self._spin_particle_count,
		          self._spin_interval, self._spin_pts_per_tick, self._spin_range_x,
		          self._spin_range_y, self._spin_range_z, self._spin_speed_factor):
			w.valueChanged.connect(self._on_traj_extra_changed)

	#  烟花内层颜色

	def _setup_fw_color_inner(self) -> None:
		self._group_fw_inner = QGroupBox("烟花颜色")
		layout = QVBoxLayout(self._group_fw_inner)

		self._combo_fw_type = QComboBox()
		for k, v in self._FW_TYPE_LABELS.items():
			self._combo_fw_type.addItem(v, k)
		self._combo_fw_type.currentIndexChanged.connect(self._on_fw_type_changed)
		layout.addWidget(QLabel("烟花类型:"))
		layout.addWidget(self._combo_fw_type)

		self._chk_inner_gradient = QCheckBox("使用渐变");
		layout.addWidget(self._chk_inner_gradient)
		self._chk_inner_gradient.toggled.connect(lambda v: self._emit_change("inner_gradient", v))
		self._color_inner_start = ColorPicker("开始:");
		layout.addWidget(self._color_inner_start)
		self._color_inner_end = ColorPicker("结束:");
		layout.addWidget(self._color_inner_end)
		self._color_inner_start.color_changed.connect(lambda c: self._emit_change("inner_color_start", c))
		self._color_inner_end.color_changed.connect(lambda c: self._emit_change("inner_color_end", c))
		self._layout.addWidget(self._group_fw_inner)

	def _on_fw_type_changed(self, idx: int) -> None:
		if not self._loading and isinstance(self._current_element, (FireworkElement, TrajFireworkElement)):
			new_type = self._combo_fw_type.itemData(idx)
			log.debug(f"烟花类型变更: {new_type}, element={self._current_element.name}")
			self._current_element.fw_type = new_type
			# 更新颜色层显示
			layers = self._FW_COLOR_LAYERS.get(new_type, ["inner"])
			self._group_fw_outer.setVisible("outer" in layers)
			# 更新参数显示
			self._hide_fw_extras()
			params = self._FW_PARAMS.get(new_type, set())
			for k in params:
				if k in self._w:
					self._w[k][0].show();
					self._w[k][1].show()
			self._group_fw_angle.setVisible("horizontal_angle" in params or "vertical_angle" in params)
			self._emit_change("fw_type", new_type)

	#  烟花外层颜色

	def _setup_fw_color_outer(self) -> None:
		self._group_fw_outer = QGroupBox("外层颜色")
		layout = QVBoxLayout(self._group_fw_outer)
		self._chk_outer_gradient = QCheckBox("使用渐变");
		layout.addWidget(self._chk_outer_gradient)
		self._chk_outer_gradient.toggled.connect(lambda v: self._emit_change("outer_gradient", v))
		self._color_outer_start = ColorPicker("开始:");
		layout.addWidget(self._color_outer_start)
		self._color_outer_end = ColorPicker("结束:");
		layout.addWidget(self._color_outer_end)
		self._color_outer_start.color_changed.connect(lambda c: self._emit_change("outer_color_start", c))
		self._color_outer_end.color_changed.connect(lambda c: self._emit_change("outer_color_end", c))
		self._layout.addWidget(self._group_fw_outer)

	#  角度 (Dial + SpinBox)

	def _setup_fw_angle_section(self) -> None:
		self._group_fw_angle = QGroupBox("爆炸角度")
		layout = QVBoxLayout(self._group_fw_angle)
		layout.setAlignment(Qt.AlignCenter)

		row = QHBoxLayout()
		row.setAlignment(Qt.AlignCenter)
		row.addStretch()

		# 水平角度组
		h_grp = QVBoxLayout()
		h_grp.setAlignment(Qt.AlignCenter)
		self._dial_h = QDial();
		self._dial_h.setRange(1, 360);
		self._dial_h.setValue(30);
		self._dial_h.setNotchesVisible(True);
		self._dial_h.setFixedSize(80, 80)
		h_grp.addWidget(self._dial_h, alignment=Qt.AlignCenter)
		h_lbl = QLabel("水平角度");
		h_lbl.setAlignment(Qt.AlignCenter)
		h_grp.addWidget(h_lbl)
		self._spin_h_angle = QDoubleSpinBox();
		self._spin_h_angle.setRange(1, 360);
		self._spin_h_angle.setValue(30);
		self._spin_h_angle.setFixedWidth(80)
		self._dial_h.valueChanged.connect(lambda v: self._spin_h_angle.setValue(v))
		self._spin_h_angle.valueChanged.connect(lambda v: self._dial_h.setValue(int(v)))
		h_grp.addWidget(self._spin_h_angle, alignment=Qt.AlignCenter)
		row.addLayout(h_grp)

		row.addSpacing(30)

		# 垂直角度组
		v_grp = QVBoxLayout()
		v_grp.setAlignment(Qt.AlignCenter)
		self._dial_v = QDial();
		self._dial_v.setRange(1, 180);
		self._dial_v.setValue(30);
		self._dial_v.setNotchesVisible(True);
		self._dial_v.setFixedSize(80, 80)
		v_grp.addWidget(self._dial_v, alignment=Qt.AlignCenter)
		v_lbl = QLabel("垂直角度");
		v_lbl.setAlignment(Qt.AlignCenter)
		v_grp.addWidget(v_lbl)
		self._spin_v_angle = QDoubleSpinBox();
		self._spin_v_angle.setRange(1, 180);
		self._spin_v_angle.setValue(30);
		self._spin_v_angle.setFixedWidth(80)
		self._dial_v.valueChanged.connect(lambda v: self._spin_v_angle.setValue(v))
		self._spin_v_angle.valueChanged.connect(lambda v: self._dial_v.setValue(int(v)))
		v_grp.addWidget(self._spin_v_angle, alignment=Qt.AlignCenter)
		row.addLayout(v_grp)

		row.addStretch()
		layout.addLayout(row)
		self._layout.addWidget(self._group_fw_angle)

	#  烟花额外参数

	def _setup_fw_extra_section(self) -> None:
		self._group_fw_extra = QGroupBox("烟花参数")
		form = QFormLayout(self._group_fw_extra)

		self._spin_speed = QDoubleSpinBox();
		self._spin_speed.setRange(0.1, 100);
		self._spin_speed.setValue(10)
		self._add_row(form, "speed", "速度:", self._spin_speed, 10.0)
		self._spin_inner_speed = QDoubleSpinBox();
		self._spin_inner_speed.setRange(0.1, 100);
		self._spin_inner_speed.setValue(8)
		self._add_row(form, "inner_speed", "内层速度:", self._spin_inner_speed, 8.0)
		self._spin_outer_speed = QDoubleSpinBox();
		self._spin_outer_speed.setRange(0.1, 100);
		self._spin_outer_speed.setValue(10)
		self._add_row(form, "outer_speed", "外层速度:", self._spin_outer_speed, 10.0)
		self._spin_spread = QDoubleSpinBox();
		self._spin_spread.setRange(1, 180);
		self._spin_spread.setValue(15)
		self._add_row(form, "spread", "扩散角:", self._spin_spread, 15.0)
		self._spin_track_count = QSpinBox();
		self._spin_track_count.setRange(1, 100);
		self._spin_track_count.setValue(1)
		self._add_row(form, "track_count", "轨迹数:", self._spin_track_count, 1)
		self._spin_radius = QDoubleSpinBox();
		self._spin_radius.setRange(0.1, 100);
		self._spin_radius.setValue(5);
		self._spin_radius.setSingleStep(0.5)
		self._add_row(form, "radius", "半径:", self._spin_radius, 5.0)
		self._spin_radial_speed = QDoubleSpinBox();
		self._spin_radial_speed.setRange(0.1, 50);
		self._spin_radial_speed.setValue(3);
		self._spin_radial_speed.setSingleStep(0.5)
		self._add_row(form, "radial_speed", "径向速度:", self._spin_radial_speed, 3.0)

		self._layout.addWidget(self._group_fw_extra)
		for w in (self._spin_speed, self._spin_inner_speed, self._spin_outer_speed,
		          self._spin_spread, self._spin_track_count, self._spin_radius, self._spin_radial_speed):
			w.valueChanged.connect(self._on_fw_extra_changed)

	#  类型选择 (动态创建，在 traj/fw section 显示)

	def _setup_type_selector(self) -> None:
		"""在加载时动态添加到 group 上方."""
		pass  # 类型选择器在 _load_* 中通过 setVisible 控制

	# 显示/隐藏

	def _show_w(self, key: str) -> None:
		if key in self._w:
			self._w[key][0].show();
			self._w[key][1].show()
			if self._w[key][2]: self._w[key][2].show()

	def _hide_w(self, key: str) -> None:
		if key in self._w:
			self._w[key][0].hide();
			self._w[key][1].hide()
			if self._w[key][2]: self._w[key][2].hide()

	def _hide_all(self) -> None:
		for grp in [self._group_common, self._group_pos, self._group_endpos,
		            self._group_traj_color, self._group_traj_extra,
		            self._group_fw_inner, self._group_fw_outer,
		            self._group_fw_angle, self._group_fw_extra]:
			grp.hide()

	def _show_traj_extras_by_type(self, traj_type: str) -> None:
		"""根据轨迹类型显示对应参数."""
		self._hide_traj_extras()
		extras = self._TRAJ_EXTRA_PARAMS.get(traj_type, [])
		for k in extras:
			if k in self._w: self._show_w(k)
		for k in ("k", "m0"):
			if k in self._w: self._show_w(k)

	def _show_fw_extras_by_type(self, fw_type: str) -> None:
		"""根据烟花类型显示对应参数."""
		self._hide_fw_extras()
		params = self._FW_PARAMS.get(fw_type, set())
		for k in params:
			if k in self._w: self._show_w(k)

	def _hide_traj_extras(self) -> None:
		for k in ("rho", "particle_count", "interval_ticks", "points_per_tick",
		          "range_x", "range_y", "range_z", "speed_factor"):
			if k in self._w: self._hide_w(k)

	def _hide_fw_extras(self) -> None:
		for k in ("speed", "inner_speed", "outer_speed", "spread", "track_count",
		          "radius", "radial_speed"):
			if k in self._w:
				self._w[k][0].hide();
				self._w[k][1].hide()

	# 加载元素

	def load_element(self, elem: Element | None, part: str = "") -> None:
		if self._loading:
			return
		self._loading = True
		try:
			self._do_load_element(elem, part)
		finally:
			self._loading = False

	def _do_load_element(self, elem: Element | None, part: str = "") -> None:
		self._current_element = elem
		if elem is None:
			self._hide_all()
			self.setEnabled(False)
			return
		self.setEnabled(True)
		self._block_all(True)

		# 公共
		self._edit_name.setText(elem.name)
		self._spin_start_tick.setValue(elem.start_tick)
		if isinstance(elem, TrajFireworkElement):
			self._spin_duration.setValue(elem.traj_duration_ticks + elem.fw_duration_ticks)
			self._spin_duration.setReadOnly(True)
		else:
			self._spin_duration.setValue(elem.duration_ticks)
			self._spin_duration.setReadOnly(False)
		self._chk_enabled.setChecked(elem.enabled)
		self._group_common.show()

		is_tf = hasattr(elem, 'traj_type') and hasattr(elem, 'fw_type')
		if is_tf:
			if part == "traj":
				self._load_tf_traj_only(elem)
			elif part == "fw":
				self._load_tf_fw_only(elem)
			else:
				self._load_tf_full(elem)
		elif isinstance(elem, TrajectoryElement):
			self._load_trajectory(elem)
		elif isinstance(elem, FireworkElement):
			self._load_firework(elem)

		self._block_all(False)
		self._update_reset_buttons()

	def _load_tf_full(self, e) -> None:
		"""轨迹烟花完整参数."""
		self._hide_all()
		self._spin_pos_x.setReadOnly(False);
		self._spin_pos_y.setReadOnly(False);
		self._spin_pos_z.setReadOnly(False)
		self._spin_end_x.setReadOnly(False);
		self._spin_end_y.setReadOnly(False);
		self._spin_end_z.setReadOnly(False)
		self._btn_pos_select.show()
		self._group_common.show()
		self._group_pos.show();
		self._group_pos.setTitle("起始位置")
		self._group_endpos.show();
		self._group_endpos.setTitle("结束位置")
		self._group_traj_color.show();
		self._group_traj_extra.show()
		self._group_fw_inner.show();
		self._group_fw_outer.show()
		self._group_fw_angle.show();
		self._group_fw_extra.show()
		# 填值
		self._spin_pos_x.setValue(e.start_position.x);
		self._spin_pos_y.setValue(e.start_position.y);
		self._spin_pos_z.setValue(e.start_position.z)
		self._spin_end_x.setValue(e.mid_position.x);
		self._spin_end_y.setValue(e.mid_position.y);
		self._spin_end_z.setValue(e.mid_position.z)
		idx = self._combo_traj_type.findData(e.traj_type)
		if idx >= 0: self._combo_traj_type.setCurrentIndex(idx)
		self._chk_traj_gradient.setChecked(e.traj_color.use_gradient)
		self._color_traj_end.setEnabled(e.traj_color.use_gradient)
		self._color_traj_start.set_color(e.traj_color.start);
		self._color_traj_end.set_color(e.traj_color.end)
		self._spin_k.setValue(e.k);
		self._spin_m0.setValue(e.m0);
		self._spin_rho.setValue(e.rho)
		idx2 = self._combo_fw_type.findData(e.fw_type)
		if idx2 >= 0: self._combo_fw_type.setCurrentIndex(idx2)
		self._chk_inner_gradient.setChecked(e.inner_color.use_gradient)
		self._color_inner_end.setEnabled(e.inner_color.use_gradient)
		self._color_inner_start.set_color(e.inner_color.start);
		self._color_inner_end.set_color(e.inner_color.end)
		self._chk_outer_gradient.setChecked(e.outer_color.use_gradient)
		self._color_outer_end.setEnabled(e.outer_color.use_gradient)
		self._color_outer_start.set_color(e.outer_color.start);
		self._color_outer_end.set_color(e.outer_color.end)
		self._spin_h_angle.setValue(e.horizontal_angle);
		self._spin_v_angle.setValue(e.vertical_angle)
		self._spin_speed.setValue(e.speed);
		self._spin_inner_speed.setValue(e.inner_speed);
		self._spin_outer_speed.setValue(e.outer_speed)
		self._spin_spread.setValue(e.spread_angle);
		self._spin_track_count.setValue(e.track_count)
		self._show_traj_extras_by_type(e.traj_type)
		self._show_fw_extras_by_type(e.fw_type)
		layers = self._FW_COLOR_LAYERS.get(e.fw_type, ["inner"])
		self._group_fw_outer.setVisible("outer" in layers)
		params = self._FW_PARAMS.get(e.fw_type, set())
		self._group_fw_angle.setVisible("horizontal_angle" in params or "vertical_angle" in params)

	def _load_tf_traj_only(self, e) -> None:
		"""仅轨迹部分."""
		self._hide_all()
		self._spin_pos_x.setReadOnly(False);
		self._spin_pos_y.setReadOnly(False);
		self._spin_pos_z.setReadOnly(False)
		self._spin_end_x.setReadOnly(False);
		self._spin_end_y.setReadOnly(False);
		self._spin_end_z.setReadOnly(False)
		self._btn_pos_select.show()
		self._group_common.show()
		self._group_pos.show();
		self._group_pos.setTitle("起始位置")
		self._group_endpos.show();
		self._group_endpos.setTitle("结束位置")
		self._group_traj_color.show();
		self._group_traj_extra.show()
		self._spin_pos_x.setValue(e.start_position.x);
		self._spin_pos_y.setValue(e.start_position.y);
		self._spin_pos_z.setValue(e.start_position.z)
		self._spin_end_x.setValue(e.mid_position.x);
		self._spin_end_y.setValue(e.mid_position.y);
		self._spin_end_z.setValue(e.mid_position.z)
		idx = self._combo_traj_type.findData(e.traj_type)
		if idx >= 0: self._combo_traj_type.setCurrentIndex(idx)
		self._chk_traj_gradient.setChecked(e.traj_color.use_gradient)
		self._color_traj_end.setEnabled(e.traj_color.use_gradient)
		self._color_traj_start.set_color(e.traj_color.start);
		self._color_traj_end.set_color(e.traj_color.end)
		self._spin_k.setValue(e.k);
		self._spin_m0.setValue(e.m0);
		self._spin_rho.setValue(e.rho)
		self._spin_duration.setValue(e.traj_duration_ticks)
		self._show_traj_extras_by_type(e.traj_type)

	def _load_tf_fw_only(self, e) -> None:
		"""仅烟花部分   位置只读."""
		self._hide_all()
		self._group_common.show()
		self._group_pos.show();
		self._group_pos.setTitle("爆炸中心（由轨迹终点决定）")
		self._group_fw_inner.show();
		self._group_fw_outer.show()
		self._group_fw_angle.show();
		self._group_fw_extra.show()
		self._spin_pos_x.setValue(e.mid_position.x if e.mid_position else 0);
		self._spin_pos_y.setValue(e.mid_position.y if e.mid_position else 0);
		self._spin_pos_z.setValue(e.mid_position.z if e.mid_position else 0)
		self._spin_pos_x.setReadOnly(True);
		self._spin_pos_y.setReadOnly(True);
		self._spin_pos_z.setReadOnly(True)
		self._btn_pos_select.hide()
		self._spin_duration.setValue(e.fw_duration_ticks)
		self._show_fw_extras_by_type(e.fw_type)
		layers = self._FW_COLOR_LAYERS.get(e.fw_type, ["inner"])
		self._group_fw_outer.setVisible("outer" in layers)
		self._group_fw_angle.setVisible("horizontal_angle" in self._FW_PARAMS.get(e.fw_type, set()))
		idx = self._combo_fw_type.findData(e.fw_type)
		if idx >= 0: self._combo_fw_type.setCurrentIndex(idx)
		self._chk_inner_gradient.setChecked(e.inner_color.use_gradient)
		self._color_inner_end.setEnabled(e.inner_color.use_gradient)
		self._color_inner_start.set_color(e.inner_color.start);
		self._color_inner_end.set_color(e.inner_color.end)
		self._chk_outer_gradient.setChecked(e.outer_color.use_gradient)
		self._color_outer_end.setEnabled(e.outer_color.use_gradient)
		self._color_outer_start.set_color(e.outer_color.start);
		self._color_outer_end.set_color(e.outer_color.end)
		self._spin_h_angle.setValue(e.horizontal_angle);
		self._spin_v_angle.setValue(e.vertical_angle)
		self._spin_speed.setValue(e.speed);
		self._spin_inner_speed.setValue(e.inner_speed);
		self._spin_outer_speed.setValue(e.outer_speed)
		self._spin_spread.setValue(e.spread_angle);
		self._spin_track_count.setValue(e.track_count)
		self._spin_duration.setValue(e.fw_duration_ticks)

	def _load_trajectory(self, e: TrajectoryElement) -> None:
		self._hide_all()
		self._spin_pos_x.setReadOnly(False);
		self._spin_pos_y.setReadOnly(False);
		self._spin_pos_z.setReadOnly(False)
		self._spin_end_x.setReadOnly(False);
		self._spin_end_y.setReadOnly(False);
		self._spin_end_z.setReadOnly(False)
		self._btn_pos_select.show()
		self._group_common.show()
		self._group_pos.show()  # 起始位置
		self._group_pos.setTitle("起始位置")
		self._group_endpos.show()
		self._group_traj_color.show()

		self._spin_pos_x.setValue(e.start_position.x);
		self._spin_pos_y.setValue(e.start_position.y);
		self._spin_pos_z.setValue(e.start_position.z)
		self._spin_end_x.setValue(e.end_position.x);
		self._spin_end_y.setValue(e.end_position.y);
		self._spin_end_z.setValue(e.end_position.z)
		idx = self._combo_traj_type.findData(e.traj_type)
		if idx >= 0: self._combo_traj_type.setCurrentIndex(idx)
		self._chk_traj_gradient.setChecked(e.traj_color.use_gradient)
		self._color_traj_end.setEnabled(e.traj_color.use_gradient)
		self._color_traj_start.set_color(e.traj_color.start)
		self._color_traj_end.set_color(e.traj_color.end)
		self._spin_k.setValue(e.k);
		self._spin_m0.setValue(e.m0)
		self._spin_rho.setValue(e.rho);
		self._spin_particle_count.setValue(e.particle_count)
		self._spin_interval.setValue(e.interval_ticks);
		self._spin_pts_per_tick.setValue(e.points_per_tick)
		self._spin_range_x.setValue(e.range_x);
		self._spin_range_y.setValue(e.range_y);
		self._spin_range_z.setValue(e.range_z)
		self._spin_speed_factor.setValue(e.speed_factor)

		# 根据类型显示/隐藏参数
		self._group_traj_extra.show()
		self._hide_traj_extras()
		extras = self._TRAJ_EXTRA_PARAMS.get(e.traj_type, [])
		for k in extras:
			if k in self._w:
				self._w[k][0].show();
				self._w[k][1].show()
		# k, m0 始终可见
		for k in ("k", "m0"):
			if k in self._w:
				self._w[k][0].show();
				self._w[k][1].show()

	def _load_firework(self, e: FireworkElement) -> None:
		self._hide_all()
		self._spin_pos_x.setReadOnly(False);
		self._spin_pos_y.setReadOnly(False);
		self._spin_pos_z.setReadOnly(False)
		self._btn_pos_select.show()
		self._group_common.show()
		self._group_pos.show()
		self._group_pos.setTitle("爆炸中心")
		self._group_fw_extra.show()

		self._spin_pos_x.setValue(e.position.x);
		self._spin_pos_y.setValue(e.position.y);
		self._spin_pos_z.setValue(e.position.z)

		idx = self._combo_fw_type.findData(e.fw_type)
		if idx >= 0: self._combo_fw_type.setCurrentIndex(idx)

		layers = self._FW_COLOR_LAYERS.get(e.fw_type, ["inner"])
		if "inner" in layers:
			self._group_fw_inner.show()
			self._chk_inner_gradient.setChecked(e.inner_color.use_gradient)
			self._color_inner_start.set_color(e.inner_color.start)
			self._color_inner_end.set_color(e.inner_color.end)
		if "outer" in layers:
			self._group_fw_outer.show()
			self._chk_outer_gradient.setChecked(e.outer_color.use_gradient)
			self._color_outer_start.set_color(e.outer_color.start)
			self._color_outer_end.set_color(e.outer_color.end)

		params = self._FW_PARAMS.get(e.fw_type, set())
		if "horizontal_angle" in params or "vertical_angle" in params:
			self._group_fw_angle.show()
			self._spin_h_angle.setValue(e.horizontal_angle)
			self._spin_v_angle.setValue(e.vertical_angle)

		self._spin_speed.setValue(e.speed);
		self._spin_inner_speed.setValue(e.inner_speed)
		self._spin_outer_speed.setValue(e.outer_speed);
		self._spin_spread.setValue(e.spread_angle)
		self._spin_track_count.setValue(e.track_count)
		self._spin_radius.setValue(e.radius);
		self._spin_radial_speed.setValue(e.radial_speed)

		# 动态显示
		self._hide_fw_extras()
		for k in params:
			if k in self._w:
				self._w[k][0].show();
				self._w[k][1].show()

	# 信号

	def _emit_change(self, key: str, value: Any) -> None:
		if not self._current_element or self._loading:
			return
		e = self._current_element
		# 捕获旧值（必须在修改前读取）
		old_value = getattr(e, key, None)
		# 立即更新元素属性
		if key in ("name", "start_tick", "duration_ticks"):
			setattr(e, key, value)
		elif key == "enabled":
			e.enabled = value
		elif key == "traj_gradient" and hasattr(e, 'traj_color'):
			e.traj_color.use_gradient = value
			self._color_traj_end.setEnabled(value)
		elif key == "inner_gradient" and hasattr(e, 'inner_color'):
			e.inner_color.use_gradient = value
			self._color_inner_end.setEnabled(value)
		elif key == "outer_gradient" and hasattr(e, 'outer_color'):
			e.outer_color.use_gradient = value
			self._color_outer_end.setEnabled(value)
		elif key == "traj_color_start" and hasattr(e, "traj_color"):
			old_value = e.traj_color.start
			e.traj_color.start = value
		elif key == "traj_color_end" and hasattr(e, "traj_color"):
			old_value = e.traj_color.end
			e.traj_color.end = value
		elif key == "inner_color_start" and hasattr(e, "fw_type"):
			old_value = e.inner_color.start
			e.inner_color.start = value
		elif key == "inner_color_end" and hasattr(e, "fw_type"):
			old_value = e.inner_color.end
			e.inner_color.end = value
		elif key == "outer_color_start" and hasattr(e, "fw_type"):
			old_value = e.outer_color.start
			e.outer_color.start = value
		elif key == "outer_color_end" and hasattr(e, "fw_type"):
			old_value = e.outer_color.end
			e.outer_color.end = value
		elif key == "position":
			pass  # 位置已在 _on_*_pos_changed 中更新
		self.property_changed.emit(e.id, key, value, old_value)

	def _on_traj_extra_changed(self) -> None:
		if isinstance(self._current_element, TrajectoryElement) and not self._loading:
			e = self._current_element
			e.k = self._spin_k.value();
			e.m0 = self._spin_m0.value()
			e.rho = self._spin_rho.value();
			e.particle_count = self._spin_particle_count.value()
			e.interval_ticks = self._spin_interval.value();
			e.points_per_tick = self._spin_pts_per_tick.value()
			e.range_x = self._spin_range_x.value();
			e.range_y = self._spin_range_y.value();
			e.range_z = self._spin_range_z.value()
			e.speed_factor = self._spin_speed_factor.value()
			self._emit_change("extra", None)

	def _on_fw_extra_changed(self) -> None:
		if isinstance(self._current_element, FireworkElement) and not self._loading:
			e = self._current_element
			e.speed = self._spin_speed.value();
			e.inner_speed = self._spin_inner_speed.value()
			e.outer_speed = self._spin_outer_speed.value();
			e.spread_angle = self._spin_spread.value()
			e.track_count = self._spin_track_count.value()
			e.radius = self._spin_radius.value();
			e.radial_speed = self._spin_radial_speed.value()
			if hasattr(e, 'horizontal_angle'):
				e.horizontal_angle = self._spin_h_angle.value()
				e.vertical_angle = self._spin_v_angle.value()
			self._emit_change("extra", None)

	def _block_all(self, block: bool) -> None:
		for typ in (QSpinBox, QDoubleSpinBox, QComboBox, QCheckBox, QLineEdit, QDial):
			for widget in self.findChildren(typ):
				widget.blockSignals(block)
