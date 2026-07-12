"""CompositeElement - 复合元素 secondary_explosion / combo_ec."""
from __future__ import annotations

from dataclasses import dataclass, field

from dyn.logging_config import get_logger
from .base import Element, ElementCategory

log = get_logger(__name__)
from .values import GradientColor, Position, CompositeType, FireworkType

@dataclass
class CompositeElement(Element):
	composite_type: CompositeType = CompositeType.SECONDARY_EXPLOSION
	position: Position = field(default_factory=Position)

	# 二次爆炸 (se_ = secondary explosion)
	se_start_position: Position = field(default_factory=Position)
	se_mid_position: Position = field(default_factory=lambda: Position(y=80))

	se_primary_type: FireworkType = FireworkType.SINGLE_LAYER
	se_primary_color: GradientColor = field(default_factory=GradientColor)
	se_primary_speed: float = 10.0
	se_primary_count: int = 100
	se_primary_duration: float = 2.0
	se_primary_lifetime: float = 2.0
	se_primary_track_count: int = 5
	se_primary_spread: float = 15.0
	se_primary_h_angle: float = 30.0
	se_primary_v_angle: float = 30.0
	se_primary_radius: float = 3.0
	se_primary_radial_speed: float = 2.0
	se_primary_density_falloff: float = 2.0

	se_secondary_type: str = "expanding"
	se_secondary_color: GradientColor = field(default_factory=GradientColor)
	se_secondary_radius: float = 3.0
	se_secondary_count: int = 50
	se_secondary_radial_speed: float = 2.0
	se_secondary_lifetime: float = 1.5
	se_secondary_speed: float = 8.0
	se_secondary_duration: float = 1.5

	# 同步烟花 (ce_ = combo expanding-clustered)
	ce_position: Position = field(default_factory=Position)
	ce_cluster_color: GradientColor = field(default_factory=GradientColor)
	ce_cluster_speed: float = 10.0
	ce_dir_count: int = 12
	ce_track_count: int = 5
	ce_spread: float = 15.0
	ce_duration: float = 2.0
	ce_lifetime: float = 2.0
	ce_sphere_color: GradientColor = field(default_factory=GradientColor)
	ce_sphere_count: int = 100
	ce_sphere_radius: float = 3.0
	ce_sphere_radial_speed: float = 2.0
	ce_flicker: bool = False

	@property
	def category(self) -> ElementCategory:
		return ElementCategory.COMPOSITE

	def to_json(self) -> dict:
		base = super().to_json()
		base.update({
			"type": self.composite_type.value,
			"position": self.position.to_json(),
			# Secondary explosion
			"se_start_position": self.se_start_position.to_json(),
			"se_mid_position": self.se_mid_position.to_json(),
			"se_primary_type": self.se_primary_type.value,
			"se_primary_color": self.se_primary_color.to_json(),
			"se_primary_speed": self.se_primary_speed,
			"se_primary_count": self.se_primary_count,
			"se_primary_duration": self.se_primary_duration,
			"se_primary_lifetime": self.se_primary_lifetime,
			"se_primary_track_count": self.se_primary_track_count,
			"se_primary_spread": self.se_primary_spread,
			"se_primary_h_angle": self.se_primary_h_angle,
			"se_primary_v_angle": self.se_primary_v_angle,
			"se_primary_radius": self.se_primary_radius,
			"se_primary_radial_speed": self.se_primary_radial_speed,
			"se_primary_density_falloff": self.se_primary_density_falloff,
			"se_secondary_type": self.se_secondary_type,
			"se_secondary_color": self.se_secondary_color.to_json(),
			"se_secondary_radius": self.se_secondary_radius,
			"se_secondary_count": self.se_secondary_count,
			"se_secondary_radial_speed": self.se_secondary_radial_speed,
			"se_secondary_lifetime": self.se_secondary_lifetime,
			"se_secondary_speed": self.se_secondary_speed,
			"se_secondary_duration": self.se_secondary_duration,
			# Combo EC
			"ce_position": self.ce_position.to_json(),
			"ce_cluster_color": self.ce_cluster_color.to_json(),
			"ce_cluster_speed": self.ce_cluster_speed,
			"ce_dir_count": self.ce_dir_count,
			"ce_track_count": self.ce_track_count,
			"ce_spread": self.ce_spread,
			"ce_duration": self.ce_duration,
			"ce_lifetime": self.ce_lifetime,
			"ce_sphere_color": self.ce_sphere_color.to_json(),
			"ce_sphere_count": self.ce_sphere_count,
			"ce_sphere_radius": self.ce_sphere_radius,
			"ce_sphere_radial_speed": self.ce_sphere_radial_speed,
			"ce_flicker": self.ce_flicker,
		})
		return base

	@classmethod
	def from_json(cls, data: dict) -> CompositeElement:
		base = cls._from_json_base(data)

		try:
			composite_type = CompositeType(data.get("type", "secondary_explosion"))
		except ValueError:
			log.warning(f"未知 CompositeType: {data.get('type')}，使用默认 SECONDARY_EXPLOSION")
			composite_type = CompositeType.SECONDARY_EXPLOSION

		try:
			se_primary_type = FireworkType(data.get("se_primary_type", "single_layer"))
		except ValueError:
			log.warning(f"未知 FireworkType: {data.get('se_primary_type')}，使用默认 SINGLE_LAYER")
			se_primary_type = FireworkType.SINGLE_LAYER

		return cls(
			**base,
			composite_type=composite_type,
			position=Position.from_json(data.get("position", {})),
			# Secondary explosion
			se_start_position=Position.from_json(data.get("se_start_position", {})),
			se_mid_position=Position.from_json(data.get("se_mid_position", {})),
			se_primary_type=se_primary_type,
			se_primary_color=GradientColor.from_json(data.get("se_primary_color", {})),
			se_primary_speed=data.get("se_primary_speed", 10.0),
			se_primary_count=data.get("se_primary_count", 100),
			se_primary_duration=data.get("se_primary_duration", 2.0),
			se_primary_lifetime=data.get("se_primary_lifetime", 2.0),
			se_primary_track_count=data.get("se_primary_track_count", 5),
			se_primary_spread=data.get("se_primary_spread", 15.0),
			se_primary_h_angle=data.get("se_primary_h_angle", 30.0),
			se_primary_v_angle=data.get("se_primary_v_angle", 30.0),
			se_primary_radius=data.get("se_primary_radius", 3.0),
			se_primary_radial_speed=data.get("se_primary_radial_speed", 2.0),
			se_primary_density_falloff=data.get("se_primary_density_falloff", 2.0),
			se_secondary_type=data.get("se_secondary_type", "expanding"),
			se_secondary_color=GradientColor.from_json(data.get("se_secondary_color", {})),
			se_secondary_radius=data.get("se_secondary_radius", 3.0),
			se_secondary_count=data.get("se_secondary_count", 50),
			se_secondary_radial_speed=data.get("se_secondary_radial_speed", 2.0),
			se_secondary_lifetime=data.get("se_secondary_lifetime", 1.5),
			se_secondary_speed=data.get("se_secondary_speed", 8.0),
			se_secondary_duration=data.get("se_secondary_duration", 1.5),
			# Combo EC
			ce_position=Position.from_json(data.get("ce_position", {})),
			ce_cluster_color=GradientColor.from_json(data.get("ce_cluster_color", {})),
			ce_cluster_speed=data.get("ce_cluster_speed", 10.0),
			ce_dir_count=data.get("ce_dir_count", 12),
			ce_track_count=data.get("ce_track_count", 5),
			ce_spread=data.get("ce_spread", 15.0),
			ce_duration=data.get("ce_duration", 2.0),
			ce_lifetime=data.get("ce_lifetime", 2.0),
			ce_sphere_color=GradientColor.from_json(data.get("ce_sphere_color", {})),
			ce_sphere_count=data.get("ce_sphere_count", 100),
			ce_sphere_radius=data.get("ce_sphere_radius", 3.0),
			ce_sphere_radial_speed=data.get("ce_sphere_radial_speed", 2.0),
			ce_flicker=data.get("ce_flicker", False),
		)
