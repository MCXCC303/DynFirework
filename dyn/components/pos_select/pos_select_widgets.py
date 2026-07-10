"""位置选择器核心 Widget — 网格图、列表模型和新建点对话框."""

from __future__ import annotations

import math

from PySide6.QtCore import QModelIndex, Qt, Signal, QAbstractListModel, QPoint
from PySide6.QtGui import (
    QColor,
    QMouseEvent,
    QPainter,
    QPen,
    QPainterPath,
    QResizeEvent,
    QAction,
)
from PySide6.QtGui import QUndoStack
from PySide6.QtWidgets import (
    QWidget,
    QSizePolicy,
    QDialog,
    QMenu,
    QApplication,
)

from dyn.ui.pos_select.create_new_point_ui import Ui_Dialog as NewPointDialogUI
from dyn.lib.units import MinecraftPosition
from dyn.components.pos_select.pos_undo_commands import (
    AddPointCommand,
    RemovePointCommand,
    EditPointCommand,
)


# ═══════════════════════════════════════════════════════
# PixElementList — 列表模型
# ═══════════════════════════════════════════════════════

class PixElementList(QAbstractListModel):
    """位置点列表模型 — QListView 的数据源."""

    point_removed_sign = Signal(list)
    selection_changed = Signal(MinecraftPosition)

    @staticmethod
    def fg_change_accord_rela_lumin(bg_color: QColor) -> QColor:
        luminance = (
            0.299 * bg_color.red() + 0.587 * bg_color.green() + 0.114 * bg_color.blue()
        )
        return QColor(0, 0, 0, 255) if luminance > 127 else QColor(255, 255, 255, 255)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.stored_pix_list: list[MinecraftPosition] = []
        self.selected_element: MinecraftPosition | None = None

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self.stored_pix_list)

    def data(self, index, role=...):
        if not index.isValid() or index.row() >= len(self.stored_pix_list):
            return None
        elem = self.stored_pix_list[index.row()]
        if role == Qt.ItemDataRole.BackgroundRole:
            rgba = elem.pix_color.getRgb()
            return QColor(rgba[0], rgba[1], rgba[2], 127)
        elif role == Qt.ItemDataRole.DisplayRole:
            return f"{elem.label}\n({elem.x}, {elem.y}, {elem.z})"
        elif role == Qt.ItemDataRole.ForegroundRole:
            return self.fg_change_accord_rela_lumin(elem.pix_color)
        return None

    def get_element_list(self, renewed_list):
        self.beginResetModel()
        self.stored_pix_list = renewed_list
        self.endResetModel()

    def get_graph_selection(self, new_selection: MinecraftPosition):
        self.selected_element = new_selection
        self.selection_changed.emit(new_selection)

    def get_list_selection(self, selected, deselected):
        if selected.indexes():
            index = selected.indexes()[0]
            if index.row() < len(self.stored_pix_list):
                selected_element = self.stored_pix_list[index.row()]
                self.selection_changed.emit(selected_element)


# ═══════════════════════════════════════════════════════
# PixGraphWidget — 网格图
# ═══════════════════════════════════════════════════════

class PixGraphWidget(QWidget):
    """网格图（笛卡尔坐标）位置选择器.

    交互:
        左键点击: 选点/建点
        中键拖拽: 平移视图
        右键: 上下文菜单（编辑/删除/复制/在此新建/重置视图）
        滚轮: 以光标为锚点缩放
    """

    point_renewed_sign = Signal(list)
    selection_changed = Signal(MinecraftPosition)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.pix_size: int = 10
        self.center_x: int = 0
        self.center_y: int = 0
        self.offset_x: float = 0.0
        self.offset_y: float = 0.0

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMouseTracking(True)

        # 渲染参数
        self.pixmap_main_tick_line_width = 2
        self.pixmap_sec_tick_line_width = 1
        self.border_corner = 3
        self.tick_line_color = QColor(200, 200, 200)
        self.hovered_pix_color = QColor(160, 160, 160, 80)
        self.sign_font_color = QColor(120, 120, 120)
        self.selected_border_color = QColor(60, 120, 220)

        # 点数据
        self.selected_point: MinecraftPosition | None = None
        self.hovered_pix: QPainterPath | None = None
        self.hovered_grid_pos: tuple[int, int] | None = None
        self.stored_pix_list: list[MinecraftPosition] = []
        self.stored_pix_fastsearch: set[tuple[int, int]] = set()

        # 交互状态
        self._panning: bool = False
        self._pan_last: QPoint | None = None

        # 撤销栈
        self._undo_stack = QUndoStack(self)

        self.set_proper_pix_size()

    # ── 公共属性 ──────────────────────────────────────

    @property
    def undo_stack(self) -> QUndoStack:
        return self._undo_stack

    # ── 坐标转换 ──────────────────────────────────────

    def _grid_to_widget(self, gx: int, gz: int) -> tuple[float, float]:
        x = self.center_x + gx * self.pix_size + self.offset_x
        y = self.center_y + gz * self.pix_size + self.offset_y
        return x, y

    def _widget_to_grid(self, wx: int, wy: int) -> tuple[int, int]:
        dx = wx - self.center_x - self.offset_x
        dy = wy - self.center_y - self.offset_y
        gx = int(dx // self.pix_size)
        gz = int(dy // self.pix_size)
        return gx, gz

    # ── 绘制 ──────────────────────────────────────────

    def resizeEvent(self, a0: QResizeEvent) -> None:
        self.center_x = self.rect().center().x()
        self.center_y = self.rect().center().y()
        super().resizeEvent(a0)

    def paintEvent(self, event):
        p_bg = QPainter(self)
        p_bg.setRenderHint(QPainter.RenderHint.Antialiasing)
        self._paint_bg(p_bg)

        p_tick = QPainter(self)
        p_tick.setRenderHint(QPainter.RenderHint.Antialiasing)
        self._paint_tick_line(p_tick)
        self._paint_tick_line_arrow(p_tick)

        p_pt = QPainter(self)
        p_pt.setRenderHint(QPainter.RenderHint.Antialiasing)
        self._paint_stored_pix(p_pt)
        self._paint_hovered(p_pt)
        self._paint_center(p_pt)
        self._paint_selected(p_pt)

    def _paint_bg(self, painter: QPainter):
        painter.fillRect(self.rect(), QColor(255, 255, 255))

    def _paint_center(self, painter: QPainter):
        x, y = self._grid_to_widget(0, 0)
        s = self.pix_size
        painter.setPen(QPen(QColor(128, 128, 128), self.pixmap_main_tick_line_width))
        painter.drawRoundedRect(int(x), int(y), s, s, s / 2, s / 2)

    def _paint_tick_line(self, painter: QPainter):
        step = self.pix_size * 16
        painter.setPen(QPen(self.tick_line_color, self.pixmap_main_tick_line_width))

        origin_x, origin_y = self._grid_to_widget(0, 0)
        # 垂直线
        x = origin_x
        while x < self.width():
            painter.drawLine(int(x), 0, int(x), self.height())
            x += step
        x = origin_x - step
        while x >= 0:
            painter.drawLine(int(x), 0, int(x), self.height())
            x -= step
        # 水平线
        y = origin_y
        while y < self.height():
            painter.drawLine(0, int(y), self.width(), int(y))
            y += step
        y = origin_y - step
        while y >= 0:
            painter.drawLine(0, int(y), self.width(), int(y))
            y -= step

        # 细线
        fine_step = self.pix_size
        painter.setPen(QPen(self.tick_line_color, self.pixmap_sec_tick_line_width))
        origin_x, origin_y = self._grid_to_widget(0, 0)
        x = origin_x
        while x < self.width():
            painter.drawLine(int(x), 0, int(x), self.height())
            x += fine_step
        x = origin_x - fine_step
        while x >= 0:
            painter.drawLine(int(x), 0, int(x), self.height())
            x -= fine_step
        y = origin_y
        while y < self.height():
            painter.drawLine(0, int(y), self.width(), int(y))
            y += fine_step
        y = origin_y - fine_step
        while y >= 0:
            painter.drawLine(0, int(y), self.width(), int(y))
            y -= fine_step

    def _paint_tick_line_arrow(self, painter: QPainter):
        origin_x, origin_y = self._grid_to_widget(0, 0)
        painter.setPen(QPen(self.tick_line_color, self.pixmap_main_tick_line_width))
        # X 轴箭头
        r = self.width()
        painter.drawLine(r, int(origin_y), r - self.pix_size, int(origin_y) + self.pix_size // 2)
        painter.drawLine(r, int(origin_y), r - self.pix_size, int(origin_y) - self.pix_size // 2)
        # Z 轴箭头
        b = self.height()
        painter.drawLine(int(origin_x), b, int(origin_x) + self.pix_size // 2, b - self.pix_size)
        painter.drawLine(int(origin_x), b, int(origin_x) - self.pix_size // 2, b - self.pix_size)
        # 标签
        painter.setPen(QPen(self.sign_font_color, self.pixmap_main_tick_line_width))
        font = painter.font()
        font.setPixelSize(self.pix_size)
        painter.setFont(font)
        painter.drawText(r - self.pix_size, int(origin_y) - self.pix_size, "X")
        painter.drawText(int(origin_x) + self.pix_size, b - self.pix_size, "Z")

    def _paint_stored_pix(self, painter):
        for pt in self.stored_pix_list:
            x, y = self._grid_to_widget(int(pt.x), int(pt.z))
            s = self.pix_size
            path = QPainterPath()
            path.addRoundedRect(int(x), int(y), s, s, self.border_corner, self.border_corner)
            painter.fillPath(path, pt.pix_color)
            painter.setPen(QPen(pt.pix_color, self.pixmap_main_tick_line_width))
            painter.drawText(int(x) + s, int(y), pt.label)

    def _paint_hovered(self, painter: QPainter):
        if self.hovered_grid_pos is None:
            return
        gx, gz = self.hovered_grid_pos
        x, y = self._grid_to_widget(gx, gz)
        s = self.pix_size
        path = QPainterPath()
        path.addRoundedRect(int(x), int(y), s, s, self.border_corner, self.border_corner)
        painter.fillPath(path, self.hovered_pix_color)

    def _paint_selected(self, painter: QPainter):
        if self.selected_point is None:
            return
        try:
            x, y = self._grid_to_widget(int(self.selected_point.x), int(self.selected_point.z))
            s = self.pix_size
            painter.setPen(QPen(self.selected_border_color, 2))
            painter.drawRoundedRect(int(x), int(y), s, s, self.border_corner, self.border_corner)
        except Exception:
            pass

    # ── 事件处理 ──────────────────────────────────────

    def mousePressEvent(self, a0: QMouseEvent) -> None:
        if a0.button() == Qt.MiddleButton:
            self._panning = True
            self._pan_last = a0.pos()
            self.setCursor(Qt.ClosedHandCursor)
            return
        super().mousePressEvent(a0)

    def mouseMoveEvent(self, a0: QMouseEvent) -> None:
        if self._panning and self._pan_last is not None:
            delta = a0.pos() - self._pan_last
            self.offset_x += delta.x()
            self.offset_y += delta.y()
            self._pan_last = a0.pos()
            self.update()
            return

        # 更新悬停
        gx, gz = self._widget_to_grid(a0.pos().x(), a0.pos().y())
        self.hovered_grid_pos = (gx, gz)
        x, y = self._grid_to_widget(gx, gz)
        s = self.pix_size
        path = QPainterPath()
        path.addRoundedRect(int(x), int(y), s, s, self.border_corner, self.border_corner)
        self.hovered_pix = path
        self.update()

    def mouseReleaseEvent(self, a0: QMouseEvent) -> None:
        if self._panning:
            self._panning = False
            self._pan_last = None
            self.setCursor(Qt.ArrowCursor)
            return

        gx, gz = self._widget_to_grid(a0.pos().x(), a0.pos().y())

        if a0.button() == Qt.RightButton:
            self._show_context_menu(a0.pos(), gx, gz)
            return

        if a0.button() == Qt.LeftButton:
            self._handle_left_click(gx, gz)

    def _handle_left_click(self, gx: int, gz: int) -> None:
        if (gx, gz) in self.stored_pix_fastsearch:
            for pt in self.stored_pix_list:
                if int(pt.x) == gx and int(pt.z) == gz:
                    self.selected_point = pt
                    self.selection_changed.emit(pt)
                    self.update()
                    return
        else:
            dlg = NewPointEditorDialog((gx, gz))
            if dlg.exec() == QDialog.DialogCode.Accepted:
                pt = MinecraftPosition(dlg.x, dlg.y, dlg.z, label=dlg.name, main_color=dlg.color)
                self._undo_stack.push(
                    AddPointCommand(self.stored_pix_list, self.stored_pix_fastsearch, pt)
                )
                self.point_renewed_sign.emit(self.stored_pix_list)
                self.update()

    def _show_context_menu(self, pos: QPoint, gx: int, gz: int) -> None:
        menu = QMenu(self)

        point_here: MinecraftPosition | None = None
        for pt in self.stored_pix_list:
            if int(pt.x) == gx and int(pt.z) == gz:
                point_here = pt
                break

        if point_here is not None:
            act_edit = QAction("编辑点...", self)
            act_edit.triggered.connect(lambda: self._edit_point(point_here))
            menu.addAction(act_edit)

            act_del = QAction("删除点", self)
            act_del.triggered.connect(lambda: self._delete_point(point_here))
            menu.addAction(act_del)

            act_copy = QAction("复制坐标", self)
            act_copy.triggered.connect(lambda: QApplication.clipboard().setText(
                f"{point_here.x}, {point_here.y}, {point_here.z}"
            ))
            menu.addAction(act_copy)
            menu.addSeparator()

        act_new = QAction("在此新建点", self)
        act_new.triggered.connect(lambda: self._handle_left_click(gx, gz))
        menu.addAction(act_new)

        act_reset = QAction("重置视图", self)
        act_reset.triggered.connect(self._reset_view)
        menu.addAction(act_reset)

        menu.exec(self.mapToGlobal(pos))

    def _edit_point(self, pt: MinecraftPosition) -> None:
        dlg = NewPointEditorDialog((int(pt.x), int(pt.z)))
        dlg.ui.doubleSpinBox_X.setValue(pt.x)
        dlg.ui.doubleSpinBox_Z.setValue(pt.z)
        dlg.ui.doubleSpinBox_Y.setValue(pt.y)
        dlg.ui.lineEdit_Name.setText(pt.label)
        dlg.ui.spinBox_r.setValue(pt.pix_color.red())
        dlg.ui.spinBox_g.setValue(pt.pix_color.green())
        dlg.ui.spinBox_b.setValue(pt.pix_color.blue())

        if dlg.exec() == QDialog.DialogCode.Accepted:
            old_vals = {"x": pt.x, "y": pt.y, "z": pt.z, "label": pt.label, "color": pt.pix_color}
            pt.x = dlg.x; pt.y = dlg.y; pt.z = dlg.z
            pt.label = dlg.name; pt._main_color = dlg.color
            new_vals = {"x": pt.x, "y": pt.y, "z": pt.z, "label": pt.label, "color": pt.pix_color}
            self._undo_stack.push(EditPointCommand(pt, old_vals, new_vals))
            self.point_renewed_sign.emit(self.stored_pix_list)
            self.selection_changed.emit(pt)
            self.update()

    def _delete_point(self, pt: MinecraftPosition) -> None:
        self._undo_stack.push(
            RemovePointCommand(self.stored_pix_list, self.stored_pix_fastsearch, pt)
        )
        if self.selected_point is pt:
            self.selected_point = None
        self.point_renewed_sign.emit(self.stored_pix_list)
        self.update()

    def _reset_view(self) -> None:
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.set_proper_pix_size()
        self.update()

    # ── 缩放 ──────────────────────────────────────────

    def wheelEvent(self, a0):
        old_size = self.pix_size
        delta = a0.angleDelta().y()

        if delta > 0 and self.pix_size < 50:
            self.pix_size += 1
        elif delta < 0 and self.pix_size > 3:
            self.pix_size -= 1
        else:
            return

        if old_size != self.pix_size:
            ratio = self.pix_size / old_size
            cursor_x = a0.position().x() - self.center_x - self.offset_x
            cursor_y = a0.position().y() - self.center_y - self.offset_y
            self.offset_x -= cursor_x * (ratio - 1)
            self.offset_y -= cursor_y * (ratio - 1)

        self.update()

    def set_min_pix_size(self):
        self.set_pix_size(3)

    def set_max_pix_size(self):
        self.set_pix_size(50)

    def set_proper_pix_size(self):
        self.pix_size = int(min(self.width() / 40, self.height() / 40))
        self.pix_size = max(3, min(50, self.pix_size))
        self.update()

    def set_pix_size(self, size: int) -> None:
        self.pix_size = max(3, min(50, size))
        self.update()

    # ── 选择同步 ──────────────────────────────────────

    def get_list_selected_pix(self, selected_point: MinecraftPosition):
        self.selected_point = selected_point
        self.update()


# ═══════════════════════════════════════════════════════
# NewPointEditorDialog — 新建点对话框
# ═══════════════════════════════════════════════════════

class NewPointEditorDialog(QDialog):
    """新建/编辑位置点对话框."""

    def __init__(self, xz_pos: tuple) -> None:
        super().__init__()
        self.ui = NewPointDialogUI()
        self.ui.setupUi(self)
        self.xz_pos = xz_pos
        self.set_default()
        self.select_color()

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

    def set_red_value(self): self.ui.spinBox_r.setValue(255)
    def set_green_value(self): self.ui.spinBox_g.setValue(255)
    def set_blue_value(self): self.ui.spinBox_b.setValue(255)

    @property
    def y(self): return self.ui.doubleSpinBox_Y.value()

    @property
    def name(self): return self.ui.lineEdit_Name.text()

    @property
    def x(self): return self.ui.doubleSpinBox_X.value()

    @property
    def z(self): return self.ui.doubleSpinBox_Z.value()

    @property
    def color(self):
        return QColor(
            self.ui.spinBox_r.value(),
            self.ui.spinBox_g.value(),
            self.ui.spinBox_b.value(),
            int(math.sqrt((self.y + 1) * 255 / 256) * 16),
        )
