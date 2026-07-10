"""服务层单元测试."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from PySide6.QtCore import QObject


class TestElementController:
    def test_create_trajectory(self):
        from dyn.service.element_controller import ElementController
        ec = ElementController()
        t = ec.create_trajectory("T1", start_tick=0)
        assert t.name == "T1"
        assert t.start_tick == 0
        assert ec.trajectory_count == 1

    def test_create_firework(self):
        from dyn.service.element_controller import ElementController
        ec = ElementController()
        f = ec.create_firework("F1", start_tick=20)
        assert f.name == "F1"
        assert f.start_tick == 20
        assert ec.firework_count == 1

    def test_select_element(self):
        from dyn.service.element_controller import ElementController
        ec = ElementController()
        t = ec.create_trajectory("T1")
        ec.select_element(t.id)
        assert ec.selected_id == t.id
        assert ec.selected_element.name == "T1"

    def test_clear_selection(self):
        from dyn.service.element_controller import ElementController
        ec = ElementController()
        t = ec.create_trajectory("T1")
        ec.select_element(t.id)
        ec.clear_selection()
        assert ec.selected_id == ""
        assert ec.selected_element is None

    def test_remove_element(self):
        from dyn.service.element_controller import ElementController
        ec = ElementController()
        t = ec.create_trajectory("T1")
        ec.remove_element(t.id)
        assert ec.trajectory_count == 0
        assert ec.get_element(t.id) is None

    def test_set_property(self):
        from dyn.service.element_controller import ElementController
        ec = ElementController()
        t = ec.create_trajectory("T1")
        ec.set_property(t.id, "start_tick", 100)
        assert t.start_tick == 100

    def test_clone_element(self):
        from dyn.service.element_controller import ElementController
        ec = ElementController()
        t = ec.create_trajectory("Original")
        cloned = ec.clone_element(t.id)
        assert cloned is not None
        assert cloned.id != t.id
        assert "(副本)" in cloned.name

    def test_all_elements_sorted(self):
        from dyn.service.element_controller import ElementController
        ec = ElementController()
        t1 = ec.create_trajectory("T2", start_tick=50)
        t2 = ec.create_trajectory("T1", start_tick=0)
        f1 = ec.create_firework("F1", start_tick=25)
        sorted_elems = ec.all_elements
        assert sorted_elems[0].start_tick == 0
        assert sorted_elems[-1].start_tick == 50

    def test_signal_emission(self):
        from dyn.service.element_controller import ElementController
        ec = ElementController()
        added = []
        ec.element_added.connect(lambda e: added.append(e))
        ec.create_trajectory("T1")
        assert len(added) == 1
        assert added[0].name == "T1"


class TestProjectManager:
    def test_new_project(self):
        from dyn.service.project_manager import ProjectManager
        pm = ProjectManager()
        proj = pm.new_project()
        assert proj.name == "Untitled"
        assert not pm.is_modified
        assert not pm.has_file

    def test_mark_modified(self):
        from dyn.service.project_manager import ProjectManager
        pm = ProjectManager()
        pm.new_project()
        pm.mark_modified()
        assert pm.is_modified
