"""ParticleEx / Colorblock Mod (/particleex) - MC 1.12.2/1.16.5.

commands.py           /particleex 命令格式化
fireworks.py          逐 tick 烟花物理
trajectories.py       逐 tick 轨迹物理
special_effects.py    逐 tick 特殊效果
shared_functions.py   后端调度器
backend_registry.py   MC 版本映射
"""
from . import backend_registry
from . import commands
from . import fireworks
from . import shared_functions
from . import special_effects
from . import trajectories
