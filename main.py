import sys
import os
sys.path.append(os.path.dirname(__file__))

import tkinter as tk
from ui import VivaUI

if __name__ == '__main__':
    root = tk.Tk()
    app = VivaUI(root)
    root.mainloop()
