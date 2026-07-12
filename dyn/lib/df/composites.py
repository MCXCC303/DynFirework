"""DynFireworkMod v2.0 复合元素计算 - secondary_explosion / combo_ec.
每个函数从 CompositeElement 提取参数，调用 commands 生成 /df 命令，写入 global_storage.
"""
from __future__ import annotations

import logging

from dyn.lib import global_storage
from dyn.lib.df.commands import (
	cmd_secondary_explosion_type1, cmd_secondary_explosion_type2, cmd_combo_ec,
)
from dyn.lib.units import seconds_to_tick

log = logging.getLogger("dyn.lib.df.composites")

def secondary_explosion(elem) -> None:
	"""二次爆炸 - /df secondaryexplosion.
	主烟花固定为 singlelayer，二次爆炸类型由 elem.se_secondary_type 决定.
	"""
	try:
		tick = seconds_to_tick(elem.start_time)
		pos = elem.se_mid_position
		s_type = elem.se_secondary_type

		if s_type == "expanding":
			cmd = cmd_secondary_explosion_type1(
				x=pos.x, y=pos.y, z=pos.z,
				r1=elem.se_primary_color.start.r, g1=elem.se_primary_color.start.g, b1=elem.se_primary_color.start.b,
				r2=elem.se_primary_color.end.r, g2=elem.se_primary_color.end.g, b2=elem.se_primary_color.end.b,
				speed=elem.se_primary_speed, particle_count=elem.se_primary_count,
				duration=elem.se_primary_duration, lifetime=elem.se_primary_lifetime,
				flicker=elem.se_enable_tail_flicker,
				s_radius=elem.se_secondary_radius, s_count=elem.se_secondary_count,
				s_radial_speed=elem.se_secondary_radial_speed, s_lifetime=elem.se_secondary_lifetime,
			)
		elif s_type == "singlelayer":
			cmd = cmd_secondary_explosion_type2(
				x=pos.x, y=pos.y, z=pos.z,
				r1=elem.se_primary_color.start.r, g1=elem.se_primary_color.start.g, b1=elem.se_primary_color.start.b,
				r2=elem.se_primary_color.end.r, g2=elem.se_primary_color.end.g, b2=elem.se_primary_color.end.b,
				speed=elem.se_primary_speed, particle_count=elem.se_primary_count,
				duration=elem.se_primary_duration, lifetime=elem.se_primary_lifetime,
				flicker=elem.se_enable_tail_flicker,
				s_r1=elem.se_secondary_color.start.r, s_g1=elem.se_secondary_color.start.g, s_b1=elem.se_secondary_color.start.b,
				s_r2=elem.se_secondary_color.end.r, s_g2=elem.se_secondary_color.end.g, s_b2=elem.se_secondary_color.end.b,
				s_speed=elem.se_secondary_speed, s_count=elem.se_secondary_count,
				s_duration=elem.se_secondary_duration, s_lifetime=elem.se_secondary_lifetime,
			)
		else:
			log.warning(f"未知 secondary_type: {s_type}")
			return

		global_storage.add_command(tick, cmd)
		log.debug(f"secondary_explosion: elem={elem.id}({elem.name}), tick={tick}, type={s_type}")
	except AttributeError as e:
		log.error(f"secondary_explosion 缺少属性: {e}")

def combo_ec(elem) -> None:
	"""同步烟花 - /df combo_ec."""
	try:
		tick = seconds_to_tick(elem.start_time)
		pos = elem.ce_position
		cmd = cmd_combo_ec(
			x=pos.x, y=pos.y, z=pos.z,
			cr1=elem.ce_cluster_color.start.r, cg1=elem.ce_cluster_color.start.g, cb1=elem.ce_cluster_color.start.b,
			cr2=elem.ce_cluster_color.end.r, cg2=elem.ce_cluster_color.end.g, cb2=elem.ce_cluster_color.end.b,
			c_speed=elem.ce_cluster_speed, dir_count=elem.ce_dir_count,
			track_count=elem.ce_track_count, spread=elem.ce_spread,
			c_duration=elem.ce_duration, c_lifetime=elem.ce_lifetime,
			sr1=elem.ce_sphere_color.start.r, sg1=elem.ce_sphere_color.start.g, sb1=elem.ce_sphere_color.start.b,
			sr2=elem.ce_sphere_color.end.r, sg2=elem.ce_sphere_color.end.g, sb2=elem.ce_sphere_color.end.b,
			s_count=elem.ce_sphere_count, flicker=elem.ce_flicker,
		)
		global_storage.add_command(tick, cmd)
		log.debug(f"combo_ec: elem={elem.id}({elem.name}), tick={tick}, dir_count={elem.ce_dir_count}, track_count={elem.ce_track_count}")
	except AttributeError as e:
		log.error(f"combo_ec 缺少属性: {e}")
