"""EffectElement - 特殊效果 不属于烟花/轨迹的独立视觉效果."""
from __future__ import annotations

from dataclasses import dataclass, field

from .base import Element, ElementCategory
from .values import GradientColor, Position, EffectType

@dataclass
class EffectElement(Element):
	effect_type: EffectType = EffectType.BEAM
	position: Position = field(default_factory=Position)

	# Beam
	beam_start_color: GradientColor = field(default_factory=GradientColor)
	beam_end_color: GradientColor = field(default_factory=GradientColor)
	beam_min_speed: float = 1.0
	beam_max_speed: float = 3.0
	beam_h_angle: float = 0.0
	beam_v_angle: float = 0.0
	beam_spread_angle: float = 15.0
	beam_count: int = 8
	beam_particles_per: int = 10
	beam_lifetime: float = 2.0

	# Spray
	spray_start_color: GradientColor = field(default_factory=GradientColor)
	spray_end_color: GradientColor = field(default_factory=GradientColor)
	spray_min_speed: float = 1.0
	spray_max_speed: float = 3.0
	spray_h_angle: float = 0.0
	spray_v_angle: float = 0.0
	spray_cone_angle: float = 15.0
	spray_duration_ticks: int = 40
	spray_particles_per_tick: int = 3
	spray_particle_lifetime_ticks: int = 20

	# DoubleHelix
	dh_radius: float = 2.0
	dh_rise_speed: float = 3.0
	dh_rotation_speed: float = 5.0
	dh_density: int = 20
	dh_min_vy: float = 0.0
	dh_max_vy: float = 1.0
	dh_lifetime: float = 2.0
	dh_duration_ticks: int = 100
	dh_color1: GradientColor = field(default_factory=GradientColor)
	dh_color2: GradientColor = field(default_factory=GradientColor)

	# RotatingRing
	rr_ring_radius: float = 3.0
	rr_tube_radius: float = 0.5
	rr_rotation_speed: float = 2.0
	rr_density: int = 30
	rr_radial_velocity: float = 1.0
	rr_lifetime: float = 3.0
	rr_duration_ticks: int = 100
	rr_color: GradientColor = field(default_factory=GradientColor)

	@property
	def category(self) -> ElementCategory:
		return ElementCategory.EFFECT

	def to_json(self) -> dict:
		base = super().to_json()
		base.update({
			"type": self.effect_type.value,
			"position": self.position.to_json(),
			# Beam
			"beam_start_color": self.beam_start_color.to_json(),
			"beam_end_color": self.beam_end_color.to_json(),
			"beam_min_speed": self.beam_min_speed,
			"beam_max_speed": self.beam_max_speed,
			"beam_h_angle": self.beam_h_angle,
			"beam_v_angle": self.beam_v_angle,
			"beam_spread_angle": self.beam_spread_angle,
			"beam_count": self.beam_count,
			"beam_particles_per": self.beam_particles_per,
			"beam_lifetime": self.beam_lifetime,
			# Spray
			"spray_start_color": self.spray_start_color.to_json(),
			"spray_end_color": self.spray_end_color.to_json(),
			"spray_min_speed": self.spray_min_speed,
			"spray_max_speed": self.spray_max_speed,
			"spray_h_angle": self.spray_h_angle,
			"spray_v_angle": self.spray_v_angle,
			"spray_cone_angle": self.spray_cone_angle,
			"spray_duration_ticks": self.spray_duration_ticks,
			"spray_particles_per_tick": self.spray_particles_per_tick,
			"spray_particle_lifetime_ticks": self.spray_particle_lifetime_ticks,
			# DoubleHelix
			"dh_radius": self.dh_radius,
			"dh_rise_speed": self.dh_rise_speed,
			"dh_rotation_speed": self.dh_rotation_speed,
			"dh_density": self.dh_density,
			"dh_min_vy": self.dh_min_vy,
			"dh_max_vy": self.dh_max_vy,
			"dh_lifetime": self.dh_lifetime,
			"dh_duration_ticks": self.dh_duration_ticks,
			"dh_color1": self.dh_color1.to_json(),
			"dh_color2": self.dh_color2.to_json(),
			# RotatingRing
			"rr_ring_radius": self.rr_ring_radius,
			"rr_tube_radius": self.rr_tube_radius,
			"rr_rotation_speed": self.rr_rotation_speed,
			"rr_density": self.rr_density,
			"rr_radial_velocity": self.rr_radial_velocity,
			"rr_lifetime": self.rr_lifetime,
			"rr_duration_ticks": self.rr_duration_ticks,
			"rr_color": self.rr_color.to_json(),
		})
		return base

	@classmethod
	def from_json(cls, data: dict) -> EffectElement:
		base = cls._from_json_base(data)
		return cls(
			**base,
			effect_type=EffectType(data.get("type", "beam")),
			position=Position.from_json(data.get("position", {})),
			# Beam
			beam_start_color=GradientColor.from_json(data.get("beam_start_color", {})),
			beam_end_color=GradientColor.from_json(data.get("beam_end_color", {})),
			beam_min_speed=data.get("beam_min_speed", 1.0),
			beam_max_speed=data.get("beam_max_speed", 3.0),
			beam_h_angle=data.get("beam_h_angle", 0.0),
			beam_v_angle=data.get("beam_v_angle", 0.0),
			beam_spread_angle=data.get("beam_spread_angle", 15.0),
			beam_count=data.get("beam_count", 8),
			beam_particles_per=data.get("beam_particles_per", 10),
			beam_lifetime=data.get("beam_lifetime", 2.0),
			# Spray
			spray_start_color=GradientColor.from_json(data.get("spray_start_color", {})),
			spray_end_color=GradientColor.from_json(data.get("spray_end_color", {})),
			spray_min_speed=data.get("spray_min_speed", 1.0),
			spray_max_speed=data.get("spray_max_speed", 3.0),
			spray_h_angle=data.get("spray_h_angle", 0.0),
			spray_v_angle=data.get("spray_v_angle", 0.0),
			spray_cone_angle=data.get("spray_cone_angle", 15.0),
			spray_duration_ticks=data.get("spray_duration_ticks", 40),
			spray_particles_per_tick=data.get("spray_particles_per_tick", 3),
			spray_particle_lifetime_ticks=data.get("spray_particle_lifetime_ticks", 20),
			# DoubleHelix
			dh_radius=data.get("dh_radius", 2.0),
			dh_rise_speed=data.get("dh_rise_speed", 3.0),
			dh_rotation_speed=data.get("dh_rotation_speed", 5.0),
			dh_density=data.get("dh_density", 20),
			dh_min_vy=data.get("dh_min_vy", 0.0),
			dh_max_vy=data.get("dh_max_vy", 1.0),
			dh_lifetime=data.get("dh_lifetime", 2.0),
			dh_duration_ticks=data.get("dh_duration_ticks", 100),
			dh_color1=GradientColor.from_json(data.get("dh_color1", {})),
			dh_color2=GradientColor.from_json(data.get("dh_color2", {})),
			# RotatingRing
			rr_ring_radius=data.get("rr_ring_radius", 3.0),
			rr_tube_radius=data.get("rr_tube_radius", 0.5),
			rr_rotation_speed=data.get("rr_rotation_speed", 2.0),
			rr_density=data.get("rr_density", 30),
			rr_radial_velocity=data.get("rr_radial_velocity", 1.0),
			rr_lifetime=data.get("rr_lifetime", 3.0),
			rr_duration_ticks=data.get("rr_duration_ticks", 100),
			rr_color=GradientColor.from_json(data.get("rr_color", {})),
		)
