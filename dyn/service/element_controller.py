"""元素控制器 — 管理所有时间线元素的 CRUD 和属性同步."""

from __future__ import annotations

import logging

from PySide6.QtCore import QObject, Signal

from dyn.logging_config import get_logger

log = get_logger(__name__)

from dyn.models.elements import (
    Element,
    TrajectoryElement,
    FireworkElement,
    TrajFireworkElement,
    Position,
    ColorRGB,
    ElementType,
)


class ElementController(QObject):
    """中央元素管理服务."""

    element_added = Signal(Element)
    element_removed = Signal(str)
    element_changed = Signal(str, str, object)
    selection_changed = Signal(str)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._elements: dict[str, Element] = {}
        self._selected_id: str = ""

    # ── 查询 ──────────────────────────────────────────

    @property
    def selected_element(self) -> Element | None:
        return self._elements.get(self._selected_id)

    @property
    def selected_id(self) -> str:
        return self._selected_id

    @property
    def all_elements(self) -> list[Element]:
        return sorted(self._elements.values(), key=lambda e: e.start_tick)

    @property
    def trajectory_count(self) -> int:
        return sum(1 for e in self._elements.values() if e.element_type == ElementType.TRAJECTORY)

    @property
    def firework_count(self) -> int:
        return sum(1 for e in self._elements.values() if e.element_type == ElementType.FIREWORK)

    @property
    def traj_firework_count(self) -> int:
        return sum(1 for e in self._elements.values() if e.element_type == ElementType.TRAJ_FIREWORK)

    def get_element(self, element_id: str) -> Element | None:
        return self._elements.get(element_id)

    # ── 选择 ──────────────────────────────────────────

    def select_element(self, element_id: str) -> None:
        self._selected_id = element_id
        self.selection_changed.emit(element_id)

    def clear_selection(self) -> None:
        self._selected_id = ""
        self.selection_changed.emit("")

    # ── 创建 / 添加 ──────────────────────────────────

    def add_element(self, elem: Element) -> None:
        if elem.id in self._elements:
            log.warning(f"覆盖已存在元素: id={elem.id}, name={elem.name}")
        self._elements[elem.id] = elem
        log.debug(f"添加元素: {elem.element_type.name} id={elem.id} name={elem.name}")
        self.element_added.emit(elem)

    def create_trajectory(self, name: str = "New Trajectory", start_tick: int = 0) -> TrajectoryElement:
        elem = TrajectoryElement(name=name, start_tick=start_tick)
        self.add_element(elem)
        return elem

    def create_firework(self, name: str = "New Firework", start_tick: int = 20) -> FireworkElement:
        elem = FireworkElement(name=name, start_tick=start_tick)
        self.add_element(elem)
        return elem

    def create_traj_firework(self, name: str = "New Traj-Firework", start_tick: int = 0) -> TrajFireworkElement:
        elem = TrajFireworkElement(name=name, start_tick=start_tick)
        self.add_element(elem)
        return elem

    # ── 删除 ──────────────────────────────────────────

    def remove_element(self, element_id: str) -> Element | None:
        removed = self._elements.pop(element_id, None)
        if removed is None:
            log.warning(f"删除失败: 元素不存在 id={element_id}")
            return None
        log.debug(f"删除元素: {removed.element_type.name} id={element_id} name={removed.name}")
        if self._selected_id == element_id:
            self._selected_id = ""
            self.selection_changed.emit("")
        self.element_removed.emit(element_id)
        return removed

    def remove_selected(self) -> Element | None:
        if not self._selected_id:
            return None
        return self.remove_element(self._selected_id)

    # ── 属性修改 ──────────────────────────────────────

    def set_property(self, element_id: str, key: str, value: object) -> bool:
        elem = self._elements.get(element_id)
        if elem is None or not hasattr(elem, key):
            return False
        setattr(elem, key, value)
        self.element_changed.emit(element_id, key, value)
        return True

    # ── 克隆 ──────────────────────────────────────────

    def clone_element(self, element_id: str) -> Element | None:
        import copy
        from uuid import uuid4
        elem = self._elements.get(element_id)
        if elem is None:
            return None
        cloned = copy.deepcopy(elem)
        cloned.id = str(uuid4())
        cloned.name = f"{elem.name} (副本)"
        self.add_element(cloned)
        return cloned

    # ── 项目同步 ──────────────────────────────────────

    def load_from_project(self, project) -> None:
        self._elements.clear()
        self._selected_id = ""
        for e in project.trajectories:
            self._elements[e.id] = e
        for e in project.fireworks:
            self._elements[e.id] = e
        for e in getattr(project, 'traj_fireworks', []):
            self._elements[e.id] = e

    def to_project(self, project) -> None:
        project.trajectories = [e for e in self._elements.values() if e.element_type == ElementType.TRAJECTORY]
        project.fireworks = [e for e in self._elements.values() if e.element_type == ElementType.FIREWORK]
        tf_list = [e for e in self._elements.values() if e.element_type == ElementType.TRAJ_FIREWORK]
        if hasattr(project, 'traj_fireworks'):
            project.traj_fireworks = tf_list
