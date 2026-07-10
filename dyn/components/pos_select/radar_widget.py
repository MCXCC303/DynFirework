"""雷达图组件 - 极坐标位置选择器."""

from __future__ import annotations

import math

from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtGui import (
    QColor,
    QMouseEvent,
    QPainter,
    QPen,
    QPainterPath,
    QWheelEvent,
    QResizeEvent,
    QAction,
    QUndoStack,
)
from PySide6.QtWidgets import (
    QWidget,
    QSizePolicy,
    QDialog,
    QMenu,
)

from dyn.lib.units import MinecraftPosition
from dyn.components.pos_select.pos_undo_commands import (
    AddPointCommand,
    RemovePointCommand,
    EditPointCommand,
)


class RadarWidget(QWidget):
    """雷达图(极坐标)位置选择器."""

    point_renewed_sign = Signal(list)
    selection_changed = Signal(MinecraftPosition)

    RING_INTERVAL = 16
    ANGLE_INTERVAL = 30

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.pix_size: int = 10
        self.center_x: int = 0
        self.center_y: int = 0
        self.offset_x: float = 0.0
        self.offset_y: float = 0.0

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMouseTracking(True)

        self.ring_color = QColor(180, 180, 190)
        self.ring_major_color = QColor(140, 140, 155)
        self.radial_color = QColor(180, 180, 190, 120)
        self.bg_color = QColor(248, 248, 250)
        self.hovered_color = QColor(160, 160, 160, 80)
        self.selected_border_color = QColor(60, 120, 220)
        self.center_color = QColor(128, 128, 128)
        self.axis_color = QColor(140, 140, 155)

        self.selected_point: MinecraftPosition | None = None
        self.hovered_grid_pos: tuple[int, int] | None = None
        self.stored_pix_list: list[MinecraftPosition] = []
        self.stored_pix_fastsearch: set[tuple[int, int]] = set()

        self._panning: bool = False
        self._pan_last: QPoint | None = None
        self._undo_stack = QUndoStack(self)

        self.set_proper_pix_size()

    @property
    def undo_stack(self) -> QUndoStack:
        return self._undo_stack

    def set_pix_size(self, size: int) -> None:
        self.pix_size = max(3, min(50, size))
        self.update()

    def set_proper_pix_size(self) -> None:
        self.pix_size = int(min(self.width() / 40, self.height() / 40))
        self.pix_size = max(3, min(50, self.pix_size))
        self.update()

    def set_min_pix_size(self) -> None: self.set_pix_size(3)
    def set_max_pix_size(self) -> None: self.set_pix_size(50)

    def _gx(self, gx: int, gz: int) -> float:
        return self.center_x + gx * self.pix_size + self.offset_x

    def _gy(self, gx: int, gz: int) -> float:
        return self.center_y + gz * self.pix_size + self.offset_y

    def _widget_to_grid(self, wx: int, wy: int) -> tuple[int, int]:
        gx = int((wx - self.center_x - self.offset_x) // self.pix_size)
        gz = int((wy - self.center_y - self.offset_y) // self.pix_size)
        return gx, gz

    def paintEvent(self, event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        try:
            self._paint_bg(p)
            self._paint_rings(p)
            self._paint_radial_lines(p)
            self._paint_axes(p)
            self._paint_stored_points(p)
            self._paint_hovered(p)
            self._paint_center(p)
            self._paint_selected(p)
        finally:
            p.end()

    def _paint_bg(self, p: QPainter) -> None:
        p.fillRect(self.rect(), self.bg_color)

    def _paint_rings(self, p: QPainter) -> None:
        cx, cy = int(self._gx(0, 0)), int(self._gy(0, 0))
        center = QPoint(cx, cy)
        max_px = int(max(self.width(), self.height()) * 1.5)
        for r in range(self.RING_INTERVAL * self.pix_size, max_px, self.RING_INTERVAL * self.pix_size):
            is_major = (r // self.pix_size) % (self.RING_INTERVAL * 4) == 0
            p.setPen(QPen(self.ring_major_color if is_major else self.ring_color, 2 if is_major else 1))
            p.drawEllipse(center, r, r)

    def _paint_radial_lines(self, p: QPainter) -> None:
        cx, cy = int(self._gx(0, 0)), int(self._gy(0, 0))
        max_r = max(self.width(), self.height()) * 1.5
        p.setPen(QPen(self.radial_color, 1))
        for angle in range(0, 360, self.ANGLE_INTERVAL):
            rad = math.radians(angle)
            ex, ey = int(cx + math.cos(rad) * max_r), int(cy + math.sin(rad) * max_r)
            p.drawLine(cx, cy, ex, ey)
        p.setPen(QPen(self.ring_major_color, 2))
        for angle in (0, 90, 180, 270):
            rad = math.radians(angle)
            ex, ey = int(cx + math.cos(rad) * max_r), int(cy + math.sin(rad) * max_r)
            p.drawLine(cx, cy, ex, ey)

    def _paint_axes(self, p: QPainter) -> None:
        """绘制主轴箭头和 X/Z 标签."""
        cx, cy = int(self._gx(0, 0)), int(self._gy(0, 0))
        max_r = max(self.width(), self.height()) * 1.5
        font = p.font(); font.setPixelSize(self.pix_size); p.setFont(font)
        arrow_len = self.pix_size

        for angle, label in [(0, "X"), (90, "Z"), (180, "-X"), (270, "-Z")]:
            rad = math.radians(angle)
            ex = int(cx + math.cos(rad) * max_r * 0.92)
            ey = int(cy + math.sin(rad) * max_r * 0.92)
            # 轴线 (主轴已有加粗线, 这里画箭头)
            p.setPen(QPen(self.axis_color, 2))
            a1 = math.radians(math.degrees(rad) + 150)
            a2 = math.radians(math.degrees(rad) - 150)
            p.drawLine(ex, ey, int(ex + math.cos(a1) * arrow_len), int(ey + math.sin(a1) * arrow_len))
            p.drawLine(ex, ey, int(ex + math.cos(a2) * arrow_len), int(ey + math.sin(a2) * arrow_len))
            # 标签
            p.setPen(QPen(QColor(100, 100, 110), 1))
            tx = int(cx + math.cos(rad) * max_r * 0.97)
            ty = int(cy + math.sin(rad) * max_r * 0.97)
            p.drawText(tx, ty, label)

    def _paint_stored_points(self, p: QPainter) -> None:
        for pt in self.stored_pix_list:
            x, y = int(self._gx(int(pt.x), int(pt.z))), int(self._gy(int(pt.x), int(pt.z)))
            s = self.pix_size
            path = QPainterPath(); path.addRoundedRect(x, y, s, s, 3, 3)
            p.fillPath(path, pt.pix_color)
            p.setPen(QPen(pt.pix_color, 1)); p.drawText(x + s, y, pt.label)

    def _paint_hovered(self, p: QPainter) -> None:
        if self.hovered_grid_pos is None: return
        gx, gz = self.hovered_grid_pos
        x, y = int(self._gx(gx, gz)), int(self._gy(gx, gz))
        p.fillRect(x, y, self.pix_size, self.pix_size, self.hovered_color)

    def _paint_center(self, p: QPainter) -> None:
        x, y = int(self._gx(0, 0)), int(self._gy(0, 0)); s = self.pix_size
        p.setPen(QPen(self.center_color, 2))
        p.drawRoundedRect(x, y, s, s, s // 2, s // 2)

    def _paint_selected(self, p: QPainter) -> None:
        if self.selected_point is None: return
        try:
            x, y = int(self._gx(int(self.selected_point.x), int(self.selected_point.z))), int(self._gy(int(self.selected_point.x), int(self.selected_point.z)))
            s = self.pix_size
            p.setPen(QPen(self.selected_border_color, 2))
            p.drawRoundedRect(x, y, s, s, 3, 3)
        except Exception: pass

    def resizeEvent(self, a0: QResizeEvent) -> None:
        self.center_x = self.rect().center().x(); self.center_y = self.rect().center().y()
        super().resizeEvent(a0)

    def mousePressEvent(self, a0: QMouseEvent) -> None:
        if a0.button() == Qt.MiddleButton:
            self._panning = True; self._pan_last = a0.pos()
            self.setCursor(Qt.ClosedHandCursor); return
        super().mousePressEvent(a0)

    def mouseMoveEvent(self, a0: QMouseEvent) -> None:
        if self._panning and self._pan_last is not None:
            delta = a0.pos() - self._pan_last
            self.offset_x += delta.x(); self.offset_y += delta.y()
            self._pan_last = a0.pos(); self.update(); return
        gx, gz = self._widget_to_grid(a0.pos().x(), a0.pos().y())
        self.hovered_grid_pos = (gx, gz); self.update()

    def mouseReleaseEvent(self, a0: QMouseEvent) -> None:
        if self._panning: self._panning = False; self._pan_last = None; self.setCursor(Qt.ArrowCursor); return
        gx, gz = self._widget_to_grid(a0.pos().x(), a0.pos().y())
        if a0.button() == Qt.RightButton: self._show_context_menu(a0.pos(), gx, gz); return
        if a0.button() == Qt.LeftButton: self._handle_left_click(gx, gz)

    def _handle_left_click(self, gx: int, gz: int) -> None:
        if (gx, gz) in self.stored_pix_fastsearch:
            for pt in self.stored_pix_list:
                if int(pt.x) == gx and int(pt.z) == gz:
                    self.selected_point = pt; self.selection_changed.emit(pt); self.update(); return
        else:
            from dyn.components.pos_select.pos_select_widgets import NewPointEditorDialog
            dlg = NewPointEditorDialog((gx, gz))
            if dlg.exec() == QDialog.DialogCode.Accepted:
                pt = MinecraftPosition(dlg.x, dlg.y, dlg.z, label=dlg.name, main_color=dlg.color)
                self.stored_pix_list.append(pt); self.stored_pix_fastsearch.add((int(pt.x), int(pt.z)))
                self._undo_stack.push(AddPointCommand(self.stored_pix_list, self.stored_pix_fastsearch, pt))
                self.point_renewed_sign.emit(self.stored_pix_list); self.update()

    def _show_context_menu(self, pos: QPoint, gx: int, gz: int) -> None:
        menu = QMenu(self)
        point_here = None
        for pt in self.stored_pix_list:
            if int(pt.x) == gx and int(pt.z) == gz: point_here = pt; break
        if point_here is not None:
            menu.addAction("编辑点...", lambda pt=point_here: self._edit_point(pt))
            menu.addAction("删除点", lambda pt=point_here: self._delete_point(pt))
            menu.addAction("复制坐标", lambda pt=point_here: self._copy_coords(pt))
            menu.addSeparator()
        menu.addAction("在此新建点", lambda: self._handle_left_click(gx, gz))
        menu.addAction("重置视图", self._reset_view)
        menu.exec(self.mapToGlobal(pos))

    def _edit_point(self, pt: MinecraftPosition) -> None:
        from dyn.components.pos_select.pos_select_widgets import NewPointEditorDialog
        dlg = NewPointEditorDialog((int(pt.x), int(pt.z)))
        dlg.ui.doubleSpinBox_X.setValue(pt.x); dlg.ui.doubleSpinBox_Z.setValue(pt.z); dlg.ui.doubleSpinBox_Y.setValue(pt.y)
        dlg.ui.lineEdit_Name.setText(pt.label)
        dlg.ui.spinBox_r.setValue(pt.pix_color.red()); dlg.ui.spinBox_g.setValue(pt.pix_color.green()); dlg.ui.spinBox_b.setValue(pt.pix_color.blue())
        if dlg.exec() == QDialog.DialogCode.Accepted:
            old_vals = {"x": pt.x, "y": pt.y, "z": pt.z, "label": pt.label, "color": pt.pix_color}
            pt.x = dlg.x; pt.y = dlg.y; pt.z = dlg.z; pt.label = dlg.name; pt._main_color = dlg.color
            new_vals = {"x": pt.x, "y": pt.y, "z": pt.z, "label": pt.label, "color": pt.pix_color}
            self._undo_stack.push(EditPointCommand(pt, old_vals, new_vals))
            self.point_renewed_sign.emit(self.stored_pix_list); self.selection_changed.emit(pt); self.update()

    def _delete_point(self, pt: MinecraftPosition) -> None:
        self._undo_stack.push(RemovePointCommand(self.stored_pix_list, self.stored_pix_fastsearch, pt))
        self.stored_pix_list.remove(pt); self.stored_pix_fastsearch.discard((int(pt.x), int(pt.z)))
        if self.selected_point is pt: self.selected_point = None
        self.point_renewed_sign.emit(self.stored_pix_list); self.update()

    def _copy_coords(self, pt: MinecraftPosition) -> None:
        from PySide6.QtWidgets import QApplication
        QApplication.clipboard().setText(f"{pt.x}, {pt.y}, {pt.z}")

    def _reset_view(self) -> None:
        self.offset_x = 0.0; self.offset_y = 0.0; self.set_proper_pix_size(); self.update()

    def wheelEvent(self, a0: QWheelEvent) -> None:
        old_size = self.pix_size; delta = a0.angleDelta().y()
        if delta > 0 and self.pix_size < 50: self.pix_size += 1
        elif delta < 0 and self.pix_size > 3: self.pix_size -= 1
        else: return
        if old_size != self.pix_size:
            ratio = self.pix_size / old_size
            cursor_x = a0.position().x() - self.center_x - self.offset_x
            cursor_y = a0.position().y() - self.center_y - self.offset_y
            self.offset_x -= cursor_x * (ratio - 1); self.offset_y -= cursor_y * (ratio - 1)
        self.update()

    def get_list_selected_pix(self, selected_point: MinecraftPosition) -> None:
        self.selected_point = selected_point; self.update()
