# global_storage.py
from pathlib import Path

commands_by_tick = {}
MAX_TICK = 0
g = 9.8

# 默认角度步长
horizontal_angle_step_default = 30
vertical_angle_step_default = 30

project_dir = str(Path(__file__).parent.parent.parent)


def update_max_tick(tick):
    global MAX_TICK
    if tick > MAX_TICK:
        MAX_TICK = tick


def add_command(tick, command):
    update_max_tick(tick)
    if tick not in commands_by_tick:
        commands_by_tick[tick] = []
    commands_by_tick[tick].append(command)
