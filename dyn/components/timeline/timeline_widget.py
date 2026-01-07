from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QPainterPath

from dyn.lib.base_class import AbstractFirework


class FireworkTimeLine(QWidget):
    selection_changed = pyqtSignal(AbstractFirework)

    def __init__(self):
        super().__init__()
        self.third_tick_line_color = None
        self.secondary_tick_line_color = None
        self.primary_tick_line_color = None
        self.third_tick_line_width = None
        self.secondary_tick_line_width = None
        self.primary_tick_line_width = None
        self.one_tick_width = None
        self.firework_list: list[AbstractFirework] = []
        self.bg_color = QColor(255, 255, 255)
        self.zero_tick_line_color = QColor(229, 107, 25)
        self.zero_tick_line_width = 2
        self.zero_blank_width = 100
        self.tracks = []

    @pyqtSlot(list)
    def update_fireworks(self, fireworks: list[AbstractFirework]):
        # 来源：元素列表
        self.firework_list = fireworks

    @pyqtSlot(AbstractFirework)
    def new_firework(self, firework: AbstractFirework):
        self.firework_list.append(firework)
        pass  # TODO

    def paintEvent(self, a0):
        p_bg = QPainter(self)
        p_bg.setRenderHint(QPainter.Antialiasing)
        self.paint_bg(p_bg)
        p_line = QPainter(self)
        p_line.setRenderHint(QPainter.Antialiasing)
        self.paint_zero_tick_line(p_line)
        self.paint_tick_lines(p_line)
        p_text = QPainter(self)
        p_text.setRenderHint(QPainter.Antialiasing)
        self.paint_tick_text(p_text)

        return super().paintEvent(a0)

    def paint_bg(self, bg_painter: QPainter):
        bg_painter.setPen(QPen(self.bg_color, 1))
        bg_painter.drawRect(self.rect())

    def paint_zero_tick_line(self, line_painter: QPainter):
        line_painter.setPen(QPen(self.zero_tick_line_color, self.zero_tick_line_width))
        line_painter.drawLine(self.zero_blank_width, 0, self.zero_blank_width, self.height())

    def paint_tick_lines(self, line_painter: QPainter):
        self.one_tick_width = 5
        self.primary_tick_line_width = 3
        self.secondary_tick_line_width = 2
        self.third_tick_line_width = 1
        self.primary_tick_line_color = QColor(120, 120, 120)
        self.secondary_tick_line_color = QColor(170, 170, 170)
        self.third_tick_line_color = QColor(200, 200, 200)
        paintable_width = self.width() - self.zero_blank_width
        for i in range(paintable_width // self.one_tick_width):
            if i % 20 == 0:
                line_painter.setPen(QPen(self.primary_tick_line_color, self.primary_tick_line_width))
                line_height = 8
            elif i % 10 == 0:
                line_painter.setPen(QPen(self.secondary_tick_line_color, self.secondary_tick_line_width))
                line_height = 5
            elif i % 5 == 0:
                line_painter.setPen(QPen(self.third_tick_line_color, self.third_tick_line_width))
                line_height = 3
            else:
                continue
            line_painter.drawLine(self.zero_blank_width + i * self.one_tick_width, 0,
                                  self.zero_blank_width + i * self.one_tick_width, line_height)
            line_painter.drawLine(self.zero_blank_width + i * self.one_tick_width, self.height() - line_height,
                                  self.zero_blank_width + i * self.one_tick_width, self.height())

    def paint_tick_text(self, text_painter: QPainter):
        pass

    def mouseMoveEvent(self, a0):
        return super().mouseMoveEvent(a0)

    def mousePressEvent(self, a0):
        return super().mousePressEvent(a0)

    def mouseReleaseEvent(self, a0):
        return super().mouseReleaseEvent(a0)

    def keyPressEvent(self, a0):
        # Delete键
        return super().keyPressEvent(a0)

    @pyqtSlot(list)
    def update_fireworks(self, fireworks: list[AbstractFirework]):
        self.firework_list = fireworks
