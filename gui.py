import tkinter as tk
from gui import datapack_form

if __name__ == "__main__":
    root = tk.Tk()
    root.option_add('*Label.Font', 'times 12 bold')
    root.option_add('*Button.Font', 'Arial 12')
    root.option_add('*Entry.Font', 'times 12')
    root.option_add('*Checkbutton.Font', 'Arial 12')
    root.option_add('*Dialog.msg.Font', 'Arial 12')
    root.title("Generate Datapack")
    datapack_form.DatapackForm(root)
    root.mainloop()
