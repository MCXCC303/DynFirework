"""核心计算库测试."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestGlobalStorage:
    def test_add_command(self):
        from dyn.lib import global_storage
        global_storage.commands_by_tick.clear()
        global_storage.MAX_TICK = 0

        global_storage.add_command(10, "dfp 1 2 3 255 0 0 255 255 255 0 0 0 15")
        assert 10 in global_storage.commands_by_tick
        assert len(global_storage.commands_by_tick[10]) == 1
        assert global_storage.MAX_TICK == 10

    def test_multiple_commands_same_tick(self):
        from dyn.lib import global_storage
        global_storage.commands_by_tick.clear()
        global_storage.MAX_TICK = 0

        global_storage.add_command(5, "cmd1")
        global_storage.add_command(5, "cmd2")
        assert len(global_storage.commands_by_tick[5]) == 2


class TestSharedFunctions:
    def test_color_expression(self):
        from dyn.lib.shared_functions import color_expression
        result = color_expression((255, 0, 0), (0, 0, 255), 20)
        assert len(result) == 2
        assert result[0] == [1.0, 0.0, 0.0]
        assert result[1] == [0.0, 0.0, 1.0]

    def test_add_firework_command(self):
        from dyn.lib import shared_functions, global_storage
        global_storage.commands_by_tick.clear()

        shared_functions.add_firework_command(
            0, 10.0, 64.0, 10.0, 20,
            ([1.0, 0.0, 0.0], [0.0, 0.0, 1.0]),
            0, 0, 0,
        )
        assert 0 in global_storage.commands_by_tick
        cmd = global_storage.commands_by_tick[0][0]
        assert cmd.startswith("dfp")
        assert "10.0" in cmd

    def test_add_spark_command(self):
        from dyn.lib import shared_functions, global_storage
        global_storage.commands_by_tick.clear()

        shared_functions.add_spark_command(0, 0, 64, 0, 0.5, 2.0, 0.5, 10)
        assert 0 in global_storage.commands_by_tick


class TestFireworks:
    def test_basic_single_layer(self):
        from dyn.lib import fireworks as fw
        from dyn.lib import global_storage
        global_storage.commands_by_tick.clear()

        fw.basic_single_layer_firework(
            tick=0, x=0, y=80, z=0,
            start_color=(255, 0, 0), end_color=(255, 255, 0),
            speed=10, horizontal_angle_step=90, vertical_angle_step=90,
            duration=1.0, lifetime=1.0,
        )
        assert len(global_storage.commands_by_tick) > 0

    def test_calculate_inner_angle_steps(self):
        from dyn.lib.fireworks import calculate_inner_angle_steps
        h, v = calculate_inner_angle_steps(30, 30, 8, 10)
        assert h > 30  # 内层速度小，步长应更大（密度匹配）
        assert v > 30

    def test_basic_double_layer(self):
        from dyn.lib import fireworks as fw
        from dyn.lib import global_storage
        global_storage.commands_by_tick.clear()

        fw.basic_double_layer_firework(
            tick=0, x=0, y=80, z=0,
            inner_start_color=(0, 0, 255), inner_end_color=(100, 100, 255),
            outer_start_color=(255, 0, 0), outer_end_color=(255, 100, 100),
            inner_speed=8, outer_speed=12,
            outer_horizontal_angle_step=30, outer_vertical_angle_step=30,
            duration=1.0, lifetime=1.0,
        )
        assert len(global_storage.commands_by_tick) > 0

    def test_expanding_sphere(self):
        from dyn.lib import fireworks as fw
        from dyn.lib import global_storage
        global_storage.commands_by_tick.clear()

        fw.expanding_sphere_firework(
            tick=0, x=0, y=80, z=0,
            start_color=(0, 255, 0), end_color=(0, 255, 255),
            radius=5, particle_count=50, radial_speed=3, lifetime=2.0,
        )
        assert len(global_storage.commands_by_tick) > 0
