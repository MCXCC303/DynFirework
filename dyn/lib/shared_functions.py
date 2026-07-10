# pylint: disable=all
# flake8: noqa
# mypy: ignore-errors
# shared_functions.py — 动态后端调度器
#
# 所有命令生成函数通过此模块路由到当前活动的后端。
# 切换后端: backend_registry.set_backend(BackendType.DFP) 或 set_backend(BackendType.PARTICLEEX)
#
# 此模块保持与原有调用方100%兼容的接口 — fireworks.py / trajectories.py /
# special_effects.py 无需任何修改。
import logging
from . import global_storage
from .backend_registry import get_backend, BackendType
from .backends import dfp_backend, particleex_backend

log = logging.getLogger("dyn.lib.shared_functions")


def _get_backend_module():
    """返回当前活动后端的模块对象."""
    backend = get_backend()
    if backend == BackendType.DFP:
        return dfp_backend
    elif backend == BackendType.PARTICLEEX:
        return particleex_backend
    else:
        log.error(f"未知后端类型: {backend}")
        raise ValueError(f"Unknown backend: {backend}")


def color_expression(start_color, end_color, lifetime):
    return _get_backend_module().color_expression(start_color, end_color, lifetime)


def add_firework_command(tick, x, y, z, lifetime, color_expr, vx=0, vy=0, vz=0):
    return _get_backend_module().add_firework_command(tick, x, y, z, lifetime, color_expr, vx, vy, vz)


def add_spark_command(tick, x, y, z, vx, vy, vz, lifetime):
    return _get_backend_module().add_spark_command(tick, x, y, z, vx, vy, vz, lifetime)


def add_thick_spark_command(tick, x, y, z, vx, vy, vz, lifetime, range_x, range_y, range_z, particle_count):
    return _get_backend_module().add_thick_spark_command(tick, x, y, z, vx, vy, vz, lifetime, range_x, range_y, range_z, particle_count)


def add_velocity_firework_command(tick, x, y, z, start_color, end_color, vx, vy, vz, lifetime):
    return _get_backend_module().add_velocity_firework_command(tick, x, y, z, start_color, end_color, vx, vy, vz, lifetime)


def lerp_color(color1, color2, factor):
    return _get_backend_module().lerp_color(color1, color2, factor)
