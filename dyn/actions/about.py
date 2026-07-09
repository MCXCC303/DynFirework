from PyQt5 import QtWidgets
from dyn.ui.dyn_help_ui import Ui_Dialog as DYNHelpUI
from dyn.ui.df_about_ui import Ui_Dialog as DFAboutUI


class DYNAboutWindow(QtWidgets.QDialog):
	def __init__(self):
		super().__init__()
		self.ui = DFAboutUI()
		self.ui.setupUi(self)
		self.show()


class DYNHelpWindow(QtWidgets.QDialog):
	def __init__(self):
		super().__init__()
		self.ui = DYNHelpUI()
		self.ui.setupUi(self)

		self.show()
