# main.py
# pylint: skip-file
# flake8: noqa
import os
import sys
# Add project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import math
from gui.lib import shared_functions
from gui.lib import basic_fireworks
from gui.lib import export_mcfunction
from gui.lib import firework_trajectories
from gui.lib import special_effects


if __name__ == '__main__':
    # --- Setup ---
    namespace = 'fireworks1'
    output_dir = os.path.dirname(os.path.abspath(__file__)) + "/functions/"
    
    import random
    from gui.lib import global_storage
    
    # Always clear previous commands at the start
    global_storage.commands_by_tick.clear()
    global_storage.MAX_TICK = 0

    # Add BGM playsound command to the very first tick
    global_storage.add_command(0, 'playsound minecraft:bgm player @a')

    # --- Constants and Helpers ---
    # Expanded ranges for a wider show
    FIREWORK_X_RANGE = (950, 990)
    FIREWORK_Z_RANGE = (-245, -165)
    FIREWORK_Y_BASE = -60
    # Hierarchical Y-levels for visual separation
    MELODY_Y_EXPLODE_MIN = -50
    MELODY_Y_EXPLODE_MAX = -40
    DRUM_Y_EXPLODE_MIN = -30
    DRUM_Y_EXPLODE_MAX = -15

    def timecode_to_tick(tc: str, fps: int = 24, tps: int = 20) -> int:
        parts = list(map(int, tc.split(':')))
        total_frames = (parts[0] * 3600 + parts[1] * 60 + parts[2]) * fps + parts[3]
        total_seconds = total_frames / fps
        return int(total_seconds * tps)

    # --- Part 1: Fractures (00:00:00:22 - 00:00:12:22) ---
    # Corrected end time to fix timing algorithm
    start_tick_abs = timecode_to_tick("00:00:00:22")
    end_tick_abs = timecode_to_tick("00:00:12:22")
    total_ticks_duration = end_tick_abs - start_tick_abs
    ticks_per_16th = total_ticks_duration / 64

    def get_tick(note_index: int) -> int:
        return round(start_tick_abs + note_index * ticks_per_16th)

    # --- Guitar (Enhanced visuals) ---
    guitar_notes_indices = [0, 4, 8, 12, 16, 21, 26, 32, 36, 42, 46, 52]
    colors1 = ((200, 200, 255), (255, 255, 255)) # Light Blue -> White
    colors2 = ((220, 180, 255), (255, 255, 255)) # Light Purple -> White
    for idx, i in enumerate(guitar_notes_indices):
        tick = get_tick(i)
        x = random.uniform(FIREWORK_X_RANGE[0], FIREWORK_X_RANGE[1])
        z = random.uniform(FIREWORK_Z_RANGE[0], FIREWORK_Z_RANGE[1])
        y = random.uniform(MELODY_Y_EXPLODE_MIN, MELODY_Y_EXPLODE_MAX)
        
        start_c, end_c = colors1 if idx % 2 == 0 else colors2

        # Launch spark trajectory for guitar firework (with tilt)
        x0 = x + random.uniform(-3, 3)
        z0 = z + random.uniform(-3, 3)
        firework_trajectories.launch_spark_trajectory(
            end_tick=tick,
            x0=x0, y0=-64, z0=z0,
            x1=x, y1=y, z1=z,
            duration=0.5,
            k=1.0, m0=8, lifetime=0.8, particle_count=2
        )

        basic_fireworks.clustered_firework(
            tick=tick, x=x, y=y, z=z,
            start_color=start_c, end_color=end_c,
            speed=15,
            horizontal_angle_step=45, vertical_angle_step=45,
            spread_angle=20,
            track_count=4,
            duration=1.8, lifetime=2.0
        )

    # --- Vocals (Single shooting star - Reworked) ---
    vocal_note_index = 50
    tick = get_tick(vocal_note_index)
    x0 = FIREWORK_X_RANGE[0] + 5 # Start from one side
    z0 = random.uniform(FIREWORK_Z_RANGE[0], FIREWORK_Z_RANGE[1])
    y0 = FIREWORK_Y_BASE
    x1, y1, z1 = x0 + 10, MELODY_Y_EXPLODE_MAX + 10, z0 + random.uniform(-5, 5)
    
    firework_trajectories.launch_spark_trajectory(
        end_tick=tick, x0=x0, y0=y0, z0=z0, x1=x1, y1=y1, z1=z1,
        duration=1.2, k=0.5, m0=5, lifetime=1.3, particle_count=2
    )
    # Replaced downward directional firework with a conventional, denser one
    basic_fireworks.clustered_firework(
        tick=tick, x=x1, y=y1, z=z1,
        start_color=(255, 215, 0), end_color=(255, 165, 0), # Gold/Orange
        speed=12,
        horizontal_angle_step=50, # Reduced density
        vertical_angle_step=50,   # Reduced density
        spread_angle=20,
        track_count=5,
        duration=1.8,
        lifetime=2.2
    )

    # --- Kick Drum (Key emphasis) ---
    # Elevated to DRUM_Y_EXPLODE, new colors, separated on Z-axis
    x_center = (FIREWORK_X_RANGE[0] + FIREWORK_X_RANGE[1]) / 2
    z_center = (FIREWORK_Z_RANGE[0] + FIREWORK_Z_RANGE[1]) / 2
    kick_drum_positions = [
        (x_center, z_center - 15), # Back
        (x_center, z_center + 15)  # Front
    ]
    for i, pos in enumerate(kick_drum_positions):
        tick = get_tick(62 + i)
        x0, z0 = pos
        y0 = FIREWORK_Y_BASE
        x1, y1, z1 = x0 + random.uniform(-2, 2), random.uniform(DRUM_Y_EXPLODE_MIN, DRUM_Y_EXPLODE_MAX), z0 + random.uniform(-2, 2)
        
        basic_fireworks.expanding_sphere_firework(
            tick=tick, x=x1, y=y1, z=z1,
            start_color=(255, 0, 0), end_color=(255, 69, 0), # Red to OrangeRed
            radius=0.5,
            particle_count=80,
            radial_speed=1.0,
            lifetime=50
        )

    # --- Part 2: Fractures (00:00:12:22 - 00:00:24:22) ---
    # Section start time is the end time of the previous section
    start_tick_p2 = end_tick_abs
    end_tick_p2 = timecode_to_tick("00:00:24:22")
    total_ticks_p2 = end_tick_p2 - start_tick_p2
    ticks_per_16th_p2 = total_ticks_p2 / 64

    def get_tick_p2(note_index: int) -> int:
        # note_index is 0-63 for this part
        return round(start_tick_p2 + note_index * ticks_per_16th_p2)

    # --- Guitar (Part 2) ---
    # Rhythm is the same as Part 1, just offset in time
    for idx, i in enumerate(guitar_notes_indices): # Re-using from Part 1
        tick = get_tick_p2(i)
        x = random.uniform(FIREWORK_X_RANGE[0], FIREWORK_X_RANGE[1])
        z = random.uniform(FIREWORK_Z_RANGE[0], FIREWORK_Z_RANGE[1])
        y = random.uniform(MELODY_Y_EXPLODE_MIN, MELODY_Y_EXPLODE_MAX)
        
        start_c, end_c = colors1 if idx % 2 == 0 else colors2

        # Launch spark trajectory for guitar firework (with tilt)
        x0 = x + random.uniform(-3, 3)
        z0 = z + random.uniform(-3, 3)
        firework_trajectories.launch_spark_trajectory(
            end_tick=tick,
            x0=x0, y0=-64, z0=z0,
            x1=x, y1=y, z1=z,
            duration=0.5,
            k=1.0, m0=8, lifetime=0.8, particle_count=2
        )

        basic_fireworks.clustered_firework(
            tick=tick, x=x, y=y, z=z,
            start_color=start_c, end_color=end_c,
            speed=15,
            horizontal_angle_step=50, vertical_angle_step=50,
            spread_angle=20,
            track_count=4,
            duration=1.8, lifetime=2.0
        )

    # --- Vocals (Part 2) ---
    tick = get_tick_p2(vocal_note_index) # Re-using from Part 1
    x0 = FIREWORK_X_RANGE[0] + 5
    z0 = random.uniform(FIREWORK_Z_RANGE[0], FIREWORK_Z_RANGE[1])
    y0 = FIREWORK_Y_BASE
    x1, y1, z1 = x0 + 10, MELODY_Y_EXPLODE_MAX + 10, z0 + random.uniform(-5, 5)
    
    firework_trajectories.launch_spark_trajectory(
        end_tick=tick, x0=x0, y0=y0, z0=z0, x1=x1, y1=y1, z1=z1,
        duration=1.2, k=0.5, m0=5, lifetime=1.3, particle_count=2
    )
    basic_fireworks.clustered_firework(
        tick=tick, x=x1, y=y1, z=z1,
        start_color=(255, 215, 0), end_color=(255, 165, 0),
        speed=12,
        horizontal_angle_step=50, vertical_angle_step=50,
        spread_angle=20,
        track_count=5,
        duration=1.8, lifetime=2.2
    )
    
    # --- Snare Drum (Part 2) ---
    # Replaced summon with a custom particle firework to avoid command conflicts
    snare_rhythm_p2 = "0000100000001000" * 4
    snare_indices_p2 = [i for i, char in enumerate(snare_rhythm_p2) if char == '1']
    for i in snare_indices_p2:
        tick = get_tick_p2(i)
        x = random.uniform(FIREWORK_X_RANGE[0], FIREWORK_X_RANGE[1])
        z = random.uniform(FIREWORK_Z_RANGE[0], FIREWORK_Z_RANGE[1])
        y = random.uniform(DRUM_Y_EXPLODE_MIN, DRUM_Y_EXPLODE_MAX)
        
        # Switched to clustered firework for a fuller effect
        basic_fireworks.clustered_firework(
            tick=tick, x=x, y=y, z=z,
            start_color=(255, 255, 0), end_color=(255, 165, 0), # Yellow to Orange
            speed=26, # Increased
            horizontal_angle_step=45, vertical_angle_step=45,
            spread_angle=20,
            track_count=7,
            duration=1.0, lifetime=1.2
        )

    # --- Kick Drum (Part 2) ---
    # Elevated, new colors, wider random placement
    kick_indices_p2 = [0, 2, 9, 10, 15, 16, 18, 25, 26, 31, 32, 34, 41, 42, 47, 48, 50, 57, 58, 63]
    last_kick_pos = None
    min_dist_sq = 15**2 # Minimum distance squared (15 blocks)

    for i in kick_indices_p2:
        tick = get_tick_p2(i)
        
        # Generate a new position in the wider range and check distance
        for _ in range(10):
            x0 = random.uniform(FIREWORK_X_RANGE[0], FIREWORK_X_RANGE[1])
            z0 = random.uniform(FIREWORK_Z_RANGE[0], FIREWORK_Z_RANGE[1])
            if last_kick_pos is None or ((x0 - last_kick_pos[0])**2 + (z0 - last_kick_pos[2])**2) > min_dist_sq:
                break
        
        y0 = FIREWORK_Y_BASE    
        last_kick_pos = (x0, y0, z0)

        x1, y1, z1 = x0, random.uniform(DRUM_Y_EXPLODE_MIN, DRUM_Y_EXPLODE_MAX), z0
        
        basic_fireworks.expanding_sphere_firework(
            tick=tick, x=x1, y=y1, z=z1,
            start_color=(255, 0, 0), end_color=(255, 69, 0), # Red to OrangeRed
            radius=0.5,
            particle_count=80,
            radial_speed=1.0,
            lifetime=50
        )

    # --- Part 3: Fractures (00:00:24:22 - 00:00:36:22) ---
    start_tick_p3 = end_tick_p2
    end_tick_p3 = timecode_to_tick("00:00:36:22")
    total_ticks_p3 = end_tick_p3 - start_tick_p3
    ticks_per_16th_p3 = total_ticks_p3 / 64

    def get_tick_p3(note_index: int) -> int:
        # note_index is 0-63 for this part
        return round(start_tick_p3 + note_index * ticks_per_16th_p3)

    # --- Vocals (Part 3 - Left-to-Right Sweep) ---
    vocal_indices_p3 = [2, 6, 9, 14, 18, 21, 22, 32, 34, 38, 44, 46, 47]
    num_vocal_notes = len(vocal_indices_p3)
    x_sweep_start = FIREWORK_X_RANGE[0] + 3
    x_sweep_end = FIREWORK_X_RANGE[1] - 3

    for i, note_idx in enumerate(vocal_indices_p3):
        tick = get_tick_p3(note_idx)
        
        # Interpolate X position for the sweep
        progress = i / (num_vocal_notes - 1) if num_vocal_notes > 1 else 0.5
        x = x_sweep_start + (x_sweep_end - x_sweep_start) * progress
        
        z = random.uniform(FIREWORK_Z_RANGE[0], FIREWORK_Z_RANGE[1])
        y = random.uniform(MELODY_Y_EXPLODE_MIN, MELODY_Y_EXPLODE_MAX)
        
        start_c, end_c = colors2 # Using the purple color scheme

        # Launch spark trajectory for vocal firework (with tilt)
        x0 = x + random.uniform(-3, 3)
        z0 = z + random.uniform(-3, 3)
        firework_trajectories.launch_spark_trajectory(
            end_tick=tick,
            x0=x0, y0=-64, z0=z0,
            x1=x, y1=y, z1=z,
            duration=0.5,
            k=1.0, m0=8, lifetime=0.8, particle_count=2
        )

        basic_fireworks.clustered_firework(
            tick=tick, x=x, y=y, z=z,
            start_color=start_c, end_color=end_c,
            speed=15,
            horizontal_angle_step=45, vertical_angle_step=45,
            spread_angle=20,
            track_count=4,
            duration=1.8, lifetime=2.0
        )

    # --- Snare Drum (Part 3) ---
    # Replaced summon with a custom particle firework
    snare_rhythm_p3 = "0000100000001000" * 4
    snare_indices_p3 = [i for i, char in enumerate(snare_rhythm_p3) if char == '1']
    for i in snare_indices_p3:
        tick = get_tick_p3(i)
        x = random.uniform(FIREWORK_X_RANGE[0], FIREWORK_X_RANGE[1])
        z = random.uniform(FIREWORK_Z_RANGE[0], FIREWORK_Z_RANGE[1])
        y = random.uniform(DRUM_Y_EXPLODE_MIN, DRUM_Y_EXPLODE_MAX)
    
        # Softer version for Part 3
        basic_fireworks.clustered_firework(
            tick=tick, x=x, y=y, z=z,
            start_color=(255, 255, 0), end_color=(255, 165, 0), # Yellow to Orange
            speed=20, # Increased
            horizontal_angle_step=50, vertical_angle_step=50,
            spread_angle=22,
            track_count=5, # Reduced tracks
            duration=1.0, lifetime=1.2
        )

    # --- Kick Drum (Part 3) ---
    last_kick_pos_p3 = None
    for i in kick_indices_p2: # kick_indices_p2 is [0, 2, 9, ...]
        tick = get_tick_p3(i)
        
        for _ in range(10):
            x0 = random.uniform(FIREWORK_X_RANGE[0], FIREWORK_X_RANGE[1])
            z0 = random.uniform(FIREWORK_Z_RANGE[0], FIREWORK_Z_RANGE[1])
            if last_kick_pos_p3 is None or ((x0 - last_kick_pos_p3[0])**2 + (z0 - last_kick_pos_p3[2])**2) > min_dist_sq:
                break
        
        y0 = FIREWORK_Y_BASE
        last_kick_pos_p3 = (x0, y0, z0)

        x1, y1, z1 = x0, random.uniform(DRUM_Y_EXPLODE_MIN, DRUM_Y_EXPLODE_MAX), z0
        
        # Softer version for Part 3
        basic_fireworks.expanding_sphere_firework(
            tick=tick, x=x1, y=y1, z=z1,
            start_color=(255, 0, 0), end_color=(255, 69, 0), # Red to OrangeRed
            radius=0.5,
            particle_count=80,
            radial_speed=1.0,
            lifetime=50
        )

    # --- Part 4: Fractures (00:00:36:22 - 00:00:48:22) ---
    start_tick_p4 = end_tick_p3
    end_tick_p4 = timecode_to_tick("00:00:48:22")
    total_ticks_p4 = end_tick_p4 - start_tick_p4
    ticks_per_16th_p4 = total_ticks_p4 / 64

    def get_tick_p4(note_index: int) -> int:
        return round(start_tick_p4 + note_index * ticks_per_16th_p4)

    # --- Bass (New Element - Expanding Trajectories) ---
    # The first two bass notes are at the end of Part 3
    bass_intro_indices = [62, 63]
    for i in bass_intro_indices:
        tick = get_tick_p3(i)
        x0 = random.uniform(FIREWORK_X_RANGE[0], FIREWORK_X_RANGE[1])
        z0 = random.uniform(FIREWORK_Z_RANGE[0], FIREWORK_Z_RANGE[1])
        y0 = FIREWORK_Y_BASE
        x1, y1, z1 = x0, random.uniform(MELODY_Y_EXPLODE_MIN, MELODY_Y_EXPLODE_MAX), z0
        
        firework_trajectories.expanding_trajectory_with_random_offset(
            end_tick=tick, x0=x0, y0=y0, z0=z0, x1=x1, y1=y1, z1=z1,
            k=0.8, m0=8, duration=1.0, lifetime=1.2, interval_ticks=5,
            points_per_tick=2, range_x=0.5, range_y=0.5, range_z=0.5,
            particle_count=2, speed_factor=1.5  # Reduced from 3 to 1.5
        )

    bass_indices_p4 = [i for i, char in enumerate("1000000010000000" * 4) if char == '1']
    for i in bass_indices_p4:
        tick = get_tick_p4(i)
        x0 = random.uniform(FIREWORK_X_RANGE[0], FIREWORK_X_RANGE[1])
        z0 = random.uniform(FIREWORK_Z_RANGE[0], FIREWORK_Z_RANGE[1])
        y0 = FIREWORK_Y_BASE
        x1, y1, z1 = x0, random.uniform(MELODY_Y_EXPLODE_MIN, MELODY_Y_EXPLODE_MAX), z0

        firework_trajectories.expanding_trajectory_with_random_offset(
            end_tick=tick, x0=x0, y0=y0, z0=z0, x1=x1, y1=y1, z1=z1,
            k=0.8, m0=8, duration=1.0, lifetime=1.2, interval_ticks=5,
            points_per_tick=2, range_x=0.5, range_y=0.5, range_z=0.5,
            particle_count=2, speed_factor=1.5  # Reduced from 3 to 1.5
        )

    # --- Vocals (Part 4 - Right-to-Left Sweep) ---
    vocal_rhythm_p4 = "0010010010010010" + "0010001100000000" + "1001001001000000" + "0000000000000000"
    vocal_indices_p4 = [i for i, char in enumerate(vocal_rhythm_p4) if char == '1']
    num_vocal_notes_p4 = len(vocal_indices_p4)

    for i, note_idx in enumerate(vocal_indices_p4):
        tick = get_tick_p4(note_idx)
        
        progress = i / (num_vocal_notes_p4 - 1) if num_vocal_notes_p4 > 1 else 0.5
        x = x_sweep_end - (x_sweep_end - x_sweep_start) * progress # Reversed sweep
        
        z = random.uniform(FIREWORK_Z_RANGE[0], FIREWORK_Z_RANGE[1])
        y = random.uniform(MELODY_Y_EXPLODE_MIN, MELODY_Y_EXPLODE_MAX)
        
        start_c, end_c = colors1 # Using the blue color scheme for variety
        
        # Launch spark trajectory for vocal firework (with tilt)
        x0 = x + random.uniform(-3, 3)
        z0 = z + random.uniform(-3, 3)
        firework_trajectories.launch_spark_trajectory(
            end_tick=tick,
            x0=x0, y0=-64, z0=z0,
            x1=x, y1=y, z1=z,
            duration=0.5,
            k=1.0, m0=8, lifetime=0.8, particle_count=2
        )
        
        basic_fireworks.clustered_firework(
            tick=tick, x=x, y=y, z=z,
            start_color=start_c, end_color=end_c,
            speed=15,
            horizontal_angle_step=45, vertical_angle_step=45,
            spread_angle=20,
            track_count=4,
            duration=1.8, lifetime=2.0
        )

    # --- Drums (Part 4) ---
    # Corrected snare rhythm to be on the 2nd and 4th quarter notes (backbeat)
    snare_rhythm_p4 = "0000100000001000" * 4
    snare_indices_p4 = [i for i, char in enumerate(snare_rhythm_p4) if char == '1']
    kick_rhythm_p4 = ("1010000001100001" * 3) + "1010000001100000"
    kick_indices_p4 = [i for i, char in enumerate(kick_rhythm_p4) if char == '1']
    
    # Snare
    for i in snare_indices_p4:
        tick = get_tick_p4(i)
        x = random.uniform(FIREWORK_X_RANGE[0], FIREWORK_X_RANGE[1])
        z = random.uniform(FIREWORK_Z_RANGE[0], FIREWORK_Z_RANGE[1])
        y = random.uniform(DRUM_Y_EXPLODE_MIN, DRUM_Y_EXPLODE_MAX)
        # Switched to clustered firework for a fuller effect
        basic_fireworks.clustered_firework(
            tick=tick, x=x, y=y, z=z,
            start_color=(255, 255, 0), end_color=(255, 165, 0), # Yellow to Orange
            speed=26, # Increased
            horizontal_angle_step=45, vertical_angle_step=45,
            spread_angle=20,
            track_count=7,
            duration=1.0, lifetime=1.2
        )
        
    # Kick
    last_kick_pos_p4 = None
    for i in kick_indices_p4:
        tick = get_tick_p4(i)
        for _ in range(10):
            x0 = random.uniform(FIREWORK_X_RANGE[0], FIREWORK_X_RANGE[1])
            z0 = random.uniform(FIREWORK_Z_RANGE[0], FIREWORK_Z_RANGE[1])
            if last_kick_pos_p4 is None or ((x0 - last_kick_pos_p4[0])**2 + (z0 - last_kick_pos_p4[2])**2) > min_dist_sq:
                break
        y0 = FIREWORK_Y_BASE
        last_kick_pos_p4 = (x0, y0, z0)
        x1, y1, z1 = x0, random.uniform(DRUM_Y_EXPLODE_MIN, DRUM_Y_EXPLODE_MAX), z0
        
        basic_fireworks.expanding_sphere_firework(
            tick=tick, x=x1, y=y1, z=z1,
            start_color=(255, 0, 0), end_color=(255, 69, 0), # Red to OrangeRed
            radius=0.5,
            particle_count=80,
            radial_speed=1.0,
            lifetime=50
        )

    # --- Cymbal Roll (End of Part 4) ---
    cymbal_sweep_count = 32  # Doubled from 16 for denser effect
    roll_start_tick = get_tick_p4(62)
    roll_duration_ticks = get_tick_p4(64) - roll_start_tick # Half a beat = 2 16th notes
    
    # Position the sweep close to the audience (x=1027) and sweep across Z
    x_pos_cymbal = 995 
    # Audience facing West (-X), Left is South (+Z), Right is North (-Z)
    # A left-to-right sweep means Z goes from a larger value to a smaller one.
    z_sweep_start = -165 # Left side, expanded
    z_sweep_end = -245   # Right side, expanded

    for i in range(cymbal_sweep_count):
        progress = i / (cymbal_sweep_count - 1)
        tick = roll_start_tick + round(progress * roll_duration_ticks)
        
        # Interpolate Z position for the sweep from left (z_sweep_start) to right (z_sweep_end)
        z_pos = z_sweep_start + (z_sweep_end - z_sweep_start) * progress
        
        # Direction: From audience POV (facing west), bottom-left to top-right.
        # Vertical angle: upwards (e.g., 45 degrees).
        # Horizontal angle: pointing right (towards -Z), so around -90 degrees.
        basic_fireworks.directional_firework(
            tick=tick, 
            x=x_pos_cymbal, y=FIREWORK_Y_BASE, z=z_pos,
            start_color=(255, 255, 0), end_color=(255, 165, 0), # Yellow to Orange
            speed=24,
            direction_horizontal_angle=-90,
            direction_vertical_angle=45,
            spread_angle=30,
            track_count=3,
            duration=0.8,
            lifetime=1.0
        )

    # --- Part 5: Ethereal Rework (00:00:48:22 - 00:01:12:22) ---
    # This entire section has been reworked based on user feedback.
    start_tick_p5 = end_tick_p4
    end_tick_p5 = timecode_to_tick("00:01:12:22")
    
    # Part 5: Melody fireworks (sparse, ambient)
    melody_indices_p5 = [0, 12, 24, 36, 48, 60, 72, 84, 96, 108, 120, 132]  # Sparse distribution
    colors_p5 = [
        ((200, 200, 255), (255, 255, 255)),  # Light blue to White
        ((255, 200, 255), (255, 255, 255)),  # Light pink to White
        ((200, 255, 255), (255, 255, 255)),  # Light cyan to White
    ]
    
    for idx, i in enumerate(melody_indices_p5):
        progress = i / 144  # Part 5 is roughly 144 units long
        tick = start_tick_p5 + round(progress * (end_tick_p5 - start_tick_p5))
        x = random.uniform(FIREWORK_X_RANGE[0], FIREWORK_X_RANGE[1])
        z = random.uniform(FIREWORK_Z_RANGE[0], FIREWORK_Z_RANGE[1])
        y = random.uniform(MELODY_Y_EXPLODE_MIN, MELODY_Y_EXPLODE_MAX)
        
        start_c, end_c = colors_p5[idx % 3]
        
        # Launch spark trajectory for melody firework (with tilt)
        x0 = x + random.uniform(-3, 3)
        z0 = z + random.uniform(-3, 3)
        firework_trajectories.launch_spark_trajectory(
            end_tick=tick,
            x0=x0, y0=-64, z0=z0,
            x1=x, y1=y, z1=z,
            duration=0.5,
            k=1.0, m0=8, lifetime=0.8, particle_count=2
        )
        
        basic_fireworks.clustered_firework(
            tick=tick, x=x, y=y, z=z,
            start_color=start_c, end_color=end_c,
            speed=18, horizontal_angle_step=90, vertical_angle_step=90,
            spread_angle=35, track_count=6,
            duration=1.5, lifetime=1.8
        )
    
    # Part 5a: "Rainbow Bridge" - Enhanced with color gradient
    rainbow_duration_ticks = end_tick_p5 - start_tick_p5
    num_rainbows = 20

    # Rainbow color spectrum (6 colors)
    rainbow_colors = [
        ((255, 0, 0), (255, 127, 0)),      # Red to Orange
        ((255, 127, 0), (255, 255, 0)),    # Orange to Yellow
        ((255, 255, 0), (0, 255, 0)),      # Yellow to Green
        ((0, 255, 0), (0, 127, 255)),      # Green to Cyan
        ((0, 127, 255), (75, 0, 130)),     # Cyan to Indigo
        ((75, 0, 130), (148, 0, 211))      # Indigo to Violet
    ]

    for i in range(num_rainbows):
        progress = i / (num_rainbows - 1)
        tick = start_tick_p5 + round(progress * rainbow_duration_ticks)

        y0 = FIREWORK_Y_BASE
        y1 = -10 # High arc peak

        # Corrected: Fixed X coordinate, motion is along Z axis
        x_pos = 970 # Fixed depth for all arcs

        if i % 2 == 0:
            # Left to Right Arc
            z0 = FIREWORK_Z_RANGE[1]
            z1 = FIREWORK_Z_RANGE[0]
        else:
            # Right to Left Arc
            z0 = FIREWORK_Z_RANGE[0]
            z1 = FIREWORK_Z_RANGE[1]

        # Select color based on progress through rainbow
        color_index = int(progress * len(rainbow_colors))
        color_index = min(color_index, len(rainbow_colors) - 1)
        start_color, end_color = rainbow_colors[color_index]

        firework_trajectories.launch_trajectory(
            end_tick=tick,
            x0=x_pos, y0=y0, z0=z0, 
            x1=x_pos, y1=y1, z1=z1, # Correct: x0 and x1 are the same
            start_color=start_color, end_color=end_color,
            duration=2.5,  # Reduced from 3.5 for faster motion
            k=0.5, m0=12, rho=3, lifetime=1.0  # Reduced from 8.0 to 1.0 second (20 ticks)
        )

    # Part 5b: "Aurora Fan" - Final correction for timing, count, and scale
    aurora_start_tick = start_tick_p5 + 240
    aurora_end_tick = end_tick_p5
    aurora_duration_ticks = aurora_end_tick - aurora_start_tick
    num_aurora_beams_per_fan = 40 # Increased count
    total_beams = num_aurora_beams_per_fan * 2
    
    # Define two separate arc centers for two fans
    arc_centers = [
        (1000, -15, -185), # Left fan center
        (1000, -15, -225)  # Right fan center
    ]
    arc_radius = 5 # Further reduced radius for a tighter fan
    
    # Symmetrical origins
    aurora_origins = [
        (975, FIREWORK_Z_RANGE[1] + 10), # Back-left
        (975, FIREWORK_Z_RANGE[0] - 10)  # Back-right
    ]

    for i in range(total_beams):
        # Determine which fan this beam belongs to
        fan_index = i % 2
        beam_index_in_fan = i // 2
        
        # Distribute ticks evenly for a continuous sweeping effect
        progress = i / (total_beams - 1)
        tick = aurora_start_tick + round(progress * aurora_duration_ticks)

        arc_center_x, arc_center_y, arc_center_z = arc_centers[fan_index]
        origin_x, origin_z = aurora_origins[fan_index]

        # Use a sine wave for smooth back-and-forth progress within each fan
        beam_progress = beam_index_in_fan / (num_aurora_beams_per_fan - 1)
        angle_progress = 0.5 * (1 - math.cos(beam_progress * 2 * math.pi)) # One full sweep

        # Calculate endpoint on the respective arc
        start_angle_deg = 160
        end_angle_deg = 20
        # Right fan sweeps in the opposite angular direction
        if fan_index == 1:
            start_angle_deg, end_angle_deg = end_angle_deg, start_angle_deg

        current_angle_deg = start_angle_deg + (end_angle_deg - start_angle_deg) * angle_progress
        current_angle_rad = math.radians(current_angle_deg)
        
        x1 = arc_center_x
        y1 = arc_center_y + arc_radius * math.sin(current_angle_rad)
        z1 = arc_center_z + arc_radius * math.cos(current_angle_rad)

        # Enhanced color palette: cycle through 4 colors
        aurora_colors = [
            ((180, 210, 255), (220, 180, 255)),  # Light blue to Purple
            ((255, 180, 210), (255, 220, 255)),  # Pink to Light pink
            ((180, 255, 210), (220, 255, 235)),  # Cyan-green to Light cyan
            ((220, 180, 255), (255, 200, 255)),  # Purple to Light purple
        ]
        color_idx = int((progress * 4) % 4)  # Cycle through 4 colors
        start_c, end_c = aurora_colors[color_idx]

        firework_trajectories.launch_trajectory(
            end_tick=tick,
            x0=origin_x, y0=FIREWORK_Y_BASE, z0=origin_z,
            x1=x1, y1=y1, z1=z1,
            start_color=start_c, end_color=end_c,
            duration=3.0,
            k=0.4, m0=10, rho=2, lifetime=1.5  # Reduced from 3.5 to 1.5
        )

    # --- Part 6: Climactic Section (00:01:12:22 - 00:01:36:22) ---
    # 16 measures, each character = 32nd note
    start_tick_p6 = end_tick_p5
    end_tick_p6 = timecode_to_tick("00:01:36:22")
    total_ticks_p6 = end_tick_p6 - start_tick_p6
    ticks_per_32nd_p6 = total_ticks_p6 / 256  # 16 measures × 16 32nd notes

    def get_tick_p6(note_index: int) -> int:
        return round(start_tick_p6 + note_index * ticks_per_32nd_p6)

    # Part 6: Melody fireworks (moderate frequency for climactic feel)
    melody_indices_p6 = [0, 16, 32, 48, 64, 80, 96, 112, 128, 144, 160, 176, 192, 208, 224, 240]
    colors_p6 = [
        ((255, 200, 200), (255, 255, 255)),  # Light red to White
        ((200, 255, 200), (255, 255, 255)),  # Light green to White
        ((200, 200, 255), (255, 255, 255)),  # Light blue to White
        ((255, 255, 200), (255, 255, 255)),  # Light yellow to White
    ]
    
    for idx, i in enumerate(melody_indices_p6):
        tick = get_tick_p6(i)
        x = random.uniform(FIREWORK_X_RANGE[0], FIREWORK_X_RANGE[1])
        z = random.uniform(FIREWORK_Z_RANGE[0], FIREWORK_Z_RANGE[1])
        y = random.uniform(MELODY_Y_EXPLODE_MIN, MELODY_Y_EXPLODE_MAX)
        
        start_c, end_c = colors_p6[idx % 4]
        
        # Launch spark trajectory for melody firework (with tilt)
        x0 = x + random.uniform(-3, 3)
        z0 = z + random.uniform(-3, 3)
        firework_trajectories.launch_spark_trajectory(
            end_tick=tick,
            x0=x0, y0=-64, z0=z0,
            x1=x, y1=y, z1=z,
            duration=0.5,
            k=1.0, m0=8, lifetime=0.8, particle_count=2
        )
        
        basic_fireworks.clustered_firework(
            tick=tick, x=x, y=y, z=z,
            start_color=start_c, end_color=end_c,
            speed=20, horizontal_angle_step=80, vertical_angle_step=80,
            spread_angle=30, track_count=7,
            duration=1.2, lifetime=1.5
        )

    # --- Kick Drum (16 measures, 32nd notes) ---
    kick_pattern_p6 = "1000001000000000" + "0000001010001010" + "1000001000000000" + "0000001010101000" + \
                      "1000001000000000" + "0000001010001010" + "1000001000000000" + "0000001010101000" + \
                      "1000001000000000" + "0000001010001010" + "1000001000000000" + "0000001010101000" + \
                      "1000001000000000" + "0000001010001010" + "1010101010101010" + "0000000000000000"
    
    kick_indices_p6 = [i for i, char in enumerate(kick_pattern_p6) if char == '1']
    
    # Reduce kick drum density to 1/2
    kick_indices_p6_reduced = kick_indices_p6[::2]  # Take every 2nd kick

    last_kick_pos_p6 = None
    for i in kick_indices_p6_reduced:
        tick = get_tick_p6(i)
        
        # Generate position with minimum distance check
        for _ in range(10):
            x0 = random.uniform(FIREWORK_X_RANGE[0], FIREWORK_X_RANGE[1])
            z0 = random.uniform(FIREWORK_Z_RANGE[0], FIREWORK_Z_RANGE[1])
            if last_kick_pos_p6 is None or ((x0 - last_kick_pos_p6[0])**2 + (z0 - last_kick_pos_p6[2])**2) > min_dist_sq:
                break
        
        y0 = FIREWORK_Y_BASE
        last_kick_pos_p6 = (x0, y0, z0)
        x1, y1, z1 = x0, random.uniform(DRUM_Y_EXPLODE_MIN, DRUM_Y_EXPLODE_MAX), z0
        
        basic_fireworks.expanding_sphere_firework(
            tick=tick, x=x1, y=y1, z=z1,
            start_color=(255, 0, 0), end_color=(255, 69, 0), # Red to OrangeRed
            radius=0.5,
            particle_count=80,
            radial_speed=1.0,
            lifetime=50
        )

    # --- Snare Drum Effects (16 measures, 32nd notes) ---
    snare_pattern_p6 = "1000001000001000" + "0010101010001011" + "1000001000001000" + "0010101010101000" + \
                       "1000001000001000" + "0010101010001011" + "1000001000001000" + "0010101010101000" + \
                       "1000101010001000" + "1010101010101011" + "1000101010001000" + "1010101010101010" + \
                       "1000101010001000" + "1010101010101011" + "1010101010101010" + "0000000000000000"

    # Find consecutive '1's for roll effects (真正相邻的1)
    def find_consecutive_ones(pattern):
        consecutive_groups = []
        i = 0
        while i < len(pattern):
            if pattern[i] == '1':
                start = i
                # 找连续的1，必须是相邻的
                while i + 1 < len(pattern) and pattern[i + 1] == '1':
                    i += 1
                # 如果找到了至少2个连续的1
                if i > start:  # i > start 意味着至少有2个连续的1
                    consecutive_groups.append((start, i))
                i += 1
            else:
                i += 1
        return consecutive_groups

    consecutive_groups = find_consecutive_ones(snare_pattern_p6)
    roll_indices = set()
    for start, end in consecutive_groups:
        for i in range(start, end + 1):
            roll_indices.add(i)

    # Process consecutive groups for roll effects (alternating directions)
    processed_groups = set()
    roll_index = 0
    for start, end in consecutive_groups:
        if start not in processed_groups:
            # Create alternating direction roll sweep effect for this group
            roll_start_tick = get_tick_p6(start)
            roll_end_tick = get_tick_p6(end + 1)  # Duration of the entire consecutive group
            roll_duration_ticks = roll_end_tick - roll_start_tick
            
            # Determine direction based on roll index
            # 0: L->R, 1: R->L, 2: L->R, 3: R->L
            left_to_right = (roll_index % 2 == 0)
            
            # Create 16 sweep fireworks for this roll - Doubled for denser effect
            sweep_count = 16  # Increased from 8
            for j in range(sweep_count):
                progress = j / (sweep_count - 1) if sweep_count > 1 else 0
                sweep_tick = roll_start_tick + round(progress * roll_duration_ticks)
                
                if left_to_right:
                    # Left to Right
                    z_pos = -165 + (-245 - (-165)) * progress
                    angle = -90
                else:
                    # Right to Left
                    z_pos = -245 + (-165 - (-245)) * progress
                    angle = 90
                
                basic_fireworks.directional_firework(
                    tick=sweep_tick,
                    x=995, y=FIREWORK_Y_BASE, z=z_pos,
                    start_color=(255, 255, 0), end_color=(255, 165, 0),  # Yellow to Orange
                    speed=24,
                    direction_horizontal_angle=angle,
                    direction_vertical_angle=45,
                    spread_angle=30,
                    track_count=3,
                    duration=0.8,
                    lifetime=1.0
                )
            
            processed_groups.add(start)
            roll_index += 1

    # Regular snare hits - full rhythm (no reduction)
    snare_indices_p6 = [i for i, char in enumerate(snare_pattern_p6) if char == '1']
    # No reduction - use all snare hits for expanding_sphere_firework (low performance impact)
    
    for i in snare_indices_p6:
        tick = get_tick_p6(i)
        x = random.uniform(FIREWORK_X_RANGE[0], FIREWORK_X_RANGE[1])
        z = random.uniform(FIREWORK_Z_RANGE[0], FIREWORK_Z_RANGE[1])
        y = random.uniform(DRUM_Y_EXPLODE_MIN, DRUM_Y_EXPLODE_MAX)
        
        basic_fireworks.expanding_sphere_firework(
            tick=tick, x=x, y=y, z=z,
            start_color=(255, 255, 0), end_color=(255, 215, 0),  # Yellow to Gold
            radius=0.5,
            particle_count=80,
            radial_speed=0.7,  # Slightly smaller than kick drum (1.0)
            lifetime=45
        )

    # --- Climactic Finale Firework Launch ---
    # Launch at measure 16, beat 1 (index 240), explode at start of Part 7
    launch_tick = get_tick_p6(240)  # Measure 16, beat 1 (16×16-16 = 240)
    
    # Calculate Part 7 start time for explosion timing
    part7_start_tick = end_tick_p6  # This will be the explosion time
    trajectory_duration = (part7_start_tick - launch_tick) / 20.0  # Convert to seconds
    
    # Launch position (behind the main stage area)
    launch_x = 960  # Slightly back from stage center
    launch_z = -225  # Back area
    launch_y = FIREWORK_Y_BASE
    
    # Explosion position (front-center facing audience)
    explode_x = 970  # Stage center
    explode_z = -205  # Front-center facing audience  
    explode_y = -20   # High explosion height
    
    # Launch trajectory that will explode at Part 7 start
    firework_trajectories.launch_spark_trajectory(
        end_tick=part7_start_tick,  # Explode at Part 7 start
        x0=launch_x, y0=launch_y, z0=launch_z,
        x1=explode_x, y1=explode_y, z1=explode_z,
        duration=trajectory_duration,
        k=0.8, m0=12, lifetime=2.0, particle_count=3
    )

    # --- Part 7 Opening: Finale Firework Explosion ---
    # This explosion occurs at the start of Part 7, triggered by the trajectory launched in Part 6
    explosion_tick = part7_start_tick
    
    # Multi-layered explosion effect at the trajectory endpoint
    # Layer 1: Massive central clustered firework (Orange-red to Orange)
    basic_fireworks.clustered_firework(
        tick=explosion_tick,
        x=explode_x, y=explode_y, z=explode_z,
        start_color=(255, 80, 0), end_color=(255, 150, 0),  # Orange-red to Orange
        speed=35,
        horizontal_angle_step=30, vertical_angle_step=30,
        spread_angle=35,
        track_count=6,  # Reduced from 12 to 6
        duration=2.5,
        lifetime=5.25  # 增加1.5倍：3.5 × 1.5 = 5.25
    )
    
    # Layer 2: Outer ring explosion (Orange to Golden yellow)
    basic_fireworks.clustered_firework(
        tick=explosion_tick + 3,  # Slight delay for layered effect
        x=explode_x, y=explode_y, z=explode_z,
        start_color=(255, 150, 0), end_color=(255, 220, 0),  # Orange to Golden yellow
        speed=28,
        horizontal_angle_step=40, vertical_angle_step=40,
        spread_angle=40,
        track_count=5,  # Reduced from 10 to 5
        duration=2.0,
        lifetime=4.5  # 增加1.5倍：3.0 × 1.5 = 4.5
    )
    
    # Layer 3: Golden finale (Golden yellow to Light yellow)
    basic_fireworks.clustered_firework(
        tick=explosion_tick + 8,  # Further delay for crescendo effect
        x=explode_x, y=explode_y + 5, z=explode_z,
        start_color=(255, 220, 0), end_color=(255, 255, 180),  # Golden yellow to Light yellow
        speed=25,
        horizontal_angle_step=45, vertical_angle_step=45,
        spread_angle=30,
        track_count=4,  # Reduced from 8 to 4
        duration=1.8,
        lifetime=3.75  # 增加1.5倍：2.5 × 1.5 = 3.75
    )

    # --- Part 7 Main: Climax Section (00:01:36:22 - 00:02:00:22) ---
    # 8 measures, highest energy section with dense fireworks
    part7_end_tick = timecode_to_tick("00:02:00:22")
    duration_p7 = (part7_end_tick - part7_start_tick) / 20.0
    ticks_per_16th_p7 = (part7_end_tick - part7_start_tick) / 128  # 8 measures × 16 notes
    
    def get_tick_p7(note_index: int) -> int:
        return round(part7_start_tick + note_index * ticks_per_16th_p7)
    
    # --- Kick Drum (Part 7) ---
    kick_pattern_p7 = ("1001001000100001" * 7) + "1001001000100000"
    kick_indices_p7 = [i for i, char in enumerate(kick_pattern_p7) if char == '1']
    for i in kick_indices_p7:
        tick = get_tick_p7(i)
        x = random.uniform(FIREWORK_X_RANGE[0], FIREWORK_X_RANGE[1])
        z = random.uniform(FIREWORK_Z_RANGE[0], FIREWORK_Z_RANGE[1])
        y = random.uniform(DRUM_Y_EXPLODE_MIN, DRUM_Y_EXPLODE_MAX)
        
        basic_fireworks.expanding_sphere_firework(
            tick=tick, x=x, y=y, z=z,
            start_color=(255, 69, 0), end_color=(255, 140, 0),  # Orange-red to Dark orange
            radius=0.5, particle_count=80, radial_speed=1.0, lifetime=50
        )
    
    # --- Melody (Part 7) ---
    melody_pattern_p7 = ("1101101101110100" * 3) + "1011101101101000" + \
                        ("1101101101110100" * 3) + "1011101101101000"
    melody_indices_p7 = [i for i, char in enumerate(melody_pattern_p7) if char == '1']
    
    for i in melody_indices_p7:
        tick = get_tick_p7(i)
        x = random.uniform(FIREWORK_X_RANGE[0], FIREWORK_X_RANGE[1])
        z = random.uniform(FIREWORK_Z_RANGE[0], FIREWORK_Z_RANGE[1])
        y = random.uniform(MELODY_Y_EXPLODE_MIN, MELODY_Y_EXPLODE_MAX)
        
        # Launch spark trajectory for melody firework
        x0 = x + random.uniform(-3, 3)
        z0 = z + random.uniform(-3, 3)
        firework_trajectories.launch_spark_trajectory(
            end_tick=tick,
            x0=x0, y0=-64, z0=z0,
            x1=x, y1=y, z1=z,
            duration=0.5,
            k=1.0, m0=8, lifetime=0.8, particle_count=2
        )
        
        # Clustered firework (golden to white)
        basic_fireworks.clustered_firework(
            tick=tick, x=x, y=y, z=z,
            start_color=(255, 215, 0), end_color=(255, 255, 255),  # Golden to White
            speed=18,
            horizontal_angle_step=45, vertical_angle_step=45,
            spread_angle=25,
            track_count=4,
            duration=1.2, lifetime=1.5
        )
    
    # --- Vocals (Part 7) ---
    vocal_pattern_p7 = ("0000000001110100" * 7) + "0000000000000000"
    vocal_indices_p7 = [i for i, char in enumerate(vocal_pattern_p7) if char == '1']
    
    for i in vocal_indices_p7:
        tick = get_tick_p7(i)
        x = random.uniform(FIREWORK_X_RANGE[0], FIREWORK_X_RANGE[1])
        z = random.uniform(FIREWORK_Z_RANGE[0], FIREWORK_Z_RANGE[1])
        y = random.uniform(MELODY_Y_EXPLODE_MIN, MELODY_Y_EXPLODE_MAX)
        
        # Launch spark trajectory for vocal firework
        x0 = x + random.uniform(-3, 3)
        z0 = z + random.uniform(-3, 3)
        firework_trajectories.launch_spark_trajectory(
            end_tick=tick,
            x0=x0, y0=-64, z0=z0,
            x1=x, y1=y, z1=z,
            duration=0.5,
            k=1.0, m0=8, lifetime=0.8, particle_count=2
        )
        
        # Clustered firework (deep red to golden)
        basic_fireworks.clustered_firework(
            tick=tick, x=x, y=y, z=z,
            start_color=(220, 20, 60), end_color=(255, 215, 0),  # Deep red to Golden
            speed=18,
            horizontal_angle_step=45, vertical_angle_step=45,
            spread_angle=25,
            track_count=4,
            duration=1.2, lifetime=1.5
        )
    
    # --- Special Roll Effect at Measure 4 End (Index 63) ---
    roll_tick = get_tick_p7(63)
    for j in range(16):  # 16 dense directional fireworks
        sub_tick = roll_tick + j
        x = random.uniform(FIREWORK_X_RANGE[0], FIREWORK_X_RANGE[1])
        z = random.uniform(FIREWORK_Z_RANGE[0], FIREWORK_Z_RANGE[1])
        y = random.uniform(DRUM_Y_EXPLODE_MIN, DRUM_Y_EXPLODE_MAX)
        
        basic_fireworks.directional_firework(
            tick=sub_tick, x=x, y=y, z=z,
            start_color=(255, 215, 0), end_color=(255, 165, 0),  # Yellow to Orange
            speed=20,
            direction_horizontal_angle=90,
            direction_vertical_angle=45,
            spread_angle=30,
            track_count=3,
            duration=0.8,
            lifetime=1.0
        )

    # --- Part 8: Quiet Transition (00:02:00:22 - 00:02:12:22) ---
    # 4 measures, soft and airy with creative firework combinations
    part8_start_tick = timecode_to_tick("00:02:00:22")
    part8_end_tick = timecode_to_tick("00:02:12:22")
    duration_p8 = (part8_end_tick - part8_start_tick) / 20.0
    ticks_per_16th_p8 = (part8_end_tick - part8_start_tick) / 64  # 4 measures × 16 notes
    
    def get_tick_p8(note_index: int) -> int:
        return round(part8_start_tick + note_index * ticks_per_16th_p8)
    
    # --- Vocals (Part 8) ---
    vocal_pattern_p8 = ("0111010001110011" + "1011110011111000") * 2
    vocal_indices_p8 = [i for i, char in enumerate(vocal_pattern_p8) if char == '1']
    
    for i in vocal_indices_p8:
        tick = get_tick_p8(i)
        x = random.uniform(FIREWORK_X_RANGE[0], FIREWORK_X_RANGE[1])
        z = random.uniform(FIREWORK_Z_RANGE[0], FIREWORK_Z_RANGE[1])
        y = random.uniform(MELODY_Y_EXPLODE_MIN, MELODY_Y_EXPLODE_MAX)
        
        # Small clustered firework (lavender to white)
        basic_fireworks.clustered_firework(
            tick=tick, x=x, y=y, z=z,
            start_color=(200, 162, 200), end_color=(255, 255, 255),  # Lavender to White
            speed=12,
            horizontal_angle_step=60, vertical_angle_step=60,
            spread_angle=20,
            track_count=3,
            duration=1.0, lifetime=1.3
        )
        
        # Halo effect using expanding sphere (light purple to white)
        basic_fireworks.expanding_sphere_firework(
            tick=tick + 5, x=x, y=y, z=z,
            start_color=(220, 200, 255), end_color=(255, 255, 255),  # Light purple to White
            radius=0.4, particle_count=60, radial_speed=0.5, lifetime=25
        )
    
    # --- Guitar (Part 8) ---
    guitar_pattern_p8 = ("0010010010010011" * 3) + "0010010010010000"
    guitar_indices_p8 = [i for i, char in enumerate(guitar_pattern_p8) if char == '1']
    
    for idx, i in enumerate(guitar_indices_p8):
        tick = get_tick_p8(i)
        x = random.uniform(FIREWORK_X_RANGE[0], FIREWORK_X_RANGE[1])
        z = random.uniform(FIREWORK_Z_RANGE[0], FIREWORK_Z_RANGE[1])
        y = random.uniform(MELODY_Y_EXPLODE_MIN, MELODY_Y_EXPLODE_MAX)
        
        # Double layer firework (pink to light yellow)
        basic_fireworks.basic_double_layer_firework(
            tick=tick, x=x, y=y, z=z,
            inner_start_color=(255, 182, 193), inner_end_color=(255, 255, 255),  # Inner: Pink to White
            outer_start_color=(255, 182, 193), outer_end_color=(255, 250, 205),  # Outer: Pink to Light yellow
            inner_speed=10, outer_speed=15,
            outer_horizontal_angle_step=45, outer_vertical_angle_step=45,
            duration=1.0, lifetime=1.2
        )
        
        # Optional directional accent (every other note for variety)
        if idx % 2 == 0:
            basic_fireworks.directional_firework(
                tick=tick + 3, x=x, y=y, z=z,
                start_color=(255, 218, 185), end_color=(255, 255, 224),  # Peach to Light yellow
                speed=10,
                direction_horizontal_angle=random.uniform(60, 120),
                direction_vertical_angle=30,  # Upward tilt
                spread_angle=20,
                track_count=2,
                duration=0.6, lifetime=0.8
            )
    
    # --- Breath Effect at Measure Starts (Ambient) ---
    breath_indices = [0, 16, 32, 48]
    
    for i in breath_indices:
        tick = get_tick_p8(i)
        x = random.uniform(FIREWORK_X_RANGE[0], FIREWORK_X_RANGE[1])
        z = random.uniform(FIREWORK_Z_RANGE[0], FIREWORK_Z_RANGE[1])
        y = random.uniform(MELODY_Y_EXPLODE_MIN, MELODY_Y_EXPLODE_MAX)
        
        # Large slow expanding sphere (like a breath)
        basic_fireworks.expanding_sphere_firework(
            tick=tick, x=x, y=y, z=z,
            start_color=(173, 216, 230), end_color=(240, 248, 255),  # Light blue to Alice blue
            radius=0.6, particle_count=80, radial_speed=0.3, lifetime=40  # Very slow expansion
        )
    
    # --- Bass Pickup Notes at the End (Indices 62-63) ---
    bass_pickup_indices = [62, 63]
    
    for i in bass_pickup_indices:
        tick = get_tick_p8(i)
        x = random.uniform(FIREWORK_X_RANGE[0], FIREWORK_X_RANGE[1])
        z = random.uniform(FIREWORK_Z_RANGE[0], FIREWORK_Z_RANGE[1])
        y_start = FIREWORK_Y_BASE
        y_end = random.uniform(MELODY_Y_EXPLODE_MIN, MELODY_Y_EXPLODE_MAX)
        
        # Rising spark trajectory (quick and urgent)
        firework_trajectories.launch_spark_trajectory(
            end_tick=tick,
            x0=x, y0=y_start, z0=z,
            x1=x, y1=y_end, z1=z,
            duration=0.4,  # Quick rise
            k=1.0, m0=8, lifetime=0.6, particle_count=3
        )
        
        # Expanding sphere at the top (deep purple to magenta - foreshadowing)
        basic_fireworks.expanding_sphere_firework(
            tick=tick, x=x, y=y_end, z=z,
            start_color=(75, 0, 130), end_color=(255, 20, 147),  # Indigo to Deep pink
            radius=0.3, particle_count=50, radial_speed=0.8, lifetime=30
        )

    # --- Part 9: Similar to Part 3/4 but with variations (00:02:12:22 - 00:02:36:22) ---
    # 8 measures, upbeat and energetic, user's favorite section
    part9_start_tick = timecode_to_tick("00:02:12:22")
    part9_end_tick = timecode_to_tick("00:02:36:22")
    duration_p9 = (part9_end_tick - part9_start_tick) / 20.0
    ticks_per_16th_p9 = (part9_end_tick - part9_start_tick) / 128  # 8 measures × 16 notes
    
    def get_tick_p9(note_index: int) -> int:
        return round(part9_start_tick + note_index * ticks_per_16th_p9)
    
    # --- Kick Drum (Part 9) ---
    kick_pattern_p9 = "1010000001100001" * 7 + "1010000001100000"
    kick_indices_p9 = [i for i, char in enumerate(kick_pattern_p9) if char == '1']
    
    for i in kick_indices_p9:
        tick = get_tick_p9(i)
        x = random.uniform(FIREWORK_X_RANGE[0], FIREWORK_X_RANGE[1])
        z = random.uniform(FIREWORK_Z_RANGE[0], FIREWORK_Z_RANGE[1])
        y = random.uniform(DRUM_Y_EXPLODE_MIN, DRUM_Y_EXPLODE_MAX)
        
        basic_fireworks.expanding_sphere_firework(
            tick=tick, x=x, y=y, z=z,
            start_color=(255, 69, 0), end_color=(255, 140, 0),  # Orange-red to Dark orange
            radius=1.0,
            particle_count=50,
            radial_speed=1.0,  # Consistent with other kick drums
            lifetime=24
        )
    
    # --- Snare Drum (Part 9) ---
    snare_pattern_p9 = "0000100000001000" * 8
    snare_indices_p9 = [i for i, char in enumerate(snare_pattern_p9) if char == '1']
    
    for i in snare_indices_p9:
        tick = get_tick_p9(i)
        x = random.uniform(FIREWORK_X_RANGE[0], FIREWORK_X_RANGE[1])
        z = random.uniform(FIREWORK_Z_RANGE[0], FIREWORK_Z_RANGE[1])
        y = random.uniform(DRUM_Y_EXPLODE_MIN, DRUM_Y_EXPLODE_MAX)
        
        basic_fireworks.clustered_firework(
            tick=tick, x=x, y=y, z=z,
            start_color=(255, 255, 0), end_color=(255, 200, 0),  # Yellow to Orange-yellow
            speed=18,
            horizontal_angle_step=60, vertical_angle_step=60,
            spread_angle=25,
            track_count=4,
            duration=1.0, lifetime=1.2
        )
    
    # --- Vocals (Part 9) ---
    vocal_pattern_p9 = ("0010010010010010" + "0010001000000010" + 
                        "1001001001001111" + "0000000000000000" +
                        "0011111111111011" + "1011001000000010" + 
                        "1001001001001100" + "0000000000000000")
    vocal_indices_p9 = [i for i, char in enumerate(vocal_pattern_p9) if char == '1']
    
    # Special section: indices 64-79 (user's favorite line)
    special_section_start = 64
    special_section_end = 79
    
    for i in vocal_indices_p9:
        tick = get_tick_p9(i)
        
        # Check if in special section
        if special_section_start <= i <= special_section_end:
            # Wave sequence: y-coordinate varies smoothly
            wave_progress = (i - special_section_start) / (special_section_end - special_section_start)
            
            # Create wave pattern in x-z plane
            center_x = (FIREWORK_X_RANGE[0] + FIREWORK_X_RANGE[1]) / 2
            center_z = (FIREWORK_Z_RANGE[0] + FIREWORK_Z_RANGE[1]) / 2
            offset = 6.0 * math.sin(wave_progress * math.pi * 2)  # Sinusoidal wave
            
            x = center_x + offset
            z = center_z + offset * 0.5  # Elliptical pattern
            
            # Y varies smoothly up and down
            y_base = (MELODY_Y_EXPLODE_MIN + MELODY_Y_EXPLODE_MAX) / 2
            y = y_base + 5.0 * math.sin(wave_progress * math.pi * 3)  # 3 waves across the section
            
            # Special colors for favorite section
            basic_fireworks.clustered_firework(
                tick=tick, x=x, y=y, z=z,
                start_color=(255, 105, 180), end_color=(255, 215, 0),  # Pink to Gold
                speed=15,
                horizontal_angle_step=60, vertical_angle_step=60,
                spread_angle=20,
                track_count=4,
                duration=1.5, lifetime=1.8
            )
            
            # Add spark trajectory
            x0_offset = random.uniform(-2, 2)
            z0_offset = random.uniform(-2, 2)
            firework_trajectories.launch_spark_trajectory(
                end_tick=tick,
                x0=x + x0_offset, y0=-64, z0=z + z0_offset,
                x1=x, y1=y, z1=z,
                duration=1.2,
                k=1.0, m0=8, lifetime=0.6, particle_count=3
            )
        else:
            # Normal vocals
            x = random.uniform(FIREWORK_X_RANGE[0], FIREWORK_X_RANGE[1])
            z = random.uniform(FIREWORK_Z_RANGE[0], FIREWORK_Z_RANGE[1])
            y = random.uniform(MELODY_Y_EXPLODE_MIN, MELODY_Y_EXPLODE_MAX)
            
            basic_fireworks.clustered_firework(
                tick=tick, x=x, y=y, z=z,
                start_color=(255, 215, 0), end_color=(255, 165, 0),  # Gold to Bright orange
                speed=15,
                horizontal_angle_step=60, vertical_angle_step=60,
                spread_angle=20,
                track_count=3,
                duration=1.5, lifetime=1.8
            )
            
            # Add spark trajectory
            x0_offset = random.uniform(-2, 2)
            z0_offset = random.uniform(-2, 2)
            firework_trajectories.launch_spark_trajectory(
                end_tick=tick,
                x0=x + x0_offset, y0=-64, z0=z + z0_offset,
                x1=x, y1=y, z1=z,
                duration=1.2,
                k=1.0, m0=8, lifetime=0.6, particle_count=3
            )
    
    # --- Corner Pillar Sequence (sync with snare drum) ---
    # Use the same timing as snare drum
    corner_pillar_indices = snare_indices_p9
    
    # Define 4 corners of the firework field
    corner_positions = [
        (FIREWORK_X_RANGE[0], FIREWORK_Z_RANGE[0]),  # SW corner
        (FIREWORK_X_RANGE[0], FIREWORK_Z_RANGE[1]),  # NW corner
        (FIREWORK_X_RANGE[1], FIREWORK_Z_RANGE[0]),  # SE corner
        (FIREWORK_X_RANGE[1], FIREWORK_Z_RANGE[1])   # NE corner
    ]
    
    for i in corner_pillar_indices:
        tick = get_tick_p9(i)
        y_center = -35  # Center position for vertical expansion
        
        # Pillar effect: particles expand vertically from center
        for corner_x, corner_z in corner_positions:
            # Generate ~100 particles per corner
            for _ in range(100):
                # Random position within diameter 2 circle (radius 1.0)
                angle = random.uniform(0, 2 * math.pi)
                radius = random.uniform(0, 1.0)
                x_offset = radius * math.cos(angle)
                z_offset = radius * math.sin(angle)
                
                x = corner_x + x_offset
                z = corner_z + z_offset
                y = y_center
                
                # Random vertical velocity (0-5 range, both up and down)
                vy = random.uniform(0, 5) * random.choice([-1, 1])
                
                # Minimal horizontal velocity (keep pillar shape)
                vx = 0
                vz = 0
                
                # Generate particle with vertical velocity (purple color)
                shared_functions.add_velocity_firework_command(
                    tick=tick, x=x, y=y, z=z,
                    start_color=(138, 43, 226), end_color=(186, 85, 211),  # Blue-violet to Medium orchid
                    vx=vx, vy=vy, vz=vz,
                    lifetime=40  # ~2 seconds to show expansion
                )

    # --- Part 10: Ethereal Spiral (00:02:36:22 - 00:03:00:22) ---
    # 8 measures, similar melody to Part 5 but with spiral visual theme
    part10_start_tick = timecode_to_tick("00:02:36:22")
    part10_end_tick = timecode_to_tick("00:03:00:22")
    duration_p10 = (part10_end_tick - part10_start_tick) / 20.0
    
    # Melody fireworks (sparse, 12 notes like Part 5)
    melody_indices_p10 = [0, 12, 24, 36, 48, 60, 72, 84, 96, 108, 120, 132]
    colors_p10 = [
        ((200, 220, 255), (255, 255, 255)),  # Light blue to White
        ((220, 200, 255), (255, 255, 255)),  # Light purple to White
        ((200, 255, 255), (255, 255, 255)),  # Light cyan to White
    ]
    
    # Center position for spiral
    center_x = (FIREWORK_X_RANGE[0] + FIREWORK_X_RANGE[1]) / 2
    center_z = (FIREWORK_Z_RANGE[0] + FIREWORK_Z_RANGE[1]) / 2
    
    for idx, i in enumerate(melody_indices_p10):
        progress = i / 144
        tick = part10_start_tick + round(progress * (part10_end_tick - part10_start_tick))
        
        # Spiral position: outward and upward
        spiral_angle = progress * 4 * math.pi  # 2 full rotations
        spiral_radius = 5 + progress * 10  # Expanding radius
        x = center_x + spiral_radius * math.cos(spiral_angle)
        z = center_z + spiral_radius * math.sin(spiral_angle)
        y = MELODY_Y_EXPLODE_MIN + progress * (MELODY_Y_EXPLODE_MAX - MELODY_Y_EXPLODE_MIN)
        
        start_c, end_c = colors_p10[idx % 3]
        
        # Launch spark trajectory for melody firework
        x0 = x + random.uniform(-2, 2)
        z0 = z + random.uniform(-2, 2)
        firework_trajectories.launch_spark_trajectory(
            end_tick=tick,
            x0=x0, y0=-64, z0=z0,
            x1=x, y1=y, z1=z,
            duration=0.6,
            k=1.0, m0=8, lifetime=0.8, particle_count=2
        )
        
        # Double layer firework for dreamlike effect
        basic_fireworks.basic_double_layer_firework(
            tick=tick, x=x, y=y, z=z,
            inner_start_color=start_c, inner_end_color=end_c,
            outer_start_color=start_c, outer_end_color=end_c,
            inner_speed=12, outer_speed=18,
            outer_horizontal_angle_step=60, outer_vertical_angle_step=60,
            duration=1.5, lifetime=1.8
        )
    
    # Spiral Ribbons (DNA double helix effect)
    spiral_duration_ticks = part10_end_tick - part10_start_tick
    
    special_effects.double_helix_spiral(
        start_tick=part10_start_tick,
        duration_ticks=spiral_duration_ticks,
        center_x=center_x,
        center_z=center_z,
        base_y=-45,  # Fixed height near ground
        helix_radius=8,
        rise_speed=0.0,  # No rise, particles spawn at same height
        rotation_speed=0.1,  # Rotation speed in radians per tick
        particle_density=2,  # 2 particles per helix per tick
        vertical_velocity_range=(0.5, 1.5),  # Random upward velocity
        lifetime=40,
        color1=((100, 180, 255), (150, 220, 255)),  # Blue helix
        color2=((180, 150, 255), (220, 180, 255))   # Purple helix
    )
    
    # Rotating Ring with Dispersion (horizontal torus)
    ring_duration_ticks = part10_end_tick - part10_start_tick
    ring_y = -60  # Lower position near ground
    
    special_effects.rotating_ring_with_dispersion(
        start_tick=part10_start_tick,
        duration_ticks=ring_duration_ticks,
        center_x=center_x,
        center_y=ring_y,
        center_z=center_z,
        ring_radius=15,  # Larger major radius for better visibility
        tube_radius=1.0,  # Minor radius (thickness of tube)
        rotation_speed=0.15,  # Faster rotation for visible effect
        particle_density=4,  # 4 particles per tick
        radial_velocity=0.5,  # Slower outward dispersion velocity
        lifetime=40,  # Longer lifetime
        start_color=(150, 220, 255),  # Light cyan
        end_color=(255, 255, 255)     # White
    )

    # --- Part 11: Edge Light Walls (00:03:00:22 - 00:03:24:22) ---
    # 16 measures, same as Part 6 but with edge lighting and center focus
    part11_start_tick = timecode_to_tick("00:03:00:22")
    part11_end_tick = timecode_to_tick("00:03:24:22")
    total_ticks_p11 = part11_end_tick - part11_start_tick
    ticks_per_32nd_p11 = total_ticks_p11 / 256  # 16 measures × 16 32nd notes per measure
    
    def get_tick_p11(note_index: int) -> int:
        return round(part11_start_tick + note_index * ticks_per_32nd_p11)
    
    # Center position for focused effects
    center_x_p11 = (FIREWORK_X_RANGE[0] + FIREWORK_X_RANGE[1]) / 2
    center_z_p11 = (FIREWORK_Z_RANGE[0] + FIREWORK_Z_RANGE[1]) / 2
    focus_radius = 10  # Focused area around center
    
    # --- Melody Fireworks (16 notes, center focused with warm colors) ---
    melody_indices_p11 = [0, 16, 32, 48, 64, 80, 96, 112, 128, 144, 160, 176, 192, 208, 224, 240]
    colors_p11 = [
        ((255, 200, 150), (255, 255, 255)),  # Warm orange to White
        ((255, 215, 0), (255, 255, 255)),    # Gold to White
        ((255, 182, 193), (255, 255, 255)),  # Pink to White
        ((200, 150, 255), (255, 255, 255)),  # Purple to White
    ]
    
    for idx, i in enumerate(melody_indices_p11):
        tick = get_tick_p11(i)
        
        # Center-focused position
        angle = random.uniform(0, 2 * math.pi)
        radius = random.uniform(0, focus_radius)
        x = center_x_p11 + radius * math.cos(angle)
        z = center_z_p11 + radius * math.sin(angle)
        y = random.uniform(MELODY_Y_EXPLODE_MIN, MELODY_Y_EXPLODE_MAX)
        
        start_c, end_c = colors_p11[idx % 4]
        
        # Launch spark trajectory
        x0 = x + random.uniform(-2, 2)
        z0 = z + random.uniform(-2, 2)
        firework_trajectories.launch_spark_trajectory(
            end_tick=tick,
            x0=x0, y0=-64, z0=z0,
            x1=x, y1=y, z1=z,
            duration=0.5,
            k=1.0, m0=8, lifetime=0.8, particle_count=2
        )
        
        basic_fireworks.clustered_firework(
            tick=tick, x=x, y=y, z=z,
            start_color=start_c, end_color=end_c,
            speed=20, horizontal_angle_step=80, vertical_angle_step=80,
            spread_angle=30, track_count=7,
            duration=1.2, lifetime=1.5
        )
    
    # --- Edge Light Walls (pulse trigger every 2 measures) ---
    # Define edge positions (every 5 blocks along each edge)
    edge_north = [(x, FIREWORK_Z_RANGE[1]) for x in range(int(FIREWORK_X_RANGE[0]), int(FIREWORK_X_RANGE[1])+1, 5)]
    edge_south = [(x, FIREWORK_Z_RANGE[0]) for x in range(int(FIREWORK_X_RANGE[0]), int(FIREWORK_X_RANGE[1])+1, 5)]
    edge_east = [(FIREWORK_X_RANGE[1], z) for z in range(int(FIREWORK_Z_RANGE[0]), int(FIREWORK_Z_RANGE[1])+1, 5)]
    edge_west = [(FIREWORK_X_RANGE[0], z) for z in range(int(FIREWORK_Z_RANGE[0]), int(FIREWORK_Z_RANGE[1])+1, 5)]
    
    # First pulse (measure 0): Full cyan light walls on all 4 edges
    tick_m0 = get_tick_p11(0)
    all_edges = edge_north + edge_south + edge_east + edge_west
    for x, z in all_edges:
        for y_idx in range(3):
            y = MELODY_Y_EXPLODE_MIN + y_idx * 8
            
            basic_fireworks.expanding_sphere_firework(
                tick=tick_m0, x=x, y=y, z=z,
                start_color=(100, 200, 255), end_color=(255, 255, 255),  # Cool cyan to White
                radius=0.5,
                particle_count=30,
                radial_speed=0.5,
                lifetime=30
            )
    
    # Remaining pulses (measures 2, 4, 6, 8, 10, 12, 14): Purple pillars on front/back sides only
    side_pulse_measures = [2, 4, 6, 8, 10, 12, 14]
    # Extend positions 10 blocks outward from edges
    front_back_edges_extended = []
    for x in range(int(FIREWORK_X_RANGE[0]), int(FIREWORK_X_RANGE[1])+1, 5):
        front_back_edges_extended.append((x, FIREWORK_Z_RANGE[1] + 10))  # North side, extended outward
        front_back_edges_extended.append((x, FIREWORK_Z_RANGE[0] - 10))  # South side, extended outward
    
    for measure in side_pulse_measures:
        tick = get_tick_p11(measure * 16)
        
        for x, z in front_back_edges_extended:
            # Purple pillar (similar to Part 9 design)
            for _ in range(100):
                # Random position within diameter 2 circle (radius 1.0)
                angle = random.uniform(0, 2 * math.pi)
                radius = random.uniform(0, 1.0)
                x_offset = radius * math.cos(angle)
                z_offset = radius * math.sin(angle)
                
                x_pos = x + x_offset
                z_pos = z + z_offset
                y_pos = -35  # Center position
                
                # Random vertical velocity (0-5 range, both up and down)
                vy = random.uniform(0, 5) * random.choice([-1, 1])
                vx = 0
                vz = 0
                
                # Generate particle with vertical velocity (purple color)
                shared_functions.add_velocity_firework_command(
                    tick=tick, x=x_pos, y=y_pos, z=z_pos,
                    start_color=(138, 43, 226), end_color=(186, 85, 211),  # Blue-violet to Medium orchid
                    vx=vx, vy=vy, vz=vz,
                    lifetime=40
                )
    
    # --- Kick Drum (16 measures, same as Part 6 pattern, 32nd notes) ---
    kick_pattern_p11 = "1000001000000000" + "0000001010001010" + "1000001000000000" + "0000001010101000" + \
                       "1000001000000000" + "0000001010001010" + "1000001000000000" + "0000001010101000" + \
                       "1000001000000000" + "0000001010001010" + "1000001000000000" + "0000001010101000" + \
                       "1000001000000000" + "0000001010001010" + "1010101010101010" + "0000000000000000"
    kick_indices_p11 = [i for i, char in enumerate(kick_pattern_p11) if char == '1']
    # No density reduction - use full rhythm
    
    last_kick_pos_p11 = None
    for i in kick_indices_p11:
        tick = get_tick_p11(i)
        
        # Generate position with minimum distance check
        for _ in range(10):
            x0 = random.uniform(FIREWORK_X_RANGE[0], FIREWORK_X_RANGE[1])
            z0 = random.uniform(FIREWORK_Z_RANGE[0], FIREWORK_Z_RANGE[1])
            if last_kick_pos_p11 is None or ((x0 - last_kick_pos_p11[0])**2 + (z0 - last_kick_pos_p11[2])**2) > min_dist_sq:
                break
        
        y0 = FIREWORK_Y_BASE
        last_kick_pos_p11 = (x0, y0, z0)
        x1, y1, z1 = x0, random.uniform(DRUM_Y_EXPLODE_MIN, DRUM_Y_EXPLODE_MAX), z0
        
        basic_fireworks.expanding_sphere_firework(
            tick=tick, x=x1, y=y1, z=z1,
            start_color=(255, 69, 0), end_color=(255, 140, 0),  # Brighter orange tones
            radius=1.0,
            particle_count=50,
            radial_speed=1.0,
            lifetime=24
        )
    
    # --- Snare Drum Effects (16 measures, same as Part 6 pattern, 32nd notes) ---
    snare_pattern_p11 = "1000001000001000" + "0010101010001011" + "1000001000001000" + "0010101010101000" + \
                        "1000001000001000" + "0010101010001011" + "1000001000001000" + "0010101010101000" + \
                        "1000101010001000" + "1010101010101011" + "1000101010001000" + "1010101010101010" + \
                        "1000101010001000" + "1010101010101011" + "1010101010101010" + "0000000000000000"
    
    # Find consecutive '1's for roll effects (extra directional sweep)
    consecutive_groups_p11 = find_consecutive_ones(snare_pattern_p11)
    
    # Process roll effects (add directional sweep for rolls)
    processed_groups_p11 = set()
    roll_index_p11 = 0
    for start, end in consecutive_groups_p11:
        if start not in processed_groups_p11:
            roll_start_tick = get_tick_p11(start)
            roll_end_tick = get_tick_p11(end + 1)
            roll_duration_ticks = roll_end_tick - roll_start_tick
            
            left_to_right = (roll_index_p11 % 2 == 0)
            
            sweep_count = 16
            for j in range(sweep_count):
                progress = j / (sweep_count - 1) if sweep_count > 1 else 0
                sweep_tick = roll_start_tick + round(progress * roll_duration_ticks)
                
                if left_to_right:
                    z_pos = FIREWORK_Z_RANGE[1] + (FIREWORK_Z_RANGE[0] - FIREWORK_Z_RANGE[1]) * progress
                    angle = -90
                else:
                    z_pos = FIREWORK_Z_RANGE[0] + (FIREWORK_Z_RANGE[1] - FIREWORK_Z_RANGE[0]) * progress
                    angle = 90
                
                basic_fireworks.directional_firework(
                    tick=sweep_tick,
                    x=center_x_p11, y=FIREWORK_Y_BASE, z=z_pos,
                    start_color=(255, 255, 0), end_color=(255, 165, 0),
                    speed=24,
                    direction_horizontal_angle=angle,
                    direction_vertical_angle=45,
                    spread_angle=30,
                    track_count=3,
                    duration=0.8, lifetime=1.0
                )
            
            processed_groups_p11.add(start)
            roll_index_p11 += 1
    
    # All snare hits use expanding_sphere_firework (same as Part 6)
    snare_indices_p11 = [i for i, char in enumerate(snare_pattern_p11) if char == '1']
    
    for i in snare_indices_p11:
        tick = get_tick_p11(i)
        x = random.uniform(FIREWORK_X_RANGE[0], FIREWORK_X_RANGE[1])
        z = random.uniform(FIREWORK_Z_RANGE[0], FIREWORK_Z_RANGE[1])
        y = random.uniform(DRUM_Y_EXPLODE_MIN, DRUM_Y_EXPLODE_MAX)
        
        basic_fireworks.expanding_sphere_firework(
            tick=tick, x=x, y=y, z=z,
            start_color=(255, 255, 0), end_color=(255, 215, 0),  # Yellow to Gold
            radius=0.5,
            particle_count=80,
            radial_speed=0.7,
            lifetime=45
        )

    # --- Part 12: Color Variation (00:03:24:22 - 00:03:48:22) ---
    # 8 measures, same rhythm as Part 7 but with color changes
    part12_start_tick = timecode_to_tick("00:03:24:22")
    part12_end_tick = timecode_to_tick("00:03:48:22")
    duration_p12 = (part12_end_tick - part12_start_tick) / 20.0
    ticks_per_16th_p12 = (part12_end_tick - part12_start_tick) / 128  # 8 measures × 16 notes
    
    def get_tick_p12(note_index: int) -> int:
        return round(part12_start_tick + note_index * ticks_per_16th_p12)
    
    # Define 4 corners for pillar effects
    corner_positions_p12 = [
        (FIREWORK_X_RANGE[0], FIREWORK_Z_RANGE[0]),  # SW corner
        (FIREWORK_X_RANGE[0], FIREWORK_Z_RANGE[1]),  # NW corner
        (FIREWORK_X_RANGE[1], FIREWORK_Z_RANGE[0]),  # SE corner
        (FIREWORK_X_RANGE[1], FIREWORK_Z_RANGE[1])   # NE corner
    ]
    
    # --- Kick Drum (Part 12) with Corner Pillars ---
    kick_pattern_p12 = ("1001001000100001" * 7) + "1001001000100000"
    kick_indices_p12 = [i for i, char in enumerate(kick_pattern_p12) if char == '1']
    
    for i in kick_indices_p12:
        tick = get_tick_p12(i)
        x = random.uniform(FIREWORK_X_RANGE[0], FIREWORK_X_RANGE[1])
        z = random.uniform(FIREWORK_Z_RANGE[0], FIREWORK_Z_RANGE[1])
        y = random.uniform(DRUM_Y_EXPLODE_MIN, DRUM_Y_EXPLODE_MAX)
        
        # Kick drum with cool colors
        basic_fireworks.expanding_sphere_firework(
            tick=tick, x=x, y=y, z=z,
            start_color=(100, 180, 255), end_color=(138, 43, 226),  # Cyan-blue to Purple
            radius=1.0,
            particle_count=50,
            radial_speed=1.0,
            lifetime=24
        )
        
        # Corner orange-red pillars synchronized with kick drum
        for corner_x, corner_z in corner_positions_p12:
            for _ in range(100):
                # Random position within diameter 2 circle (radius 1.0)
                angle = random.uniform(0, 2 * math.pi)
                radius = random.uniform(0, 1.0)
                x_offset = radius * math.cos(angle)
                z_offset = radius * math.sin(angle)
                
                x_pos = corner_x + x_offset
                z_pos = corner_z + z_offset
                y_pos = -35  # Center position
                
                # Random vertical velocity (0-5 range, both up and down)
                vy = random.uniform(0, 5) * random.choice([-1, 1])
                vx = 0
                vz = 0
                
                # Generate particle with vertical velocity (orange-red color)
                shared_functions.add_velocity_firework_command(
                    tick=tick, x=x_pos, y=y_pos, z=z_pos,
                    start_color=(255, 69, 0), end_color=(255, 140, 0),  # Orange-red to Dark orange
                    vx=vx, vy=vy, vz=vz,
                    lifetime=40
                )
    
    # --- Melody (Part 12) with Double Layer ---
    melody_pattern_p12 = ("1101101101110100" * 3) + "1011101101101000" + \
                         ("1101101101110100" * 3) + "1011101101101000"
    melody_indices_p12 = [i for i, char in enumerate(melody_pattern_p12) if char == '1']
    
    for i in melody_indices_p12:
        tick = get_tick_p12(i)
        x = random.uniform(FIREWORK_X_RANGE[0], FIREWORK_X_RANGE[1])
        z = random.uniform(FIREWORK_Z_RANGE[0], FIREWORK_Z_RANGE[1])
        y = random.uniform(MELODY_Y_EXPLODE_MIN, MELODY_Y_EXPLODE_MAX)
        
        # Launch spark trajectory
        x0 = x + random.uniform(-3, 3)
        z0 = z + random.uniform(-3, 3)
        firework_trajectories.launch_spark_trajectory(
            end_tick=tick,
            x0=x0, y0=-64, z0=z0,
            x1=x, y1=y, z1=z,
            duration=0.5,
            k=1.0, m0=8, lifetime=0.8, particle_count=2
        )
        
        # Double layer firework (purple to pink to white gradient)
        basic_fireworks.basic_double_layer_firework(
            tick=tick, x=x, y=y, z=z,
            inner_start_color=(200, 150, 255), inner_end_color=(255, 255, 255),  # Purple to White
            outer_start_color=(255, 182, 193), outer_end_color=(255, 255, 255),  # Pink to White
            inner_speed=15, outer_speed=22,
            outer_horizontal_angle_step=45, outer_vertical_angle_step=45,
            duration=1.2, lifetime=1.5
        )
    
    # --- Vocals (Part 12) ---
    vocal_pattern_p12 = ("0000000001110100" * 7) + "0000000000000000"
    vocal_indices_p12 = [i for i, char in enumerate(vocal_pattern_p12) if char == '1']
    
    for i in vocal_indices_p12:
        tick = get_tick_p12(i)
        x = random.uniform(FIREWORK_X_RANGE[0], FIREWORK_X_RANGE[1])
        z = random.uniform(FIREWORK_Z_RANGE[0], FIREWORK_Z_RANGE[1])
        y = random.uniform(MELODY_Y_EXPLODE_MIN, MELODY_Y_EXPLODE_MAX)
        
        # Launch spark trajectory
        x0 = x + random.uniform(-3, 3)
        z0 = z + random.uniform(-3, 3)
        firework_trajectories.launch_spark_trajectory(
            end_tick=tick,
            x0=x0, y0=-64, z0=z0,
            x1=x, y1=y, z1=z,
            duration=0.5,
            k=1.0, m0=8, lifetime=0.8, particle_count=2
        )
        
        # Clustered firework (orange to gold to white gradient)
        basic_fireworks.clustered_firework(
            tick=tick, x=x, y=y, z=z,
            start_color=(255, 165, 0), end_color=(255, 255, 255),  # Orange to White
            speed=18,
            horizontal_angle_step=45, vertical_angle_step=45,
            spread_angle=25,
            track_count=4,
            duration=1.2, lifetime=1.5
        )

    # --- Part 13: Quiet Transition Repeat (00:03:48:22 - 00:04:00:22) ---
    # 4 measures, same as Part 8 but with roll effect at the end
    part13_start_tick = timecode_to_tick("00:03:48:22")
    part13_end_tick = timecode_to_tick("00:04:00:22")
    duration_p13 = (part13_end_tick - part13_start_tick) / 20.0
    ticks_per_16th_p13 = (part13_end_tick - part13_start_tick) / 64  # 4 measures × 16 notes
    
    def get_tick_p13(note_index: int) -> int:
        return round(part13_start_tick + note_index * ticks_per_16th_p13)
    
    # --- Vocals (Part 13) ---
    vocal_pattern_p13 = ("0111010001110011" + "1011110011111000") * 2
    vocal_indices_p13 = [i for i, char in enumerate(vocal_pattern_p13) if char == '1']
    
    for i in vocal_indices_p13:
        tick = get_tick_p13(i)
        x = random.uniform(FIREWORK_X_RANGE[0], FIREWORK_X_RANGE[1])
        z = random.uniform(FIREWORK_Z_RANGE[0], FIREWORK_Z_RANGE[1])
        y = random.uniform(MELODY_Y_EXPLODE_MIN, MELODY_Y_EXPLODE_MAX)
        
        # Small clustered firework (lavender to white)
        basic_fireworks.clustered_firework(
            tick=tick, x=x, y=y, z=z,
            start_color=(200, 162, 200), end_color=(255, 255, 255),  # Lavender to White
            speed=12,
            horizontal_angle_step=60, vertical_angle_step=60,
            spread_angle=20,
            track_count=3,
            duration=1.0, lifetime=1.3
        )
        
        # Halo effect using expanding sphere (light purple to white)
        basic_fireworks.expanding_sphere_firework(
            tick=tick + 5, x=x, y=y, z=z,
            start_color=(220, 200, 255), end_color=(255, 255, 255),  # Light purple to White
            radius=0.4, particle_count=60, radial_speed=0.5, lifetime=25
        )
    
    # --- Guitar (Part 13) ---
    guitar_pattern_p13 = ("0010010010010011" * 3) + "0010010010010000"
    guitar_indices_p13 = [i for i, char in enumerate(guitar_pattern_p13) if char == '1']
    
    for idx, i in enumerate(guitar_indices_p13):
        tick = get_tick_p13(i)
        x = random.uniform(FIREWORK_X_RANGE[0], FIREWORK_X_RANGE[1])
        z = random.uniform(FIREWORK_Z_RANGE[0], FIREWORK_Z_RANGE[1])
        y = random.uniform(MELODY_Y_EXPLODE_MIN, MELODY_Y_EXPLODE_MAX)
        
        # Double layer firework (pink to light yellow)
        basic_fireworks.basic_double_layer_firework(
            tick=tick, x=x, y=y, z=z,
            inner_start_color=(255, 182, 193), inner_end_color=(255, 255, 255),  # Inner: Pink to White
            outer_start_color=(255, 182, 193), outer_end_color=(255, 250, 205),  # Outer: Pink to Light yellow
            inner_speed=10, outer_speed=15,
            outer_horizontal_angle_step=45, outer_vertical_angle_step=45,
            duration=1.0, lifetime=1.2
        )
        
        # Optional directional accent (every other note for variety)
        if idx % 2 == 0:
            basic_fireworks.directional_firework(
                tick=tick + 3, x=x, y=y, z=z,
                start_color=(255, 218, 185), end_color=(255, 255, 224),  # Peach to Light yellow
                speed=10,
                direction_horizontal_angle=random.uniform(60, 120),
                direction_vertical_angle=30,  # Upward tilt
                spread_angle=20,
                track_count=2,
                duration=0.6, lifetime=0.8
            )
    
    # --- Breath Effect at Measure Starts (Ambient) ---
    breath_indices_p13 = [0, 16, 32, 48]
    
    for i in breath_indices_p13:
        tick = get_tick_p13(i)
        x = random.uniform(FIREWORK_X_RANGE[0], FIREWORK_X_RANGE[1])
        z = random.uniform(FIREWORK_Z_RANGE[0], FIREWORK_Z_RANGE[1])
        y = random.uniform(MELODY_Y_EXPLODE_MIN, MELODY_Y_EXPLODE_MAX)
        
        # Large slow expanding sphere (like a breath)
        basic_fireworks.expanding_sphere_firework(
            tick=tick, x=x, y=y, z=z,
            start_color=(173, 216, 230), end_color=(240, 248, 255),  # Light blue to Alice blue
            radius=0.6, particle_count=80, radial_speed=0.3, lifetime=40  # Very slow expansion
        )
    
    # --- Roll Effect at Last Beat (Indices 60-63) ---
    roll_start_tick_p13 = get_tick_p13(60)
    roll_end_tick_p13 = get_tick_p13(64)  # End of measure 4
    roll_duration_ticks_p13 = roll_end_tick_p13 - roll_start_tick_p13
    
    center_x_p13 = (FIREWORK_X_RANGE[0] + FIREWORK_X_RANGE[1]) / 2
    center_z_p13 = (FIREWORK_Z_RANGE[0] + FIREWORK_Z_RANGE[1]) / 2
    
    # Dense directional sweep for roll effect (16 fireworks)
    for j in range(16):
        progress = j / 15 if j < 15 else 1
        sweep_tick = roll_start_tick_p13 + round(progress * roll_duration_ticks_p13)
        
        # Left to right sweep
        z_pos = FIREWORK_Z_RANGE[1] + (FIREWORK_Z_RANGE[0] - FIREWORK_Z_RANGE[1]) * progress
        
        basic_fireworks.directional_firework(
            tick=sweep_tick,
            x=center_x_p13, y=FIREWORK_Y_BASE, z=z_pos,
            start_color=(255, 215, 0), end_color=(255, 165, 0),  # Gold to Orange
            speed=24,
            direction_horizontal_angle=-90,
            direction_vertical_angle=45,
            spread_angle=30,
            track_count=3,
            duration=0.8, lifetime=1.0
        )

    # --- Finalize ---
    print("Scheduling next tick commands...")
    # The scheduling is now handled within the export function itself.
    # export_mcfunction.schedule_next_tick(namespace)
    print(f"Successfully generated firework show. Exporting to '{output_dir}'...")
    export_mcfunction.export_mcfunction(output_dir, namespace)
    # Create auto exec function file
    # export_mcfunction.generate_auto_exec_file(output_dir, datapack_namespace)
