"""数据模型序列化往返测试."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dyn.models.elements import (
    Element, ElementType,
    TrajectoryElement, FireworkElement,
    ColorRGB, GradientColor, Position,
)
from dyn.models.timeline import Project


class TestColorRGB:
    def test_default(self):
        c = ColorRGB()
        assert c.r == 255
        assert c.g == 165
        assert c.b == 0

    def test_to_json_roundtrip(self):
        c = ColorRGB(r=100, g=200, b=50)
        data = c.to_json()
        c2 = ColorRGB.from_json(data)
        assert c2.r == 100
        assert c2.g == 200
        assert c2.b == 50

    def test_as_tuple(self):
        c = ColorRGB(r=10, g=20, b=30)
        assert c.as_tuple() == (10, 20, 30)


class TestPosition:
    def test_default(self):
        p = Position()
        assert p.x == 0.0
        assert p.y == 64.0

    def test_to_json_roundtrip(self):
        p = Position(x=10.5, y=70.0, z=-5.2)
        data = p.to_json()
        p2 = Position.from_json(data)
        assert p2.x == 10.5
        assert p2.y == 70.0
        assert p2.z == -5.2


class TestGradientColor:
    def test_default_no_gradient(self):
        gc = GradientColor()
        assert gc.use_gradient is False

    def test_to_json_roundtrip(self):
        gc = GradientColor(
            start=ColorRGB(r=255, g=0, b=0),
            end=ColorRGB(r=0, g=0, b=255),
            use_gradient=True,
        )
        data = gc.to_json()
        gc2 = GradientColor.from_json(data)
        assert gc2.use_gradient is True
        assert gc2.start.r == 255
        assert gc2.end.b == 255


class TestTrajectoryElement:
    def test_default_creation(self):
        t = TrajectoryElement(name="Test")
        assert t.name == "Test"
        assert t.element_type == ElementType.TRAJECTORY
        assert t.start_tick == 0
        assert t.duration_ticks == 20
        assert t.end_tick == 20

    def test_to_json_roundtrip(self):
        t = TrajectoryElement(
            name="Launch 1", start_tick=10, duration_ticks=40,
            traj_type="spark", k=1.5, m0=0.8,
        )
        data = t.to_json()
        t2 = TrajectoryElement.from_json(data)
        assert t2.name == "Launch 1"
        assert t2.start_tick == 10
        assert t2.duration_ticks == 40
        assert t2.traj_type == "spark"
        assert t2.k == 1.5
        assert t2.m0 == 0.8

    def test_unique_id(self):
        t1 = TrajectoryElement()
        t2 = TrajectoryElement()
        assert t1.id != t2.id

    def test_end_tick(self):
        t = TrajectoryElement(start_tick=100, duration_ticks=50)
        assert t.end_tick == 150


class TestFireworkElement:
    def test_default_creation(self):
        f = FireworkElement(name="FW")
        assert f.name == "FW"
        assert f.element_type == ElementType.FIREWORK
        assert f.fw_type == "single_layer"

    def test_to_json_roundtrip(self):
        f = FireworkElement(
            name="Double Firework", start_tick=60, duration_ticks=30,
            fw_type="double_layer", speed=15.0, horizontal_angle=45,
        )
        data = f.to_json()
        f2 = FireworkElement.from_json(data)
        assert f2.name == "Double Firework"
        assert f2.fw_type == "double_layer"
        assert f2.speed == 15.0
        assert f2.horizontal_angle == 45


class TestProject:
    def test_empty_project(self):
        p = Project()
        assert p.name == "Untitled"
        assert len(p.all_elements) == 0
        assert p.total_duration_ticks == 0

    def test_add_elements(self):
        p = Project()
        p.add_trajectory(TrajectoryElement(name="T1", start_tick=0, duration_ticks=40))
        p.add_firework(FireworkElement(name="F1", start_tick=40, duration_ticks=20))
        assert len(p.all_elements) == 2
        assert p.total_duration_ticks == 60

    def test_get_element(self):
        p = Project()
        t = TrajectoryElement(name="T1")
        p.add_trajectory(t)
        found = p.get_element(t.id)
        assert found is not None
        assert found.name == "T1"
        assert p.get_element("nonexistent") is None

    def test_remove_element(self):
        p = Project()
        t = TrajectoryElement()
        p.add_trajectory(t)
        p.remove_element(t.id)
        assert len(p.all_elements) == 0

    def test_full_json_roundtrip(self):
        p = Project(name="TestShow", bpm=140, music_path="/tmp/test.mp3")
        t = TrajectoryElement(name="T1", start_tick=0, duration_ticks=100)
        f = FireworkElement(name="F1", start_tick=100, duration_ticks=30)
        p.add_trajectory(t)
        p.add_firework(f)

        js_str = p.to_json_string()
        data = json.loads(js_str)
        p2 = Project.from_json(data)

        assert p2.name == "TestShow"
        assert p2.bpm == 140
        assert p2.music_path == "/tmp/test.mp3"
        assert len(p2.trajectories) == 1
        assert len(p2.fireworks) == 1
        assert p2.trajectories[0].name == "T1"
        assert p2.fireworks[0].name == "F1"
        assert p2.total_duration_ticks == 130

    def test_file_roundtrip(self, tmp_path):
        p = Project(name="FileTest")
        p.add_trajectory(TrajectoryElement(name="T1"))
        p.add_firework(FireworkElement(name="F1"))
        test_file = tmp_path / "test.dyn"
        p.to_file(test_file)
        p2 = Project.from_file(test_file)
        assert p2.name == "FileTest"
        assert len(p2.all_elements) == 2
