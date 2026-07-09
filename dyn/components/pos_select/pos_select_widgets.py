import math

from PyQt5.QtCore import QModelIndex, Qt, pyqtSignal, QAbstractListModel
from PyQt5.QtGui import (
	QColor,
	QMouseEvent,
	QPainter,
	QPen,
	QPainterPath,
	QResizeEvent,
)
from PyQt5.QtWidgets import QWidget, QSizePolicy, QDialog

from dyn.ui.pos_select.create_new_point_ui import Ui_Dialog as NewPointDialogUI
from dyn.lib.units import MinecraftPosition


class PixElementList(QAbstractListModel):
	point_removed_sign: pyqtSignal = pyqtSignal(list)
	selection_changed: pyqtSignal = pyqtSignal(
		MinecraftPosition)

	# SOLVED: 用QListView.selectionModel().selectionChanged信号重写
	# 现在好像也不是那么需要重写了，直接使用内部传输后使用自定义模型向外发送

	@staticmethod
	def fg_change_accord_rela_lumin(bg_color: QColor) -> QColor:
		luminance = (
			0.299 * bg_color.red() + 0.587 * bg_color.green() + 0.114 * bg_color.blue()
		)
		return QColor(0, 0, 0, 255) if luminance > 127 else QColor(255, 255, 255, 255)

	def __init__(self, parent=None) -> None:
		super().__init__(parent)
		self.stored_pix_list: list[MinecraftPosition] = []
		self.selected_element = None

	def rowCount(self, parent=QModelIndex()) -> int:
		return len(self.stored_pix_list)

	def data(self, index, role=...):
		to_show_element = self.stored_pix_list[index.row()]
		if role == Qt.ItemDataRole.BackgroundRole:
			return QColor(*(to_show_element.pix_color.getRgb()[:3]), alpha=127)
		elif role == Qt.ItemDataRole.DisplayRole:
			return f"{to_show_element.label}\n({to_show_element.x}, {to_show_element.y}, {to_show_element.z})"
		elif role == Qt.ItemDataRole.TextColorRole:
			return self.fg_change_accord_rela_lumin(to_show_element.pix_color)
		else:
			return None

	def get_element_list(self, renewed_list):
		self.beginResetModel()
		self.stored_pix_list = renewed_list
		self.endResetModel()
		self.layoutChanged.emit()

	def get_graph_selection(self, new_selection: MinecraftPosition):
		self.selected_element = new_selection
		self.selection_changed.emit(new_selection)

	def get_list_selection(self, selected, deselected):
		# 内部传输来自 QListView.selectionModel().selectionChanged信号
		if selected.indexes():
			index = selected.indexes()[0]
			selected_element = self.stored_pix_list[index.row()]
			self.selection_changed.emit(selected_element)


class PixGraphWidget(QWidget):
	point_renewed_sign: pyqtSignal = pyqtSignal(list)
	selection_changed: pyqtSignal = pyqtSignal(MinecraftPosition)

	def __init__(self, parent=None):
		super().__init__(parent)
		self.pix_size = None
		self.center_y = None
		self.center_x = None
		self.center_point = None
		self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
		self.setMouseTracking(True)
		self.set_proper_pix_size()
		self.pixmap_main_tick_line_width = 2
		self.pixmap_sec_tick_line_width = 1
		self.border_corner = 3
		self.tick_line_color = QColor(200, 200, 200)
		self.hovered_pix_color = QColor(160, 160, 160)
		self.sign_font_color = QColor(120, 120, 120)

		self.selected_point: MinecraftPosition | None = None
		self.hovered_pix = None
		self.position_to_choose = None
		self.stored_pix_list: list[MinecraftPosition] = []
		self.stored_pix_fastsearch = set()

	def resizeEvent(self, a0: QResizeEvent) -> None:
		self.center_point = (self.rect().center().x(), self.rect().center().y())
		self.center_x = self.center_point[0]
		self.center_y = self.center_point[1]
		self.set_proper_pix_size()
		self.update()
		return super().resizeEvent(a0)

	def paintEvent(self, event):
		p_bg = QPainter(self)
		p_bg.setRenderHint(QPainter.RenderHint.Antialiasing)
		self.paint_bg(p_bg)

		p_tick_line = QPainter(self)
		p_tick_line.setRenderHint(QPainter.RenderHint.Antialiasing)
		self.paint_tick_line(p_tick_line)
		self.paint_tick_line_arrow(p_tick_line)
		# p_tick_line.setPen(QPen(QColor(255, 0, 0), 3))
		# p_tick_line.drawLine(200, 10, 20, 4)

		p_point = QPainter(self)
		p_point.setRenderHint(QPainter.RenderHint.Antialiasing)
		# 绘制顺序：存储点->鼠标指针->中心标志
		self.paint_stored_pix(p_point)
		self.paint_hovered_pix(p_point)
		self.paint_central_point(p_point)
		self.paint_selected_pix(p_point)
		return super().paintEvent(event)

	def paint_central_point(self, painter: QPainter):
		x = self.center_x
		y = self.center_y
		width = height = self.pix_size
		painter.setPen(QPen(QColor(128, 128, 128), self.pixmap_main_tick_line_width))
		painter.drawRoundedRect(x, y, width, height, width / 2, height / 2)

	def paint_bg(self, painter: QPainter):
		painter.fillRect(self.rect(), QColor(255, 255, 255))

	def paint_tick_line(self, painter: QPainter):
		# 主刻度线
		painter.setPen(QPen(self.tick_line_color, self.pixmap_main_tick_line_width))
		for x in range(self.center_x, self.width(), self.pix_size * 16):
			painter.drawLine(x, 0, x, self.height())
		for x in range(self.center_x, 0, -self.pix_size * 16):
			painter.drawLine(x, 0, x, self.height())
		for y in range(self.center_y, self.height(), self.pix_size * 16):
			painter.drawLine(0, y, self.width(), y)
		for y in range(self.center_y, 0, -self.pix_size * 16):
			painter.drawLine(0, y, self.width(), y)

		# 次刻度线
		painter.setPen(QPen(self.tick_line_color, self.pixmap_sec_tick_line_width))
		for x in range(self.center_x, self.width(), self.pix_size):
			painter.drawLine(x, 0, x, self.height())
		for x in range(self.center_x, 0, -self.pix_size):
			painter.drawLine(x, 0, x, self.height())
		for y in range(self.center_y, self.height(), self.pix_size):
			painter.drawLine(0, y, self.width(), y)
		for y in range(self.center_y, 0, -self.pix_size):
			painter.drawLine(0, y, self.width(), y)

	def paint_tick_line_arrow(self, painter: QPainter):
		arrow_top_x = self.width(), self.center_y
		arrow_top_z = self.center_x, self.height()
		painter.setPen(QPen(self.tick_line_color, self.pixmap_main_tick_line_width))
		painter.drawLine(*arrow_top_z, self.center_x + int(self.pix_size / 2), self.height() - self.pix_size)
		painter.drawLine(*arrow_top_z, self.center_x - int(self.pix_size / 2), self.height() - self.pix_size)
		painter.drawLine(*arrow_top_x, self.width() - self.pix_size, self.center_y + int(self.pix_size / 2))
		painter.drawLine(*arrow_top_x, self.width() - self.pix_size, self.center_y - int(self.pix_size / 2))
		# X/Z
		painter.setPen(QPen(self.sign_font_color, self.pixmap_main_tick_line_width))
		font = painter.font()
		font.setPixelSize(self.pix_size)
		painter.setFont(font)
		text_X_pos_x = self.width() - self.pix_size
		text_X_pos_y = self.center_y - self.pix_size
		text_Z_pos_x = self.center_x + self.pix_size
		text_Z_pos_y = self.height() - self.pix_size
		painter.drawText(text_X_pos_x, text_X_pos_y, "X")
		painter.drawText(text_Z_pos_x, text_Z_pos_y, "Z")

	def paint_hovered_pix(self, painter: QPainter):
		if self.hovered_pix is not None:
			painter.fillPath(self.hovered_pix, self.hovered_pix_color)

	def get_list_selected_pix(self, selected_point: MinecraftPosition):
		# 接受ListView的selectionChanged信号
		self.selected_point = selected_point
		self.update()

	def paint_selected_pix(self, painter: QPainter):
		if self.selected_point is None:
			return
		try:
			painter.drawRoundedRect(
				int(self.selected_point.x * self.pix_size + self.center_x),
				int(self.selected_point.z * self.pix_size + self.center_y),
				self.pix_size,
				self.pix_size,
				self.border_corner,
				self.border_corner,
			)
		except Exception as e:
			# 你好python弱类型检查，我日你仙人
			# Qt我是没说你吗，报错不发送到控制台直接抛出6/ABRT也是有你的
			print(f"绘制选中点时出错: {e}")

	def mouseMoveEvent(self, a0: QMouseEvent) -> None:
		# 获取量化后的鼠标指针
		mouse_pos = a0.x(), a0.y()
		selected_x, selected_y = self.calculate_selected_pix_corner_pos(mouse_pos)
		hovered_pix = QPainterPath()
		hovered_pix.addRoundedRect(
			selected_x + self.center_x,
			selected_y + self.center_y,
			self.pix_size,
			self.pix_size,
			self.border_corner,
			self.border_corner,
		)
		self.hovered_pix = hovered_pix
		self.update()
		return super().mouseMoveEvent(a0)

	def calculate_selected_pix_corner_pos(self, mouse_pos: tuple):
		selected_dx = (mouse_pos[0] - self.center_x) // self.pix_size * self.pix_size
		selected_dy = (mouse_pos[1] - self.center_y) // self.pix_size * self.pix_size
		return selected_dx, selected_dy

	def mouseReleaseEvent(self, a0: QMouseEvent) -> None:
		mouse_pos = a0.x(), a0.y()
		selected_dx, selected_dz = self.calculate_selected_pix_corner_pos(mouse_pos)
		selected_dx = selected_dx / self.pix_size
		selected_dz = selected_dz / self.pix_size
		if a0.button() == Qt.MouseButton.RightButton:
			# 弹出菜单，删除已有点
			return super().mousePressEvent(a0)
		if (selected_dx, selected_dz) not in self.stored_pix_fastsearch:
			# 新建点
			new_point = NewPointEditorDialog((selected_dx, selected_dz))
			if new_point.exec_() == QDialog.DialogCode.Accepted:
				confirmed_dx, confirmed_dz = new_point.x, new_point.z
				confirmed_y = new_point.y
				label_color = new_point.color
				new_point_name = new_point.name
				self.stored_pix_list.append(
					MinecraftPosition(
						confirmed_dx,
						confirmed_y,
						confirmed_dz,
						main_color=label_color,
						label=new_point_name,
					)
				)
				self.stored_pix_fastsearch.add((confirmed_dx, confirmed_dz))
				self.point_renewed_sign.emit(self.stored_pix_list)
				self.update()
		else:
			# 选中点编辑
			for pix in self.stored_pix_list:
				if pix.x == selected_dx and pix.z == selected_dz:
					self.selected_point = pix
					break
			self.selection_changed.emit(self.selected_point)
			return super().mousePressEvent(a0)
		return super().mousePressEvent(a0)

	def paint_stored_pix(self, painter):
		for pix in self.stored_pix_list:
			selected_pix = QPainterPath()
			selected_pix.addRoundedRect(
				pix.x * self.pix_size + self.center_x,
				pix.z * self.pix_size + self.center_y,
				self.pix_size,
				self.pix_size,
				self.border_corner,
				self.border_corner,
			)
			painter.fillPath(selected_pix, pix.pix_color)
			# point text label
			painter.setPen(QPen(pix.pix_color, self.pixmap_main_tick_line_width))
			label_pos_x = int(pix.x * self.pix_size + self.center_x + self.pix_size)
			label_pos_y = int(pix.z * self.pix_size + self.center_y)
			painter.drawText(label_pos_x, label_pos_y, str(pix.label))

	def wheelEvent(self, a0):
		d_angle = a0.angleDelta().y()
		if d_angle > 0 and self.pix_size < 50:
			self.pix_size += 1
			self.update()
		elif d_angle < 0 and self.pix_size > 3:
			self.pix_size -= 1
			self.update()
		else:
			return super().wheelEvent(a0)
		return super().wheelEvent(a0)

	def set_min_pix_size(self):
		self.pix_size = 3
		self.update()

	def set_max_pix_size(self):
		self.pix_size = 50
		self.update()

	def set_proper_pix_size(self):
		self.pix_size = int(min(self.width() / 40, self.height() / 40))
		self.update()


class NewPointEditorDialog(QDialog):
	def __init__(self, xz_pos: tuple) -> None:
		super().__init__()
		self.ui = NewPointDialogUI()
		self.ui.setupUi(self)
		self.xz_pos = xz_pos
		self.set_default()
		self.select_color()

		self.show()

	def set_default(self):
		self.ui.doubleSpinBox_X.setValue(self.xz_pos[0])
		self.ui.doubleSpinBox_Z.setValue(self.xz_pos[1])
		self.ui.lineEdit_Name.setText("New Point")

	def select_color(self):
		self.ui.pushButton_color_red.clicked.connect(self.clear_value)
		self.ui.pushButton_color_red.clicked.connect(self.set_red_value)
		self.ui.pushButton_color_blue.clicked.connect(self.clear_value)
		self.ui.pushButton_color_blue.clicked.connect(self.set_blue_value)
		self.ui.pushButton_color_green.clicked.connect(self.clear_value)
		self.ui.pushButton_color_green.clicked.connect(self.set_green_value)

		self.ui.pushButton_color_yellow.clicked.connect(self.clear_value)
		self.ui.pushButton_color_yellow.clicked.connect(self.set_red_value)
		self.ui.pushButton_color_yellow.clicked.connect(self.set_green_value)

		self.ui.pushButton_color_purple.clicked.connect(self.clear_value)
		self.ui.pushButton_color_purple.clicked.connect(self.set_red_value)
		self.ui.pushButton_color_purple.clicked.connect(self.set_blue_value)

		self.ui.pushButton_color_cyan.clicked.connect(self.clear_value)
		self.ui.pushButton_color_cyan.clicked.connect(self.set_blue_value)
		self.ui.pushButton_color_cyan.clicked.connect(self.set_green_value)

		self.ui.pushButton_color_black.clicked.connect(self.clear_value)

	def clear_value(self):
		self.ui.spinBox_r.setValue(0)
		self.ui.spinBox_g.setValue(0)
		self.ui.spinBox_b.setValue(0)

	def set_red_value(self):
		self.ui.spinBox_r.setValue(255)

	def set_green_value(self):
		self.ui.spinBox_g.setValue(255)

	def set_blue_value(self):
		self.ui.spinBox_b.setValue(255)

	@property
	def y(self):
		return self.ui.doubleSpinBox_Y.value()

	@property
	def name(self):
		return self.ui.lineEdit_Name.text()

	@property
	def x(self):
		return self.ui.doubleSpinBox_X.value()

	@property
	def z(self):
		return self.ui.doubleSpinBox_Z.value()

	@property
	def color(self):
		return QColor(
			self.ui.spinBox_r.value(),
			self.ui.spinBox_g.value(),
			self.ui.spinBox_b.value(),
			int(math.sqrt((self.y + 1) * 255 / 256) * 16),
		)
