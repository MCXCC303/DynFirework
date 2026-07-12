"""关于对话框."""
from __future__ import annotations

import logging

from PySide6 import QtWidgets

from dyn.ui.df_about_ui import Ui_Dialog as DFAboutUI

log = logging.getLogger("dyn.actions.about")

class DYNAboutWindow(QtWidgets.QDialog):
	"""关于 DynFirework 对话框."""

	def __init__(self) -> None:
		super().__init__()
		log.debug("打开关于对话框")
		self.ui = DFAboutUI()
		self.ui.setupUi(self)
