"""DynFireworkMod v2.0 /df 命令字符串生成.
每个 cmd_*() 函数生成一条高层 /df 命令
"""
from __future__ import annotations

from dyn.lib import global_storage

def _add(tick: int, cmd: str) -> None:
	global_storage.add_command(tick, cmd)

def cmd_single_layer(x: float, y: float, z: float,
                     r1: int, g1: int, b1: int, r2: int, g2: int, b2: int,
                     speed: float, particle_count: int,
                     duration: float, lifetime: float, flicker: bool) -> str:
	return (f"/df singlelayer {x:.2f} {y:.2f} {z:.2f} "
	        f"{r1} {g1} {b1} {r2} {g2} {b2} "
	        f"{speed:.2f} {particle_count} {duration:.2f} {lifetime:.2f} "
	        f"{str(flicker).lower()}")

def cmd_double_layer(x: float, y: float, z: float,
                     ir1: int, ig1: int, ib1: int, ir2: int, ig2: int, ib2: int,
                     or1: int, og1: int, ob1: int, or2: int, og2: int, ob2: int,
                     inner_speed: float, outer_speed: float,
                     inner_count: int, outer_count: int,
                     h_angle: float, v_angle: float,
                     duration: float, lifetime: float, flicker: bool) -> str:
	return (f"/df doublelayer {x:.2f} {y:.2f} {z:.2f} "
	        f"{ir1} {ig1} {ib1} {ir2} {ig2} {ib2} "
	        f"{or1} {og1} {ob1} {or2} {og2} {ob2} "
	        f"{inner_speed:.2f} {outer_speed:.2f} {inner_count} {outer_count} "
	        f"{h_angle:.1f} {v_angle:.1f} "
	        f"{duration:.2f} {lifetime:.2f} {str(flicker).lower()}")

def cmd_directional(x: float, y: float, z: float,
                    r1: int, g1: int, b1: int, r2: int, g2: int, b2: int,
                    speed: float, h_angle: float, v_angle: float,
                    spread_angle: float, track_count: int,
                    duration: float, lifetime: float, flicker: bool) -> str:
	return (f"/df directional {x:.2f} {y:.2f} {z:.2f} "
	        f"{r1} {g1} {b1} {r2} {g2} {b2} "
	        f"{speed:.2f} {h_angle:.1f} {v_angle:.1f} "
	        f"{spread_angle:.1f} {track_count} "
	        f"{duration:.2f} {lifetime:.2f} {str(flicker).lower()}")

def cmd_clustered(x: float, y: float, z: float,
                  r1: int, g1: int, b1: int, r2: int, g2: int, b2: int,
                  speed: float, h_angle: float, v_angle: float,
                  direction_count: int, spread_angle: float, track_count: int,
                  duration: float, lifetime: float, flicker: bool) -> str:
	return (f"/df clustered {x:.2f} {y:.2f} {z:.2f} "
	        f"{r1} {g1} {b1} {r2} {g2} {b2} "
	        f"{speed:.2f} {h_angle:.1f} {v_angle:.1f} "
	        f"{direction_count} {spread_angle:.1f} {track_count} "
	        f"{duration:.2f} {lifetime:.2f} {str(flicker).lower()}")

def cmd_expanding(x: float, y: float, z: float,
                  r1: int, g1: int, b1: int, r2: int, g2: int, b2: int,
                  radius: float, radial_speed: float, particle_count: int,
                  lifetime: float, flicker: bool) -> str:
	return (f"/df expanding {x:.2f} {y:.2f} {z:.2f} "
	        f"{r1} {g1} {b1} {r2} {g2} {b2} "
	        f"{radius:.2f} {radial_speed:.2f} {particle_count} "
	        f"{lifetime:.2f} {str(flicker).lower()}")

def cmd_nebula(x: float, y: float, z: float,
               r1: int, g1: int, b1: int, r2: int, g2: int, b2: int,
               particle_count: int, expansion_speed: float,
               density_falloff: float, duration: float, flicker: bool) -> str:
	return (f"/df nebula {x:.2f} {y:.2f} {z:.2f} "
	        f"{r1} {g1} {b1} {r2} {g2} {b2} "
	        f"{particle_count} {expansion_speed:.2f} {density_falloff:.2f} "
	        f"{duration:.2f} {str(flicker).lower()}")

# Trajectory commands

def cmd_launch(x0: float, y0: float, z0: float, x1: float, y1: float, z1: float,
               r1: int, g1: int, b1: int, r2: int, g2: int, b2: int,
               k: float, m0: float, rho: float, duration: float, lifetime: float) -> str:
	return (f"/df launch {x0:.2f} {y0:.2f} {z0:.2f} {x1:.2f} {y1:.2f} {z1:.2f} "
	        f"{r1} {g1} {b1} {r2} {g2} {b2} "
	        f"{k:.3f} {m0:.3f} {rho:.1f} {duration:.2f} {lifetime:.2f}")

def cmd_launch_spark(x0: float, y0: float, z0: float, x1: float, y1: float, z1: float,
                     r1: int, g1: int, b1: int, r2: int, g2: int, b2: int,
                     k: float, m0: float, particle_count: int,
                     duration: float, lifetime: float) -> str:
	return (f"/df launchspark {x0:.2f} {y0:.2f} {z0:.2f} {x1:.2f} {y1:.2f} {z1:.2f} "
	        f"{r1} {g1} {b1} {r2} {g2} {b2} "
	        f"{k:.3f} {m0:.3f} {particle_count} {duration:.2f} {lifetime:.2f}")

def cmd_expanding_traj(x0: float, y0: float, z0: float, x1: float, y1: float, z1: float,
                       r1: int, g1: int, b1: int, r2: int, g2: int, b2: int,
                       k: float, m0: float, range_x: float, range_y: float, range_z: float,
                       particle_count: int, speed_factor: float,
                       duration: float, lifetime: float) -> str:
	return (f"/df expandingtraj {x0:.2f} {y0:.2f} {z0:.2f} {x1:.2f} {y1:.2f} {z1:.2f} "
	        f"{r1} {g1} {b1} {r2} {g2} {b2} "
	        f"{k:.3f} {m0:.3f} {range_x:.2f} {range_y:.2f} {range_z:.2f} "
	        f"{particle_count} {speed_factor:.2f} {duration:.2f} {lifetime:.2f}")

def cmd_spiral(x0: float, y0: float, z0: float, x1: float, y1: float, z1: float,
               r1: int, g1: int, b1: int, r2: int, g2: int, b2: int,
               k: float, m0: float, spiral_radius: float, spiral_speed: float,
               shrink_exponent: float, particle_count: int,
               duration: float, lifetime: float) -> str:
	return (f"/df spiral {x0:.2f} {y0:.2f} {z0:.2f} {x1:.2f} {y1:.2f} {z1:.2f} "
	        f"{r1} {g1} {b1} {r2} {g2} {b2} "
	        f"{k:.3f} {m0:.3f} {spiral_radius:.2f} {spiral_speed:.2f} "
	        f"{shrink_exponent:.2f} {particle_count} {duration:.2f} {lifetime:.2f}")

# Effect commands

def cmd_beam(x: float, y: float, z: float,
             sr1: int, sg1: int, sb1: int, sr2: int, sg2: int, sb2: int,
             er1: int, eg1: int, eb1: int, er2: int, eg2: int, eb2: int,
             min_speed: float, max_speed: float,
             h_angle: float, v_angle: float, spread_angle: float,
             count: int, particles_per: int, lifetime: float) -> str:
	return (f"/df beam {x:.2f} {y:.2f} {z:.2f} "
	        f"{sr1} {sg1} {sb1} {sr2} {sg2} {sb2} "
	        f"{er1} {eg1} {eb1} {er2} {eg2} {eb2} "
	        f"{min_speed:.2f} {max_speed:.2f} "
	        f"{h_angle:.1f} {v_angle:.1f} {spread_angle:.1f} "
	        f"{count} {particles_per} {lifetime:.2f}")

def cmd_spray(x: float, y: float, z: float,
              sr1: int, sg1: int, sb1: int, sr2: int, sg2: int, sb2: int,
              er1: int, eg1: int, eb1: int, er2: int, eg2: int, eb2: int,
              min_speed: float, max_speed: float,
              h_angle: float, v_angle: float, cone_angle: float,
              duration_ticks: int, particles_per_tick: int,
              particle_lifetime_ticks: int) -> str:
	return (f"/df spray {x:.2f} {y:.2f} {z:.2f} "
	        f"{sr1} {sg1} {sb1} {sr2} {sg2} {sb2} "
	        f"{er1} {eg1} {eb1} {er2} {eg2} {eb2} "
	        f"{min_speed:.2f} {max_speed:.2f} "
	        f"{h_angle:.1f} {v_angle:.1f} {cone_angle:.1f} "
	        f"{duration_ticks} {particles_per_tick} {particle_lifetime_ticks}")

def cmd_double_helix(cx: float, cz: float, base_y: float,
                     radius: float, rise_speed: float, rotation_speed: float,
                     density: int, min_vy: float, max_vy: float,
                     duration_ticks: int, lifetime: float,
                     c1r1: int, c1g1: int, c1b1: int, c1r2: int, c1g2: int, c1b2: int,
                     c2r1: int, c2g1: int, c2b1: int, c2r2: int, c2g2: int, c2b2: int) -> str:
	return (f"/df doublehelix {cx:.2f} {cz:.2f} {base_y:.2f} "
	        f"{radius:.2f} {rise_speed:.2f} {rotation_speed:.2f} "
	        f"{density} {min_vy:.2f} {max_vy:.2f} "
	        f"{duration_ticks} {lifetime:.2f} "
	        f"{c1r1} {c1g1} {c1b1} {c1r2} {c1g2} {c1b2} "
	        f"{c2r1} {c2g1} {c2b1} {c2r2} {c2g2} {c2b2}")

def cmd_rotating_ring(cx: float, cy: float, cz: float,
                      ring_radius: float, tube_radius: float,
                      rotation_speed: float, density: int,
                      radial_velocity: float, duration_ticks: int, lifetime: float,
                      r1: int, g1: int, b1: int, r2: int, g2: int, b2: int) -> str:
	return (f"/df rotatingring {cx:.2f} {cy:.2f} {cz:.2f} "
	        f"{ring_radius:.2f} {tube_radius:.2f} "
	        f"{rotation_speed:.2f} {density} {radial_velocity:.2f} "
	        f"{duration_ticks} {lifetime:.2f} "
	        f"{r1} {g1} {b1} {r2} {g2} {b2}")

# Composite commands

def cmd_secondary_explosion(sx: float, sy: float, sz: float,
                            mx: float, my: float, mz: float,
                            k: float, m0: float,
                            p_type: str,
                            pr1: int, pg1: int, pb1: int, pr2: int, pg2: int, pb2: int,
                            p_speed: float, p_count: int, p_duration: float,
                            p_lifetime: float, p_track_count: int,
                            p_spread: float, p_h_angle: float, p_v_angle: float,
                            s_type: str,
                            sr1: int, sg1: int, sb1: int, sr2: int, sg2: int, sb2: int,
                            s_radius: float, s_count: int, s_radial_speed: float,
                            s_lifetime: float, s_speed: float, s_duration: float) -> str:
	return (f"/df secondaryexplosion {sx:.2f} {sy:.2f} {sz:.2f} "
	        f"{mx:.2f} {my:.2f} {mz:.2f} "
	        f"{k:.3f} {m0:.3f} "
	        f"{p_type} {pr1} {pg1} {pb1} {pr2} {pg2} {pb2} "
	        f"{p_speed:.2f} {p_count} {p_duration:.2f} {p_lifetime:.2f} "
	        f"{p_track_count} {p_spread:.1f} {p_h_angle:.1f} {p_v_angle:.1f} "
	        f"{s_type} {sr1} {sg1} {sb1} {sr2} {sg2} {sb2} "
	        f"{s_radius:.2f} {s_count} {s_radial_speed:.2f} "
	        f"{s_lifetime:.2f} {s_speed:.2f} {s_duration:.2f}")

def cmd_combo_ec(x: float, y: float, z: float,
                 cr1: int, cg1: int, cb1: int, cr2: int, cg2: int, cb2: int,
                 c_speed: float, dir_count: int, track_count: int, spread: float,
                 c_duration: float, c_lifetime: float,
                 sr1: int, sg1: int, sb1: int, sr2: int, sg2: int, sb2: int,
                 s_count: int,
                 flicker: bool) -> str:
	return (f"/df combo_ec {x:.2f} {y:.2f} {z:.2f} "
	        f"{cr1} {cg1} {cb1} {cr2} {cg2} {cb2} "
	        f"{c_speed:.2f} {dir_count} {track_count} {spread:.1f} "
	        f"{c_duration:.2f} {c_lifetime:.2f} "
	        f"{sr1} {sg1} {sb1} {sr2} {sg2} {sb2} "
	        f"{s_count} {str(flicker).lower()}")

# Spark / Shell (auxiliary)

def cmd_spark(x: float, y: float, z: float,
              vx: float, vy: float, vz: float,
              r: int, g: int, b: int, lifetime: int) -> str:
	return (f"/df spark {x:.2f} {y:.2f} {z:.2f} "
	        f"{vx:.4f} {vy:.4f} {vz:.4f} "
	        f"{r} {g} {b} {lifetime}")

def cmd_shell(x: float, y: float, z: float,
              r: int, g: int, b: int, size: float) -> str:
	return f"/df shell {x:.2f} {y:.2f} {z:.2f} {r} {g} {b} {size:.2f}"
