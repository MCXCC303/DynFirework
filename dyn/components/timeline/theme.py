"""时间线共享常量与调色板 所有子包共用布局常数和颜色函数."""

from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QWidget, QApplication

__all__ = [
	"HEADER_HEIGHT", "TRACK_LABEL_WIDTH", "WAVEFORM_HEIGHT",
	"TRACK_HEIGHT", "BLOCK_MIN_WIDTH", "PIXELS_PER_TICK_DEFAULT",
	"palette_colors", "propagate_palette",
]

HEADER_HEIGHT = 28
TRACK_LABEL_WIDTH = 120
WAVEFORM_HEIGHT = 40
TRACK_HEIGHT = 36
BLOCK_MIN_WIDTH = 8
PIXELS_PER_TICK_DEFAULT = 3.0

def palette_colors():
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
	for child in widget.findChildren(QWidget):
		if hasattr(child, "_update_colors"):
			child._update_colors()
