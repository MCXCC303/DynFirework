"""同步烟花父级摘要表单 只读."""
from __future__ import annotations

from PySide6.QtWidgets import (
	QFormLayout, QLabel, QPushButton, QGroupBox,
)

from dyn.models.df.composites import CompositeElement
from ..composite_base import CompositeBase

class ParentCEForm(CompositeBase):
	"""同步烟花父级摘要 只读展示关键信息 提供位置选择按钮."""

	def _setup_position(self) -> None:
		self._grp_center = QGroupBox("中心位置")
		form = QFormLayout(self._grp_center)
		self._lbl_pos_x = QLabel("0.00")
		self._lbl_pos_y = QLabel("0.00")
		self._lbl_pos_z = QLabel("0.00")
		for lbl in (self._lbl_pos_x, self._lbl_pos_y, self._lbl_pos_z):
			lbl.setStyleSheet("font-family: monospace;")
		form.addRow("X:", self._lbl_pos_x)
		form.addRow("Y:", self._lbl_pos_y)
		form.addRow("Z:", self._lbl_pos_z)
		btn = QPushButton("在地图上选择...")
		btn.clicked.connect(lambda: self.position_select_requested.emit("ce_pos"))
		form.addRow("", btn)
		self.layout().addWidget(self._grp_center)

		self._group_pos = self._grp_center

	def _setup_type_params(self) -> None:
		self._grp_type = QGroupBox("元素类型")
		form = QFormLayout(self._grp_type)
		self._lbl_type_info = QLabel("集束烟花 + 膨胀球")
		form.addRow("组合:", self._lbl_type_info)
		self._lbl_flicker = QLabel("")
		form.addRow("闪烁:", self._lbl_flicker)
		self.layout().addWidget(self._grp_type)

		self._lbl_hint = QLabel("请展开左侧树节点编辑具体参数")
		self._lbl_hint.setStyleSheet("color: #888; padding: 8px;")
		self.layout().addWidget(self._lbl_hint)

		self._sub_groups = [self._grp_type]

	def load(self, elem: CompositeElement) -> None:
		self._loading = True
		self._element = elem
		self.block_signals(True)

		self._hide_all()
		self._group_pos.show()

		cp = elem.ce_position
		self._lbl_pos_x.setText(f"{cp.x:.2f}")
		self._lbl_pos_y.setText(f"{cp.y:.2f}")
		self._lbl_pos_z.setText(f"{cp.z:.2f}")

		self._lbl_flicker.setText("是" if elem.ce_flicker else "否")
		self._grp_type.show()

		self._lbl_hint.show()

		self.block_signals(False)
		self._loading = False
		self._update_reset_buttons()

	def _load_type_params(self, elem: CompositeElement) -> None:
		pass
