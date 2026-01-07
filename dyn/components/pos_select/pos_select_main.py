import sys
import json
from dataclasses import asdict

from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal, QItemSelectionModel
from PyQt5.QtWidgets import QApplication, QMainWindow, QGridLayout, QAbstractItemView

from dyn.ui.pos_select.pos_select_graph_ui import Ui_MainWindow as PosSelectMainUI
from dyn.lib.units import MinecraftPosition
from dyn.components.pos_select.pos_select_widgets import PixGraphWidget, PixElementList


class PosSelectMainWindow(QMainWindow):
    send_chosen_point: pyqtSignal = pyqtSignal(MinecraftPosition)

    def __init__(self):
        super().__init__()
        self._chosen_point: MinecraftPosition | None = None
        self.ui = PosSelectMainUI()
        self.ui.setupUi(self)

        self.pix_graph = PixGraphWidget()
        self.pixGraphLayout = QGridLayout(self.ui.widget)
        self.pixGraphLayout.setSpacing(0)
        self.pixGraphLayout.setContentsMargins(0, 0, 0, 0)
        self.pixGraphLayout.addWidget(self.pix_graph, 0, 0)

        self.pix_element_list = PixElementList()
        self.ui.listView_element.setModel(self.pix_element_list)
        self.ui.listView_element.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        self.ui.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(self.chosen_point is not None)

        self.signal_connect()
        self.connect_menu_toggles()

    @property
    def chosen_point(self) -> MinecraftPosition:
        return self._chosen_point

    @chosen_point.setter
    def chosen_point(self, point: MinecraftPosition):
        self._chosen_point = point
        self.ui.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(self.chosen_point is not None)

    def connect_menu_toggles(self):
        self.ui.action_exit.setChecked(True)
        self.ui.action_exit.triggered.connect(lambda: self.close())
        self.ui.buttonBox.rejected.connect(lambda: self.close())
        self.ui.buttonBox.accepted.connect(self.confirm_selection)
        self.ui.action_pixsize_min.triggered.connect(self.pix_graph.set_min_pix_size)
        self.ui.action_pixsize_max.triggered.connect(self.pix_graph.set_max_pix_size)
        self.ui.action_pixsize_proper.triggered.connect(self.pix_graph.set_proper_pix_size)

    def confirm_selection(self):
        self.send_chosen_point.emit(self.chosen_point)
        print(self.chosen_point.position_text)
        self.close()

    def selection_text_change(self):
        self.ui.label_selection.setText(f"已选中 ({self.chosen_point.x}, {self.chosen_point.y}, {self.chosen_point.z})")

    def selection_point_border_change(self):
        self.pix_graph.get_list_selected_pix(self.chosen_point)

    def get_chosen_point(self, point: MinecraftPosition):
        self.chosen_point = point
        self.handle_chosen_point()

    def handle_chosen_point(self):
        self.selection_text_change()
        self.selection_point_border_change()
        self.update_list_selection()

    def update_list_selection(self):
        index = self.pix_element_list.stored_pix_list.index(self.chosen_point)
        model_index = self.pix_element_list.index(index)
        self.ui.listView_element.selectionModel().select(model_index, QItemSelectionModel.ClearAndSelect)

    def signal_connect(self):
        self.pix_graph.point_renewed_sign.connect(self.pix_element_list.get_element_list)
        self.pix_graph.selection_changed.connect(self.pix_element_list.get_graph_selection)
        self.pix_graph.selection_changed.connect(self.get_chosen_point)

        self.pix_element_list.selection_changed.connect(self.get_chosen_point)
        self.ui.listView_element.selectionModel().selectionChanged.connect(self.pix_element_list.get_list_selection)

    def export_data(self):
        try:
            with open("../../../learn1/radar_practice/data.json", "w") as jsonfile:
                json.dump([asdict(s.export_obj) for s in self.pix_element_list.stored_pix_list], jsonfile, indent=2)
        except Exception as e:
            print(f"导出数据时出错: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = PosSelectMainWindow()
    win.showNormal()
    sys.exit(app.exec_())
