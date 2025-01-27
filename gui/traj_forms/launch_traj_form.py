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
start_color = (255, 0, 0)
start_color_labels = ['R', 'G', 'B']
end_color = (255, 255, 255)
end_color_labels = ['R', 'G', 'B']
m0 = 2.0
k = 1.2
lifetime = 0.5
rho = 5
other_labels = ['Explode Time (end_tick/20, s)',
                'Launch Time (end_tick/20-duration, s)',
                'Particles\' Lifetime (lifetime, s)',
                'Particle Massive (m0)',
                'Particles Per Second (rho)',
                'Air Resistance (k)']


class LaunchTrajForm:
    def __init__(self, root):
        self.root = root
        self.root.title("Launch Trajectory: Info")
        tk.Label(self.root, text="Launch Trajectory", font=('Arial', 30, 'bold')).grid(
            row=0,
            column=0,
            pady=3,
            padx=30,
            columnspan=2)
        start_pos_frame = tk.LabelFrame(self.root, text="Start Position")
        start_pos_frame.grid(row=1, column=0, padx=30, pady=3, sticky=tk.NSEW)
        start_pos_insertions = dict(zip(start_pos_labels,
                                        [x0, y0, z0]))
        self.start_pos_entries = {}
        end_pos_frame = tk.LabelFrame(self.root, text="End Position")
        end_pos_frame.grid(row=1, column=1, padx=30, pady=3, sticky=tk.NSEW)
        end_pos_insertions = dict(zip(end_pos_labels,
                                      [x1, y1, z1]))
        self.end_pos_entries = {}
        start_color_frame = tk.LabelFrame(self.root, text="Start Color (0-255)")
        start_color_frame.grid(row=2, column=0, padx=30, pady=3, sticky=tk.NSEW)
        start_color_insertions = dict(zip(start_color_labels, start_color))
        self.start_color_entries = {}
        end_color_frame = tk.LabelFrame(self.root, text="End Color (0-255)")
        end_color_frame.grid(row=2, column=1, padx=30, pady=3, sticky=tk.NSEW)
        end_color_insertions = dict(zip(end_color_labels, end_color))
        self.end_color_entries = {}
        other_pos_frame = tk.LabelFrame(self.root, text="Other Data")
        other_pos_frame.grid(row=3, column=0, columnspan=2, padx=30, pady=3, sticky=tk.NSEW)
        other_label_insertions = dict(zip(other_labels,
                                          [int(end_tick / 20), end_tick / 20 - duration, lifetime, m0, rho, k]))
        self.other_entries = {}

        for i, label in enumerate(start_pos_labels):
            tk.Label(start_pos_frame, text=label).grid(row=i, column=0, padx=10, pady=10)
            entry = tk.Entry(start_pos_frame)
            entry.insert(0, str(start_pos_insertions[label]))
            entry.grid(row=i, column=1, padx=10, pady=10)
            self.start_pos_entries[label] = entry

        for i, label in enumerate(end_pos_labels):
            tk.Label(end_pos_frame, text=label).grid(row=i, column=1, padx=10, pady=10)
            entry = tk.Entry(end_pos_frame)
            entry.insert(0, str(end_pos_insertions[label]))
            entry.grid(row=i, column=2, padx=10, pady=10)
            self.end_pos_entries[label] = entry

        for i, label in enumerate(start_color_labels):
            tk.Label(start_color_frame, text=label).grid(row=i, column=0, padx=10, pady=10)
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

        for i, label in enumerate(other_labels):
            tk.Label(other_pos_frame, text=label).grid(row=i, column=0, padx=10, pady=10, sticky=tk.W)
            entry = tk.Entry(other_pos_frame)
            entry.insert(0, str(other_label_insertions[label]))
            entry.grid(row=i, column=1, padx=10, pady=10)
            self.other_entries[label] = entry

        tk.Button(self.root, text='Submit', command=self.submit).grid(row=4, column=0, padx=10, pady=10, columnspan=2)

        self.enable_gradiant()

    def enable_gradiant(self):
        if self.is_gradiant.get():
            for entry in self.end_color_entries.values():
                entry.config(state=tk.NORMAL)
        else:
            for entry in self.end_color_entries.values():
                entry.config(state=tk.DISABLED)

    def submit(self):
        global end_tick, x0, y0, z0, x1, y1, z1, duration, m0, k, start_color, end_color, lifetime, rho
        end_tick = int(self.other_entries['Explode Time (end_tick/20, s)'].get()) * 20
        x0 = float(self.start_pos_entries['x'].get())
        y0 = float(self.start_pos_entries['y'].get())
        z0 = float(self.start_pos_entries['z'].get())
        x1 = float(self.end_pos_entries['x'].get())
        y1 = float(self.end_pos_entries['y'].get())
        z1 = float(self.end_pos_entries['z'].get())
        duration = end_tick / 20 - float(self.other_entries['Launch Time (end_tick/20-duration, s)'].get())
        start_color = (int(self.start_color_entries['R'].get()),
                       int(self.start_color_entries['G'].get()),
                       int(self.start_color_entries['B'].get()))
        if self.is_gradiant.get():
            end_color = (int(self.end_color_entries['R'].get()),
                         int(self.end_color_entries['G'].get()),
                         int(self.end_color_entries['B'].get()))
        else:
            end_color = start_color
        k = float(self.other_entries['Air Resistance (k)'].get())
        m0 = float(self.other_entries['Particle Massive (m0)'].get())
        lifetime = float(self.other_entries['Particles\' Lifetime (lifetime, s)'].get())
        rho = int(self.other_entries['Particles Per Second (rho)'].get())
        firework_trajectories.launch_trajectory(
            end_tick=end_tick,
            x0=x0, y0=y0, z0=z0,
            x1=x1, y1=y1, z1=z1,
            duration=duration,
            start_color=start_color,
            end_color=end_color,
            k=k,
            m0=m0,
            lifetime=lifetime,
            rho=rho)
        messagebox.showinfo('Launch Trajectory',
                            f'Generated Launch Trajectory\nFrom:\n({x0}, {y0}, {z0})\nTo:\n({x1}, {y1}, {z1})')
        for widget in self.root.winfo_children():
            widget.destroy()
        select_firework.FireworkSelect(self.root, (end_tick, x1, y1, z1))
