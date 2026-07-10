# pylint: disable=all
# flake8: noqa
# mypy: ignore-errors
# global_storage.py
import logging
from pathlib import Path
from . import global_storage

log = logging.getLogger("dyn.lib.global_storage")

# A global variable to hold the namespace, accessible by export_mcfunction
global_storage.namespace = 'fireworks1'

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


def reset_storage():
    """清空全局命令存储."""
    global commands_by_tick, MAX_TICK
    count = sum(len(v) for v in commands_by_tick.values())
    log.debug(f"清空命令存储: {count} 条命令, MAX_TICK={MAX_TICK}")
    commands_by_tick = {}
    MAX_TICK = 0
