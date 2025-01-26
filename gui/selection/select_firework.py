import tkinter as tk
from PIL import Image, ImageTk
from gui.firework_forms.clustered_firework_form import ClusteredFireworkForm
from gui.firework_forms.single_layer_firework_form import SingleLayerFireworkForm
from gui.firework_forms.double_layer_firework_form import DoubleLayerFireworkForm
from gui.firework_forms.directional_firework_form import DirectionalFireworkForm

firework_image_names = ['gui/selection/firework_image/slf.png',
                        'gui/selection/firework_image/dlf.png',
                        'gui/selection/firework_image/cf.png',
                        'gui/selection/firework_image/df.png', ]

firework_types = ['Single Layer\nFirework',
                  'Double Layer\nFirework',
                  'Clustered\nFirework',
                  'Directional\nFirework']


class FireworkSelect:
    # 3rd page
    def __init__(self, root, traj_end_data):
        self.root = root
        self.traj_end_data = traj_end_data
        self.root.title("Firework Select")
        tk.Label(self.root, text="Select Firework", font=('Arial', 50, 'bold')).grid(
            row=0,
            column=1,
            pady=50,
            padx=50,
            columnspan=3)
        firework_images = []
        for name in firework_image_names:
            image = Image.open(name)
            resized_image = image.resize((256, 256))
            photo = ImageTk.PhotoImage(resized_image)
            firework_images.append(photo)

        selection_info = list(zip(firework_types, firework_images))
        for i, (firework_type, image) in enumerate(selection_info):
            tk.Button(self.root, text=firework_type, command=lambda t=firework_type: self.jump_to_form_page(t)).grid(
                row=2 * (i // 3 + 1),
                column=i % 3 + 1,
                padx=30,
                pady=30)
            label_image = tk.Label(self.root, image=image)
            label_image.image = image
            label_image.grid(row=2 * (i // 3 + 1) - 1, column=i % 3 + 1, padx=30, pady=30)

    def jump_to_form_page(self, firework_type: str):
        for widget in self.root.winfo_children():
            widget.destroy()
        print(firework_type.replace('\n', ' '))
        if firework_type == 'Single Layer\nFirework':
            SingleLayerFireworkForm(self.root, self.traj_end_data)
        if firework_type == 'Double Layer\nFirework':
            DoubleLayerFireworkForm(self.root, self.traj_end_data)
        if firework_type == 'Clustered\nFirework':
            ClusteredFireworkForm(self.root, self.traj_end_data)
        if firework_type == 'Directional\nFirework':
            DirectionalFireworkForm(self.root, self.traj_end_data)
