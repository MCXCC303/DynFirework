import tkinter as tk
from gui import datapack_form

if __name__ == "__main__":
    root = tk.Tk()
    root.option_add('*Label.Font', 'times 20 bold')
    root.option_add('*Button.Font', 'Arial 20')
    root.option_add('*Entry.Font', 'times 20')
    root.option_add('*Checkbutton.Font', 'Arial 20')
    root.option_add('*Dialog.msg.Font', 'Arial 16')
    root.title("Generate Datapack")
    datapack_form.DatapackForm(root)
    root.mainloop()

