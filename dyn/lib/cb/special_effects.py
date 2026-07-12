# special_effects.py
# Special firework effects for advanced visual patterns
# pylint: skip-file
# flake8: noqa
import logging
import math
import random

from dyn.lib.cb import commands

log = logging.getLogger(__name__)

def rotating_ring_with_dispersion(start_tick, duration_ticks, center_x, center_y, center_z,
                                  ring_radius, tube_radius, rotation_speed,
                                  particle_density, radial_velocity, lifetime,
                                  start_color, end_color):
	"""
	Creates a rotating horizontal ring effect where particles continuously spawn
	along a torus and disperse radially outward.

	Parameters:
		start_tick: Starting game tick
		duration_ticks: Duration of the effect in ticks
		center_x, center_y, center_z: Center position of the ring
		ring_radius: Major radius of the torus (distance from center to tube center)
		tube_radius: Minor radius of the torus (thickness of the ring tube)
		rotation_speed: Angular speed in radians per tick
		particle_density: Number of particles to generate per tick
		radial_velocity: Initial velocity magnitude for radial dispersion
		lifetime: Particle lifetime in ticks
		start_color, end_color: Color gradient tuples (R, G, B)
	"""
	log.debug(f"rotating_ring_with_dispersion: start_tick={start_tick}, duration={duration_ticks}, radius={ring_radius}, rotation_speed={rotation_speed}")
	for tick_offset in range(duration_ticks):
		tick = start_tick + tick_offset

		# Current rotation angle
		rotation_angle = rotation_speed * tick_offset

		# Generate particles along the ring
		for _ in range(particle_density):
			# Random position on the torus
			theta = random.uniform(0, 2 * math.pi)  # Angle around the major circle
			phi = random.uniform(0, 2 * math.pi)  # Angle around the tube

			# Torus parametric equations (horizontal ring)
			# Major circle rotates around Y axis
			major_x = ring_radius * math.cos(theta + rotation_angle)
			major_z = ring_radius * math.sin(theta + rotation_angle)

			# Add tube thickness
			x = center_x + major_x + tube_radius * math.cos(phi) * math.cos(theta + rotation_angle)
			y = center_y + tube_radius * math.sin(phi)
			z = center_z + major_z + tube_radius * math.cos(phi) * math.sin(theta + rotation_angle)

			# Radial velocity (outward horizontally only, no vertical component)
			# Direction is perpendicular to the major circle, in the XZ plane
			vx = radial_velocity * math.cos(theta + rotation_angle)
			vy = 0  # No vertical velocity
			vz = radial_velocity * math.sin(theta + rotation_angle)

			# Generate particle
			commands.add_velocity_firework_command(
				tick=tick, x=x, y=y, z=z,
				start_color=start_color, end_color=end_color,
				vx=vx, vy=vy, vz=vz,
				lifetime=lifetime
			)

def spiral_ribbon_with_rise(start_tick, duration_ticks, center_x, center_z,
                            base_y, spiral_radius, rise_speed, rotation_speed,
                            particle_density, vertical_velocity_range, lifetime,
                            start_color, end_color):
	"""
	Creates a spiral ribbon effect where particles spawn in a rotating plane
	and rise upward with varying velocities.

	Parameters:
		start_tick: Starting game tick
		duration_ticks: Duration of the effect in ticks
		center_x, center_z: Center position of the spiral
		base_y: Base Y coordinate where particles spawn
		spiral_radius: Radius of the spiral circle
		rise_speed: Speed at which the spawn plane rises (blocks per tick)
		rotation_speed: Angular speed in radians per tick
		particle_density: Number of particles to generate per tick
		vertical_velocity_range: Tuple (min_vy, max_vy) for random vertical velocity
		lifetime: Particle lifetime in ticks
		start_color, end_color: Color gradient tuples (R, G, B)
	"""
	log.debug(f"spiral_ribbon_with_rise: start_tick={start_tick}, duration={duration_ticks}, radius={spiral_radius}, rise_speed={rise_speed}")
	min_vy, max_vy = vertical_velocity_range

	for tick_offset in range(duration_ticks):
		tick = start_tick + tick_offset

		# Current rotation angle and height
		rotation_angle = rotation_speed * tick_offset
		current_y = base_y + rise_speed * tick_offset

		# Generate particles in a circle at current height
		for _ in range(particle_density):
			# Random position on the circle
			angle = random.uniform(0, 2 * math.pi)
			radius_factor = random.uniform(0.5, 1.0)  # Vary radius for ribbon effect

			x = center_x + spiral_radius * radius_factor * math.cos(angle + rotation_angle)
			z = center_z + spiral_radius * radius_factor * math.sin(angle + rotation_angle)
			y = current_y

			# Random upward velocity
			vx = 0
			vy = random.uniform(min_vy, max_vy)
			vz = 0

			# Generate particle
			commands.add_velocity_firework_command(
				tick=tick, x=x, y=y, z=z,
				start_color=start_color, end_color=end_color,
				vx=vx, vy=vy, vz=vz,
				lifetime=lifetime
			)

def double_helix_spiral(start_tick, duration_ticks, center_x, center_z,
                        base_y, helix_radius, rise_speed, rotation_speed,
                        particle_density, vertical_velocity_range, lifetime,
                        color1, color2):
	"""
	Creates a DNA-like double helix effect with two intertwining spirals.
	Each spiral has its own color and rises upward.

	Parameters:
		start_tick: Starting game tick
		duration_ticks: Duration of the effect in ticks
		center_x, center_z: Center position of the helix
		base_y: Base Y coordinate where particles spawn
		helix_radius: Radius of the helix
		rise_speed: Speed at which the spawn plane rises (blocks per tick)
		rotation_speed: Angular speed in radians per tick
		particle_density: Number of particles per helix per tick
		vertical_velocity_range: Tuple (min_vy, max_vy) for random vertical velocity
		lifetime: Particle lifetime in ticks
		color1, color2: Tuples of (start_color, end_color) for each helix
	"""
	log.debug(f"double_helix_spiral: start_tick={start_tick}, duration={duration_ticks}, radius={helix_radius}, rise_speed={rise_speed}")
	min_vy, max_vy = vertical_velocity_range

	for tick_offset in range(duration_ticks):
		tick = start_tick + tick_offset

		# Current rotation angle and height
		rotation_angle = rotation_speed * tick_offset
		current_y = base_y + rise_speed * tick_offset

		# Generate two helices with 180 degree phase offset
		for helix_idx in range(2):
			phase_offset = helix_idx * math.pi  # 180 degrees apart
			current_color = color1 if helix_idx == 0 else color2
			start_c, end_c = current_color

			for _ in range(particle_density):
				# Position on helix
				x = center_x + helix_radius * math.cos(rotation_angle + phase_offset)
				z = center_z + helix_radius * math.sin(rotation_angle + phase_offset)
				y = current_y + random.uniform(-0.5, 0.5)  # Small Y variation

				# Random upward velocity
				vx = 0
				vy = random.uniform(min_vy, max_vy)
				vz = 0

				# Generate particle
				commands.add_velocity_firework_command(
					tick=tick, x=x, y=y, z=z,
					start_color=start_c, end_color=end_c,
					vx=vx, vy=vy, vz=vz,
					lifetime=lifetime
				)
