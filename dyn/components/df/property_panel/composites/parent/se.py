"""二次爆炸父级摘要表单 只读."""
from __future__ import annotations

from PySide6.QtWidgets import (
	QFormLayout, QLabel, QPushButton, QGroupBox,
)

from dyn.models.df.composites import CompositeElement
from dyn.models.df.values import FireworkType
from ..composite_base import CompositeBase

_FW_TYPE_NAMES = {
	FireworkType.SINGLE_LAYER: "单层烟花",
	FireworkType.DOUBLE_LAYER: "双层烟花",
	FireworkType.DIRECTIONAL: "定向烟花",
	FireworkType.CLUSTERED: "集束烟花",
	FireworkType.EXPANDING_SPHERE: "膨胀球烟花",
	FireworkType.NEBULA: "星云烟花",
}

_SEC_TYPE_NAMES = {
	"expanding": "扩散",
	"single_layer": "单层",
}

class ParentSEForm(CompositeBase):
	"""二次爆炸父级摘要 只读展示关键信息 提供位置选择按钮."""

	def _setup_position(self) -> None:
		self._grp_start = QGroupBox("初始位置")
		form = QFormLayout(self._grp_start)
		self._lbl_start_x = QLabel("0.00")
		self._lbl_start_y = QLabel("0.00")
		self._lbl_start_z = QLabel("0.00")
		for lbl in (self._lbl_start_x, self._lbl_start_y, self._lbl_start_z):
			lbl.setStyleSheet("font-family: monospace;")
		form.addRow("X:", self._lbl_start_x)
		form.addRow("Y:", self._lbl_start_y)
		form.addRow("Z:", self._lbl_start_z)
		btn = QPushButton("在地图上选择...")
		btn.clicked.connect(lambda: self.position_select_requested.emit("se_start"))
		form.addRow("", btn)
		self.layout().addWidget(self._grp_start)

		self._grp_mid = QGroupBox("中间位置")
		form = QFormLayout(self._grp_mid)
		self._lbl_mid_x = QLabel("0.00")
		self._lbl_mid_y = QLabel("80.00")
		self._lbl_mid_z = QLabel("0.00")
		for lbl in (self._lbl_mid_x, self._lbl_mid_y, self._lbl_mid_z):
			lbl.setStyleSheet("font-family: monospace;")
		form.addRow("X:", self._lbl_mid_x)
		form.addRow("Y:", self._lbl_mid_y)
		form.addRow("Z:", self._lbl_mid_z)
		btn = QPushButton("在地图上选择...")
		btn.clicked.connect(lambda: self.position_select_requested.emit("se_mid"))
		form.addRow("", btn)
		self.layout().addWidget(self._grp_mid)

		self._group_pos = self._grp_start

	def _setup_type_params(self) -> None:
		self._grp_type = QGroupBox("元素类型")
		form = QFormLayout(self._grp_type)
		self._lbl_primary_type = QLabel("")
		self._lbl_secondary_type = QLabel("")
		form.addRow("一级烟花:", self._lbl_primary_type)
		form.addRow("二级爆炸:", self._lbl_secondary_type)
		self.layout().addWidget(self._grp_type)

		self._lbl_hint = QLabel("请展开左侧树节点编辑具体参数")
		self._lbl_hint.setStyleSheet("color: #888; padding: 8px;")
		self.layout().addWidget(self._lbl_hint)

		self._sub_groups = [self._grp_mid, self._grp_type]

	def load(self, elem: CompositeElement) -> None:
		self._loading = True
		self._element = elem
		self.block_signals(True)

		self._hide_all()
		self._group_pos.show()

		sp = elem.se_start_position
		self._lbl_start_x.setText(f"{sp.x:.2f}")
		self._lbl_start_y.setText(f"{sp.y:.2f}")
		self._lbl_start_z.setText(f"{sp.z:.2f}")

		mp = elem.se_mid_position
		self._lbl_mid_x.setText(f"{mp.x:.2f}")
		self._lbl_mid_y.setText(f"{mp.y:.2f}")
		self._lbl_mid_z.setText(f"{mp.z:.2f}")
		self._grp_mid.show()

		self._lbl_primary_type.setText(
			_FW_TYPE_NAMES.get(elem.se_primary_type, elem.se_primary_type.value))
		self._lbl_secondary_type.setText(
			_SEC_TYPE_NAMES.get(elem.se_secondary_type, elem.se_secondary_type))
		self._grp_type.show()

		self._lbl_hint.show()

		self.block_signals(False)
		self._loading = False
		self._update_reset_buttons()

	def _load_type_params(self, elem: CompositeElement) -> None:
		pass
