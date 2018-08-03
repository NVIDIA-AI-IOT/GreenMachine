from Tkinter import *
import Tkinter as tk
from gui import GUI

root = Tk()
root.columnconfigure((2), weight=1)  # make buttons stretch when
my_gui = GUI(root)
root.mainloop()