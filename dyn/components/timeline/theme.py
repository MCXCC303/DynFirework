"""时间线共享常量与调色板."""

from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QWidget, QApplication

HEADER_HEIGHT = 28
TRACK_LABEL_WIDTH = 120
WAVEFORM_HEIGHT = 40
TRACK_HEIGHT = 28
BLOCK_MIN_WIDTH = 4
PIXELS_PER_TICK_DEFAULT = 3.0

def palette_colors():
	"""读取系统 palette，返回时间线各组件所需颜色字典."""
	pal = QApplication.palette()
	hl = pal.color(QPalette.Highlight)
	return {
		"bg": pal.color(QPalette.Base),
		"bg_alt": pal.color(QPalette.Window),
		"bg_dark": pal.color(QPalette.Window).darker(105),
		"text": pal.color(QPalette.Text),
		"text_dim": pal.color(QPalette.Text).lighter(150),
		"mid": pal.color(QPalette.Mid),
		"dark": pal.color(QPalette.Dark),
		"highlight": hl,
		"highlight_alpha": QColor(hl.red(), hl.green(), hl.blue(), 120),
		"cursor": QColor(255, 60, 60),
		"sel": QColor(255, 200, 60),
	}

def propagate_palette(widget: QWidget) -> None:
	"""遍历子 widget，调用 _update_colors()（如果存在）."""
	for child in widget.findChildren(QWidget):
		if hasattr(child, "_update_colors"):
			child._update_colors()
