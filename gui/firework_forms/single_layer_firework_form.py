import tkinter as tk
from tkinter import messagebox
from gui.lib import basic_fireworks, export_mcfunction

tick = 30
x = 0
y = 0
z = 0
start_color = (255, 0, 0)
start_color_labels = ['R', 'G', 'B']
end_color = (255, 255, 255)
end_color_labels = ['R', 'G', 'B']
speed = 30
directional_horizontal_angle = 30
direction_vertical_angle = 30
angle_step_labels = ['Horizontal', 'Vertical']
duration = 4
lifetime = 1.5
other_labels = ['Show Time (duration, s)',
                'Explode Speed (speed, m/s)',
                'Particles\' Lifetime (lifetime, s)']


class SingleLayerFireworkForm:
    def __init__(self, root, traj_end_data):
        self.root = root
        global tick, x, y, z
        tick, x, y, z = traj_end_data
        start_color_frame = tk.LabelFrame(self.root, text="Start Color (0-255)")
        start_color_frame.grid(row=2, column=0, padx=30, pady=30, sticky=tk.NSEW)
        start_color_insertions = dict(zip(start_color_labels, start_color))
        self.start_color_entries = {}
        end_color_frame = tk.LabelFrame(self.root, text="End Color (0-255)")
        end_color_frame.grid(row=2, column=1, padx=30, pady=30, sticky=tk.NSEW)
        end_color_insertions = dict(zip(end_color_labels, end_color))
        self.end_color_entries = {}
        angle_step_frame = tk.LabelFrame(self.root, text="Angle Step")
        angle_step_frame.grid(row=3, column=0, padx=30, pady=30, columnspan=2, sticky=tk.NSEW)
        angle_step_insertions = dict(zip(angle_step_labels,
                                         [directional_horizontal_angle, direction_vertical_angle]))
        self.angle_step_entries = {}
        other_pos_frame = tk.LabelFrame(self.root, text="Other Data")
        other_pos_frame.grid(row=4, column=0, columnspan=2, padx=30, pady=30, sticky=tk.NSEW)
        other_label_insertions = dict(zip(other_labels,
                                          [duration, speed, lifetime]))
        self.other_entries = {}

        for i, label in enumerate(start_color_labels):
            tk.Label(start_color_frame, text=label).grid(row=i, column=0, padx=10, pady=10, sticky=tk.W)
            entry = tk.Entry(start_color_frame)
            entry.insert(0, str(start_color_insertions[label]))
            entry.grid(row=i, column=1, padx=10, pady=10)
            self.start_color_entries[label] = entry

        self.is_gradiant = tk.BooleanVar()
        (tk.Checkbutton(start_color_frame,
                        text="Gradiant",
                        variable=self.is_gradiant,
                        command=self.enable_gradiant)
         .grid(row=3, column=0, columnspan=2, pady=10))

        for i, label in enumerate(end_color_labels):
            tk.Label(end_color_frame, text=label).grid(row=i, column=0, padx=10, pady=10)
            entry = tk.Entry(end_color_frame)
            entry.insert(0, str(end_color_insertions[label]))
            entry.grid(row=i, column=1, padx=10, pady=10)
            self.end_color_entries[label] = entry

        for i, label in enumerate(angle_step_labels):
            tk.Label(angle_step_frame, text=label).grid(row=i, column=0, padx=10, pady=10, sticky=tk.W)
            entry = tk.Entry(angle_step_frame)
            entry.insert(0, str(angle_step_insertions[label]))
            entry.grid(row=i, column=1, padx=10, pady=10)
            self.angle_step_entries[label] = entry

        for i, label in enumerate(other_labels):
            tk.Label(other_pos_frame, text=label).grid(row=i, column=0, padx=10, pady=10, sticky=tk.W)
            entry = tk.Entry(other_pos_frame)
            entry.insert(0, str(other_label_insertions[label]))
            entry.grid(row=i, column=1, padx=10, pady=10)
            self.other_entries[label] = entry

        tk.Button(self.root, text='Submit', command=self.submit).grid(row=5, column=0, padx=10, pady=10, columnspan=2)

        self.enable_gradiant()

    def enable_gradiant(self):
        if self.is_gradiant.get():
            for entry in self.end_color_entries.values():
                entry.config(state=tk.NORMAL)
        else:
            for entry in self.end_color_entries.values():
                entry.config(state=tk.DISABLED)

    def submit(self):
        global duration, start_color, end_color, lifetime, x, y, z, directional_horizontal_angle, direction_vertical_angle, speed
        start_color = (int(self.start_color_entries['R'].get()),
                       int(self.start_color_entries['G'].get()),
                       int(self.start_color_entries['B'].get()))
        if self.is_gradiant.get():
            end_color = (int(self.end_color_entries['R'].get()),
                         int(self.end_color_entries['G'].get()),
                         int(self.end_color_entries['B'].get()))
        else:
            end_color = start_color
        speed = float(self.other_entries['Explode Speed (speed, m/s)'].get())
        horizontal_angle_step = int(self.angle_step_entries['Horizontal'].get())
        vertical_angle_step = int(self.angle_step_entries['Vertical'].get())
        duration = float(self.other_entries['Show Time (duration, s)'].get())
        lifetime = float(self.other_entries['Particles\' Lifetime (lifetime, s)'].get())
        basic_fireworks.basic_single_layer_firework(
            tick=tick,
            x=x, y=y, z=z,
            start_color=start_color,
            end_color=end_color,
            speed=speed,
            horizontal_angle_step=horizontal_angle_step,
            vertical_angle_step=vertical_angle_step,
            duration=duration,
            lifetime=lifetime)
        continuing = messagebox.askyesno('Single Layer Firework',
                                         f'Generated Single Layer Firework\nAt:\n({x}, {y}, {z})\n'
                                         f'Continue Generating?')
        for widget in self.root.winfo_children():
            widget.destroy()
        if not continuing:
            self.root.destroy()
            from gui.datapack_form import datapack_namespace, output_dir
            export_mcfunction.schedule_next_tick(datapack_namespace)
            export_mcfunction.export_mcfunction(output_dir)
        else:
            from gui.selection.select_traj import TrajectorySelect
            TrajectorySelect(self.root)
