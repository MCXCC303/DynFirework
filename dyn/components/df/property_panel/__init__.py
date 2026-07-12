"""DynFireworkMod v2.0 属性表单 秒单位."""
from __future__ import annotations

from dyn.logging_config import get_logger
from .composites.composite_base import CompositeBase
from .effects.effect_base import EffectBase
from .fw.fw_base import FwBase
from .traj.traj_base import TrajBase

# 注册表: type_key -> form_class
log = get_logger(__name__)

FORM_REGISTRY: dict[str, type] = {}

def _init_form_registry() -> None:
	# 初始化表单
	if FORM_REGISTRY:
		log.debug("表单注册表已初始化, 跳过")
		return
	from .fw.fw_single_layer import SingleLayerForm
	from .fw.fw_double_layer import DoubleLayerForm
	from .fw.fw_directional import DirectionalForm
	from .fw.fw_clustered import ClusteredForm
	from .fw.fw_expanding import ExpandingForm
	from .fw.fw_nebula import NebulaForm
	from .traj.traj_launch import LaunchForm
	from .traj.traj_launch_spark import LaunchSparkForm
	from .traj.traj_expanding import ExpandingForm as TrajExpandingForm
	from .traj.traj_spiral import SpiralForm
	from .effects.effect_beam import BeamForm
	from .effects.effect_spray import SprayForm
	from .effects.effect_double_helix import DoubleHelixForm
	from .effects.effect_rotating_ring import RotatingRingForm
	from .composites.parent.se import ParentSEForm
	from .composites.parent.ce import ParentCEForm
	from .composites.sub.primary import SubPrimaryForm
	from .composites.sub.secondary import SubSecondaryForm
	from .composites.sub.cluster import SubClusterForm
	from .composites.sub.expanding import SubExpandingForm

	FORM_REGISTRY.update({
		"single_layer": SingleLayerForm,
		"double_layer": DoubleLayerForm,
		"directional": DirectionalForm,
		"clustered": ClusteredForm,
		"expanding_sphere": ExpandingForm,
		"nebula": NebulaForm,
		"launch": LaunchForm,
		"launch_spark": LaunchSparkForm,
		"expanding": TrajExpandingForm,
		"spiral": SpiralForm,
		"beam": BeamForm,
		"spray": SprayForm,
		"double_helix": DoubleHelixForm,
		"rotating_ring": RotatingRingForm,
		"secondary_explosion": ParentSEForm,
		"combo_ec": ParentCEForm,
		"_comp_primary": SubPrimaryForm,
		"_comp_secondary": SubSecondaryForm,
		"_comp_clustered": SubClusterForm,
		"_comp_expanding": SubExpandingForm,
	})

def get_form(type_key: str):
	"""懒加载获取表单实例."""
	_init_form_registry()
	cls = FORM_REGISTRY.get(type_key)
	if cls is None:
		log.warning(f"未找到表单: type_key={type_key}")
		return None
	return cls()

__all__ = ["FwBase", "TrajBase", "EffectBase", "CompositeBase", "FORM_REGISTRY", "get_form"]
