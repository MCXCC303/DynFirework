"""DynFireworkMod v2.0 完整实现 - /df 命令格式化 + 物理计算.
每个元素类型对应一个计算函数，生成一条高层 /df 命令写入 global_storage.
"""
from .commands import (
	cmd_single_layer,
	cmd_double_layer,
	cmd_directional,
	cmd_clustered,
	cmd_expanding,
	cmd_nebula,
	cmd_launch,
	cmd_launch_spark,
	cmd_expanding_traj,
	cmd_spiral,
	cmd_beam,
	cmd_spray,
	cmd_double_helix,
	cmd_rotating_ring,
	cmd_secondary_explosion,
	cmd_combo_ec,
	cmd_spark,
	cmd_shell,
)
from .composites import (
	secondary_explosion,
	combo_ec,
)
from .effects import (
	beam_effect,
	spray_effect,
	double_helix_effect,
	rotating_ring_effect,
)
from .fireworks import (
	single_layer_firework,
	double_layer_firework,
	directional_firework_v2,
	clustered_firework_v2,
	expanding_sphere_firework_v2,
	nebula_firework,
)
from .trajectories import (
	launch_trajectory_v2,
	launch_spark_trajectory_v2,
	expanding_trajectory_v2,
	spiral_trajectory_v2,
)
