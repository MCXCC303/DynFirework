from PyQt5.QtCore import pyqtSignal, QAbstractItemModel


class ElementBrowser(QAbstractItemModel):
    selection_changed = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        pass

    def data(self, index, role = ...):
        pass

