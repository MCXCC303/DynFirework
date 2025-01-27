import tkinter as tk
from PIL import Image, ImageTk
from gui.traj_forms.launch_traj_form import LaunchTrajForm
from gui.traj_forms.launch_spark_traj_form import LaunchSparkTrajForm
from gui.traj_forms.trajectory_with_interval_form import TrajWithIntervalForm
from gui.traj_forms.thick_trajectory_with_interval_form import ThickTrajWithIntervalForm
from gui.traj_forms.expanding_trajectory_with_interval_form import ExpdTrajWithIntervalForm

trajectory_types = ['Launch\nTrajectory',
                    'Launch Spark\nTrajectory',
                    'Trajectory\nwith random offset',
                    'Thick Trajectory\nwith random offset',
                    'Expanding Trajectory\nwith random offset']

trajectory_image_names = ['gui/selection/traj_image/lt.png',
                          'gui/selection/traj_image/lst.png',
                          'gui/selection/traj_image/t_wro.png',
                          'gui/selection/traj_image/tt_wro.png',
                          'gui/selection/traj_image/et_wro.png']


class TrajectorySelect:
    # 2rd page
    def __init__(self, root):
        self.root = root
        self.root.title("Trajectory Select")
        tk.Label(self.root, text="Select Trajectory", font=('Arial', 30, 'bold')).grid(
            row=0,
            column=1,
            pady=20,
            padx=30,
            columnspan=3)
        trajectory_images = []
        for name in trajectory_image_names:
            image = Image.open(name)
            resized_image = image.resize((128, 128))
            photo = ImageTk.PhotoImage(resized_image)
            trajectory_images.append(photo)

        selection_info = list(zip(trajectory_types, trajectory_images))
        for i, (traj_type, image) in enumerate(selection_info):
            tk.Button(self.root, text=traj_type, command=lambda t=traj_type: self.jump_to_form_page(t)).grid(
                row=2 * (i // 3 + 1),
                column=i % 3 + 1,
                padx=30,
                pady=20)
            label_image = tk.Label(self.root, image=image)
            label_image.image = image
            label_image.grid(row=2 * (i // 3 + 1) - 1, column=i % 3 + 1, padx=5, pady=5)

    def jump_to_form_page(self, trajectory_type: str):
        for widget in self.root.winfo_children():
            widget.destroy()
        print(trajectory_type.replace('\n', ' '))
        if trajectory_type == 'Launch\nTrajectory':
            LaunchTrajForm(self.root)
        if trajectory_type == 'Launch Spark\nTrajectory':
            LaunchSparkTrajForm(self.root)
        if trajectory_type == 'Trajectory\nwith random offset':
            TrajWithIntervalForm(self.root)
        if trajectory_type == 'Thick Trajectory\nwith random offset':
            ThickTrajWithIntervalForm(self.root)
        if trajectory_type == 'Expanding Trajectory\nwith random offset':
            ExpdTrajWithIntervalForm(self.root)
