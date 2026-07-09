from typing import Optional

import sys

from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QApplication, QWidget, QColorDialog, QSpinBox, QPushButton

from dyn.actions.about import DYNHelpWindow, DYNAboutWindow
from dyn.components.pos_select.pos_select_main import PosSelectMainWindow
from dyn.ui.mainwin_ui import Ui_MainWindow
from dyn.lib.units import MinecraftPosition
from dyn.components.timeline.timeline_widget import FireworkTimeLine


class MainWin(QtWidgets.QMainWindow):
	def __init__(self):
		super().__init__()
		self.firework_timeline = None
		self.position_selector_target = None
		self.position_selector = None
		self.ui = Ui_MainWindow()
		self.ui.setupUi(self)

		self.init_components()
		self.connect_actions()
		self.show()

	def init_components(self):
		self.position_selector: PosSelectMainWindow = PosSelectMainWindow()
		self.firework_timeline = FireworkTimeLine()
		self.ui.scrollArea_timeline.setWidget(self.firework_timeline)

	def connect_actions(self):
		self.connect_menubar_file_menu()
		self.connect_menubar_view_menu()
		self.connect_menubar_about_menu()
		self.connect_color_select_gradients()
		self.connect_color_dialogs()
		self.connect_signal_pos_selection()

	def connect_menubar_about_menu(self):
		self.ui.action_DynFirework.triggered.connect(lambda: DYNAboutWindow().exec_())
		self.ui.action_help.triggered.connect(lambda: DYNHelpWindow().exec_())

	def connect_menubar_file_menu(self):
		self.ui.action_exit.triggered.connect(lambda: self.close())

	def connect_menubar_view_menu(self):
		self.ui.action_view_element_list.triggered.connect(
			lambda checked: self.ui.frame_element_list.setVisible(checked))
		self.ui.action_view_timeline.triggered.connect(
			lambda checked: self.ui.frame_timeline.setVisible(checked))
		self.ui.action_view_checker.triggered.connect(lambda checked: self.ui.frame_checker.setVisible(checked))
		self.ui.action_view_base_traj.triggered.connect(lambda checked: self.ui.frame_traj.setVisible(checked))
		self.ui.action_view_base_firework.triggered.connect(
			lambda checked: self.ui.frame_firework.setVisible(checked))

	def connect_color_select_gradients(self):
		self.connect_color_select_widget(self.ui.checkBox_traj_gradient,
		                                 self.ui.widget_traj_color_end)
		self.connect_color_select_widget(self.ui.checkBox_firework_inner_gradient,
		                                 self.ui.widget_inner_firework_color_end)
		self.connect_color_select_widget(self.ui.checkBox_firework_outer_gradient,
		                                 self.ui.widget_outer_firework_color_end)

	@staticmethod
	def connect_color_select_widget(checkbox, widget):
		def toggle_widget_and_children(state):
			enabled = bool(state)
			widget.setEnabled(enabled)
			for child in widget.findChildren(QWidget):
				child.setEnabled(enabled)
			# button color
			buttons = widget.findChildren(QtWidgets.QPushButton)
			button_color = QColor(192, 192, 192)
			if enabled:
				button_color = QColor(0, 0, 0)
			for button in buttons:
				button.setStyleSheet(f"QPushButton {{ background-color: {button_color.name()}; }}")
			# spinbox values
			color_values = widget.findChildren(QtWidgets.QSpinBox)
			if color_values:
				color_values[0].setValue(button_color.red())
				color_values[1].setValue(button_color.green())
				color_values[2].setValue(button_color.blue())

		checkbox.stateChanged.connect(toggle_widget_and_children)
		toggle_widget_and_children(False)

	def connect_default_color_dialog(self, button: QPushButton,
	                                 spinbox_r: QSpinBox,
	                                 spinbox_g: QSpinBox,
	                                 spinbox_b: QSpinBox):
		@pyqtSlot()
		def on_color_select_button_clicked():
			color = QColor(spinbox_r.value(), spinbox_g.value(), spinbox_b.value())
			color_select = QColorDialog().getColor(color, self, "选择颜色")
			if color_select.isValid():
				button.setStyleSheet(f"QPushButton {{ background-color: {color.name()}; }}")
				spinbox_r.setValue(color_select.red())
				spinbox_g.setValue(color_select.green())
				spinbox_b.setValue(color_select.blue())

		button.clicked.connect(on_color_select_button_clicked)

	def connect_color_dialogs(self):
		# traj
		self.connect_default_color_dialog(self.ui.pushButton_traj_color_select_start,
		                                  self.ui.spinBox_traj_color_start_r,
		                                  self.ui.spinBox_traj_color_start_g,
		                                  self.ui.spinBox_traj_color_start_b)
		self.connect_default_color_dialog(self.ui.pushButton_traj_color_select_end,
		                                  self.ui.spinBox_traj_color_end_r,
		                                  self.ui.spinBox_traj_color_end_g,
		                                  self.ui.spinBox_traj_color_end_b)
		# Firework (inner/outer)
		self.connect_default_color_dialog(self.ui.pushButton_firework_inner_color_select_start,
		                                  self.ui.spinBox_firework_inner_color_start_r,
		                                  self.ui.spinBox_firework_inner_color_start_g,
		                                  self.ui.spinBox_firework_inner_color_start_b)
		self.connect_default_color_dialog(self.ui.pushButton_firework_inner_color_select_end,
		                                  self.ui.spinBox_firework_inner_color_end_r,
		                                  self.ui.spinBox_firework_inner_color_end_g,
		                                  self.ui.spinBox_firework_inner_color_end_b)
		self.connect_default_color_dialog(self.ui.pushButton_firework_outer_color_select_start,
		                                  self.ui.spinBox_firework_outer_color_start_r,
		                                  self.ui.spinBox_firework_outer_color_start_g,
		                                  self.ui.spinBox_firework_outer_color_start_b)
		self.connect_default_color_dialog(self.ui.pushButton_firework_outer_color_select_end,
		                                  self.ui.spinBox_firework_outer_color_end_r,
		                                  self.ui.spinBox_firework_outer_color_end_g,
		                                  self.ui.spinBox_firework_outer_color_end_b)
		trajectory_color_select_start_init_color = QColor(255, 165, 0)
		self.ui.spinBox_traj_color_start_r.setValue(trajectory_color_select_start_init_color.red())
		self.ui.spinBox_traj_color_start_g.setValue(trajectory_color_select_start_init_color.green())
		self.ui.spinBox_traj_color_start_b.setValue(trajectory_color_select_start_init_color.blue())
		self.ui.pushButton_traj_color_select_start.setStyleSheet(
			f"QPushButton {{ background-color: {trajectory_color_select_start_init_color.name()}; }}")
		firework_color_select_start_init_color = QColor(0, 0, 255)
		self.ui.spinBox_firework_inner_color_start_r.setValue(firework_color_select_start_init_color.red())
		self.ui.spinBox_firework_inner_color_start_g.setValue(firework_color_select_start_init_color.green())
		self.ui.spinBox_firework_inner_color_start_b.setValue(firework_color_select_start_init_color.blue())
		self.ui.pushButton_firework_inner_color_select_start.setStyleSheet(
			f"QPushButton {{ background-color: {firework_color_select_start_init_color.name()}; }}")
		self.ui.spinBox_firework_outer_color_start_r.setValue(firework_color_select_start_init_color.red())
		self.ui.spinBox_firework_outer_color_start_g.setValue(firework_color_select_start_init_color.green())
		self.ui.spinBox_firework_outer_color_start_b.setValue(firework_color_select_start_init_color.blue())
		self.ui.pushButton_firework_outer_color_select_start.setStyleSheet(
			f"QPushButton {{ background-color: {firework_color_select_start_init_color.name()}; }}")

	def connect_signal_pos_selection(self):
		self.position_selector.send_chosen_point.connect(self.update_position_spinboxes)

	# 点选择
	@pyqtSlot()
	def on_pushButton_select_end_point_clicked(self):
		self.position_selector_target = "end"
		self.position_selector.showNormal()

	@pyqtSlot()
	def on_pushButton_select_start_point_clicked(self):
		self.position_selector_target = "start"
		self.position_selector.showNormal()

	@pyqtSlot(MinecraftPosition)
	def update_position_spinboxes(self, point):
		if self.position_selector_target == "start":
			self.ui.doubleSpinBox_start_x.setValue(point.x)
			self.ui.doubleSpinBox_start_y.setValue(point.y)
			self.ui.doubleSpinBox_start_z.setValue(point.z)
		elif self.position_selector_target == "end":
			self.ui.doubleSpinBox_end_x.setValue(point.x)
			self.ui.doubleSpinBox_end_y.setValue(point.y)
			self.ui.doubleSpinBox_end_z.setValue(point.z)

	@pyqtSlot(int)
	def on_horizontalSlider_vertical_angle_valueChanged(self, value):
		self.ui.doubleSpinBox_vertical_angle.setValue(value)

	@pyqtSlot()
	def on_doubleSpinBox_vertical_angle_editingFinished(self):
		self.ui.horizontalSlider_vertical_angle.setValue(int(self.ui.doubleSpinBox_vertical_angle.value()))

	@pyqtSlot(int)
	def on_horizontalSlider_horizontal_angle_valueChanged(self, value):
		self.ui.doubleSpinBox_horizontal_angle.setValue(value)

	@pyqtSlot()
	def on_doubleSpinBox_horizontal_angle_editingFinished(self):
		self.ui.horizontalSlider_horizontal_angle.setValue(int(self.ui.doubleSpinBox_horizontal_angle.value()))


if __name__ == "__main__":
	app = QApplication(sys.argv)
	exp = MainWin()
	sys.exit(app.exec_())
