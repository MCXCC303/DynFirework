import tkinter as tk
from tkinter import messagebox
from gui.selection import select_firework
from gui.lib import firework_trajectories

end_tick = 60
start_pos_labels = ['x', 'y', 'z']
x0 = 0
y0 = 0
z0 = 0
end_pos_labels = ['x', 'y', 'z']
x1 = 50
y1 = 100
z1 = 30
duration = 2.0
m0 = 2.0
k = 1.2
interval_ticks = 5
points_per_tick = 5
interval_labels = ['Interval Ticks', 'Points Per Tick']
range_x = 0.15
range_y = 0.15
range_z = 0.15
particle_count = 5
group_labels = ['x', 'y', 'z', 'Particle Counts']
lifetime = 0.5
other_labels = ['Explode Time (end_tick/20, s)',
                'Launch Time (end_tick/20-duration, s)',
                'Particles\' Lifetime (lifetime, s)',
                'Particle Massive (m0)',
                'Air Resistance (k)']


class ThickTrajWithIntervalForm:
    def __init__(self, root):
        self.root = root
        self.root.title("Thick Trajectory with interval: Info")
        start_pos_frame = tk.LabelFrame(self.root, text="Start Position")
        start_pos_frame.grid(row=1, column=0, padx=30, pady=30, sticky=tk.NSEW)
        start_pos_insertions = dict(zip(start_pos_labels,
                                        [x0, y0, z0]))
        self.start_pos_entries = {}
        end_pos_frame = tk.LabelFrame(self.root, text="End Position")
        end_pos_frame.grid(row=1, column=1, padx=30, pady=30, sticky=tk.NSEW)
        end_pos_insertions = dict(zip(end_pos_labels,
                                      [x1, y1, z1]))
        self.end_pos_entries = {}
        interval_frame = tk.LabelFrame(self.root, text="Interval Info")
        interval_frame.grid(row=2, column=0, padx=30, pady=30, sticky=tk.NSEW)
        interval_insertions = dict(zip(interval_labels, [interval_ticks, points_per_tick]))
        self.interval_entries = {}
        group_frame = tk.LabelFrame(self.root, text="Group Info")
        group_frame.grid(row=2, column=1, padx=30, pady=30, sticky=tk.NSEW)
        group_insertions = dict(zip(group_labels, [range_x, range_y, range_z, particle_count]))
        self.group_entries = {}
        other_pos_frame = tk.LabelFrame(self.root, text="Other Data")
        other_pos_frame.grid(row=3, column=0, columnspan=2, padx=30, pady=30, sticky=tk.NSEW)
        other_label_insertions = dict(zip(other_labels,
                                          [int(end_tick / 20),
                                           end_tick / 20 - duration,
                                           lifetime, m0, k]))
        self.other_entries = {}

        for i, label in enumerate(start_pos_labels):
            tk.Label(start_pos_frame, text=label).grid(row=i, column=0, padx=10, pady=10)
            entry = tk.Entry(start_pos_frame)
            entry.insert(0, str(start_pos_insertions[label]))
            entry.grid(row=i, column=1, padx=10, pady=10)
            self.start_pos_entries[label] = entry

        for i, label in enumerate(end_pos_labels):
            tk.Label(end_pos_frame, text=label).grid(row=i, column=0, padx=10, pady=10)
            entry = tk.Entry(end_pos_frame)
            entry.insert(0, str(end_pos_insertions[label]))
            entry.grid(row=i, column=1, padx=10, pady=10)
            self.end_pos_entries[label] = entry

        for i, label in enumerate(interval_labels):
            tk.Label(interval_frame, text=label).grid(row=i, column=0, padx=10, pady=10, sticky=tk.W)
            entry = tk.Entry(interval_frame)
            entry.insert(0, str(interval_insertions[label]))
            entry.grid(row=i, column=1, padx=10, pady=10)
            self.interval_entries[label] = entry

        for i, label in enumerate(group_labels):
            tk.Label(group_frame, text=label).grid(row=i, column=0, padx=10, pady=10, sticky=tk.W)
            entry = tk.Entry(group_frame)
            entry.insert(0, str(group_insertions[label]))
            entry.grid(row=i, column=1, padx=10, pady=10)
            self.group_entries[label] = entry

        self.sync_range = tk.BooleanVar()
        (tk.Checkbutton(group_frame,
                        text="Sync Range",
                        variable=self.sync_range,
                        command=self.sync_range_enabled)
         .grid(row=4, column=0, columnspan=2, pady=10))

        for i, label in enumerate(other_labels):
            tk.Label(other_pos_frame, text=label).grid(row=i, column=0, padx=10, pady=10, sticky=tk.W)
            entry = tk.Entry(other_pos_frame)
            entry.insert(0, str(other_label_insertions[label]))
            entry.grid(row=i, column=1, padx=10, pady=10)
            self.other_entries[label] = entry

        tk.Button(self.root, text='Submit', command=self.submit).grid(row=4, column=0, padx=10, pady=10, columnspan=2)

        self.sync_range_enabled()

    def sync_range_enabled(self):
        if self.sync_range.get():
            self.group_entries['y'].config(state=tk.DISABLED)
            self.group_entries['z'].config(state=tk.DISABLED)
        else:
            self.group_entries['y'].config(state=tk.NORMAL)
            self.group_entries['z'].config(state=tk.NORMAL)

    def submit(self):
        global end_tick, x0, y0, z0, x1, y1, z1, duration, m0, k, lifetime, points_per_tick, interval_ticks, range_x, range_y, range_z, particle_count
        end_tick = int(self.other_entries['Explode Time (end_tick/20, s)'].get()) * 20
        x0 = float(self.start_pos_entries['x'].get())
        y0 = float(self.start_pos_entries['y'].get())
        z0 = float(self.start_pos_entries['z'].get())
        x1 = float(self.end_pos_entries['x'].get())
        y1 = float(self.end_pos_entries['y'].get())
        z1 = float(self.end_pos_entries['z'].get())
        duration = end_tick / 20 - float(self.other_entries['Launch Time (end_tick/20-duration, s)'].get())
        k = float(self.other_entries['Air Resistance (k)'].get())
        m0 = float(self.other_entries['Particle Massive (m0)'].get())
        lifetime = float(self.other_entries['Particles\' Lifetime (lifetime, s)'].get())
        interval_ticks = int(self.interval_entries['Interval Ticks'].get())
        points_per_tick = int(self.interval_entries['Points Per Tick'].get())
        particle_count = int(self.group_entries['Particle Counts'].get())
        range_x = float(self.group_entries['x'].get())
        if self.sync_range.get():
            range_y = range_x
            range_z = range_x
        else:
            range_y = float(self.group_entries['y'].get())
            range_z = float(self.group_entries['z'].get())
        firework_trajectories.thick_trajectory_with_random_offset(
            end_tick=end_tick,
            x0=x0, y0=y0, z0=z0,
            x1=x1, y1=y1, z1=z1,
            duration=duration,
            k=k,
            m0=m0,
            lifetime=lifetime,
            points_per_tick=points_per_tick,
            interval_ticks=interval_ticks,
        range_x=range_x, range_y=range_y, range_z=range_z, particle_count=particle_count)
        messagebox.showinfo('Thick Trajectory with interval',
                            f'Generated Thick Trajectory with interval\nFrom:\n({x0}, {y0}, {z0})\nTo:\n({x1}, {y1}, {z1})')
        for widget in self.root.winfo_children():
            widget.destroy()
        select_firework.FireworkSelect(self.root, (end_tick, x1, y1, z1))
