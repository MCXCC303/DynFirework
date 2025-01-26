import tkinter as tk
from tkinter import messagebox
from gui.lib import basic_fireworks, export_mcfunction

tick = 30
x = 0
y = 0
z = 0
inner_start_color = (255, 0, 0)
inner_start_color_labels = ['R', 'G', 'B']
inner_end_color = (255, 255, 255)
inner_end_color_labels = ['R', 'G', 'B']
outer_start_color = (255, 0, 0)
outer_start_color_labels = ['R', 'G', 'B']
outer_end_color = (255, 255, 255)
outer_end_color_labels = ['R', 'G', 'B']
inner_speed = 30
outer_speed = 50
outer_horizontal_angle_step = 30
outer_vertical_angle_step = 30
outer_angle_step_labels = ['Horizontal', 'Vertical']
duration = 4
lifetime = 1.5
other_labels = ['Show Time (duration, s)',
                'Inner Explode Speed (inner_speed, m/s)',
                'Outer Explode Speed (outer_speed, m/s)',
                'Particles\' Lifetime (lifetime, s)']


class DoubleLayerFireworkForm:
    def __init__(self, root, traj_end_data):
        self.root = root
        global tick, x, y, z
        tick, x, y, z = traj_end_data
        inner_start_color_frame = tk.LabelFrame(self.root, text="Inner Start Color (0-255)")
        inner_start_color_frame.grid(row=1, column=0, padx=30, pady=30, sticky=tk.NSEW)
        inner_start_color_insertions = dict(zip(inner_start_color_labels, inner_start_color))
        self.inner_start_color_entries = {}
        inner_end_color_frame = tk.LabelFrame(self.root, text="Inner End Color (0-255)")
        inner_end_color_frame.grid(row=1, column=1, padx=30, pady=30, sticky=tk.NSEW)
        inner_end_color_insertions = dict(zip(inner_end_color_labels, inner_end_color))
        self.inner_end_color_entries = {}
        outer_start_color_frame = tk.LabelFrame(self.root, text="Outer Start Color (0-255)")
        outer_start_color_frame.grid(row=2, column=0, padx=30, pady=30, sticky=tk.NSEW)
        outer_start_color_insertions = dict(zip(outer_start_color_labels, outer_start_color))
        self.outer_start_color_entries = {}
        outer_end_color_frame = tk.LabelFrame(self.root, text="Outer End Color (0-255)")
        outer_end_color_frame.grid(row=2, column=1, padx=30, pady=30, sticky=tk.NSEW)
        outer_end_color_insertions = dict(zip(outer_end_color_labels, outer_end_color))
        self.outer_end_color_entries = {}
        outer_angle_step_frame = tk.LabelFrame(self.root, text="Outer Angle Step")
        outer_angle_step_frame.grid(row=3, column=0, padx=30, pady=30, columnspan=2, sticky=tk.NSEW)
        outer_angle_step_insertions = dict(zip(outer_angle_step_labels,
                                               [outer_horizontal_angle_step, outer_vertical_angle_step]))
        self.outer_angle_step_entries = {}
        other_pos_frame = tk.LabelFrame(self.root, text="Other Data")
        other_pos_frame.grid(row=4, column=0, columnspan=2, padx=30, pady=30, sticky=tk.NSEW)
        other_label_insertions = dict(zip(other_labels,
                                          [duration, inner_speed, outer_speed, lifetime]))
        self.other_entries = {}

        for i, label in enumerate(inner_start_color_labels):
            tk.Label(inner_start_color_frame, text=label).grid(row=i, column=0, padx=10, pady=10, sticky=tk.W)
            entry = tk.Entry(inner_start_color_frame)
            entry.insert(0, str(inner_start_color_insertions[label]))
            entry.grid(row=i, column=1, padx=10, pady=10)
            self.inner_start_color_entries[label] = entry

        self.is_gradiant_inner = tk.BooleanVar()
        (tk.Checkbutton(inner_start_color_frame,
                        text="Gradiant",
                        variable=self.is_gradiant_inner,
                        command=self.enable_gradiant_inner)
         .grid(row=3, column=0, columnspan=2, pady=10))

        for i, label in enumerate(inner_end_color_labels):
            tk.Label(inner_end_color_frame, text=label).grid(row=i, column=0, padx=10, pady=10)
            entry = tk.Entry(inner_end_color_frame)
            entry.insert(0, str(inner_end_color_insertions[label]))
            entry.grid(row=i, column=1, padx=10, pady=10)
            self.inner_end_color_entries[label] = entry

        for i, label in enumerate(outer_start_color_labels):
            tk.Label(outer_start_color_frame, text=label).grid(row=i, column=0, padx=10, pady=10, sticky=tk.W)
            entry = tk.Entry(outer_start_color_frame)
            entry.insert(0, str(outer_start_color_insertions[label]))
            entry.grid(row=i, column=1, padx=10, pady=10)
            self.outer_start_color_entries[label] = entry

        self.is_gradiant_outer = tk.BooleanVar()
        (tk.Checkbutton(outer_start_color_frame,
                        text="Gradiant",
                        variable=self.is_gradiant_outer,
                        command=self.enable_gradiant_outer)
         .grid(row=3, column=0, columnspan=2, pady=10))

        for i, label in enumerate(outer_end_color_labels):
            tk.Label(outer_end_color_frame, text=label).grid(row=i, column=0, padx=10, pady=10)
            entry = tk.Entry(outer_end_color_frame)
            entry.insert(0, str(outer_end_color_insertions[label]))
            entry.grid(row=i, column=1, padx=10, pady=10)
            self.outer_end_color_entries[label] = entry

        for i, label in enumerate(outer_angle_step_labels):
            tk.Label(outer_angle_step_frame, text=label).grid(row=i, column=0, padx=10, pady=10, sticky=tk.W)
            entry = tk.Entry(outer_angle_step_frame)
            entry.insert(0, str(outer_angle_step_insertions[label]))
            entry.grid(row=i, column=1, padx=10, pady=10)
            self.outer_angle_step_entries[label] = entry

        for i, label in enumerate(other_labels):
            tk.Label(other_pos_frame, text=label).grid(row=i, column=0, padx=10, pady=10, sticky=tk.W)
            entry = tk.Entry(other_pos_frame)
            entry.insert(0, str(other_label_insertions[label]))
            entry.grid(row=i, column=1, padx=10, pady=10)
            self.other_entries[label] = entry

        tk.Button(self.root, text='Submit', command=self.submit).grid(row=5, column=0, padx=10, pady=10, columnspan=2)

        self.enable_gradiant_inner()
        self.enable_gradiant_outer()

    def enable_gradiant_inner(self):
        if self.is_gradiant_inner.get():
            for entry in self.inner_end_color_entries.values():
                entry.config(state=tk.NORMAL)
        else:
            for entry in self.inner_end_color_entries.values():
                entry.config(state=tk.DISABLED)

    def enable_gradiant_outer(self):
        if self.is_gradiant_outer.get():
            for entry in self.outer_end_color_entries.values():
                entry.config(state=tk.NORMAL)
        else:
            for entry in self.outer_end_color_entries.values():
                entry.config(state=tk.DISABLED)

    def submit(self):
        global duration, inner_speed, outer_speed, outer_horizontal_angle_step, outer_vertical_angle_step, inner_start_color, outer_start_color, inner_end_color, outer_end_color, lifetime
        inner_start_color = (int(self.inner_start_color_entries['R'].get()),
                             int(self.inner_start_color_entries['G'].get()),
                             int(self.inner_start_color_entries['B'].get()))
        if self.is_gradiant_inner.get():
            inner_end_color = (int(self.inner_end_color_entries['R'].get()),
                               int(self.inner_end_color_entries['G'].get()),
                               int(self.inner_end_color_entries['B'].get()))
        else:
            inner_end_color = inner_start_color
        outer_start_color = (int(self.outer_start_color_entries['R'].get()),
                             int(self.outer_start_color_entries['G'].get()),
                             int(self.outer_start_color_entries['B'].get()))
        if self.is_gradiant_outer.get():
            outer_end_color = (int(self.outer_end_color_entries['R'].get()),
                               int(self.outer_end_color_entries['G'].get()),
                               int(self.outer_end_color_entries['B'].get()))
        else:
            outer_end_color = outer_start_color
        inner_speed = float(self.other_entries['Inner Explode Speed (inner_speed, m/s)'].get())
        outer_speed = float(self.other_entries['Outer Explode Speed (outer_speed, m/s)'].get())
        outer_horizontal_angle_step = int(self.outer_angle_step_entries['Horizontal'].get())
        outer_vertical_angle_step = int(self.outer_angle_step_entries['Vertical'].get())
        duration = float(self.other_entries['Show Time (duration, s)'].get())
        lifetime = float(self.other_entries['Particles\' Lifetime (lifetime, s)'].get())
        basic_fireworks.basic_double_layer_firework(
            tick=tick,
            x=x, y=y, z=z,
            inner_start_color=inner_start_color,
            outer_start_color=outer_start_color,
            inner_end_color=inner_end_color,
            outer_end_color=outer_end_color,
            lifetime=lifetime,
            duration=duration,
            inner_speed=inner_speed,
            outer_speed=outer_speed,
            outer_horizontal_angle_step=outer_horizontal_angle_step,
            outer_vertical_angle_step=outer_vertical_angle_step,
        )
        continuing = messagebox.askyesno('Double Layer Firework',
                                         f'Generated Double Layer Firework\nAt:\n({x}, {y}, {z})\n'
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
