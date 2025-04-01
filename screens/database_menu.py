# doujinshi_manager/screens/database_menu.py
import tkinter as tk
from .doujinshi_menu import DoujinshiMenu  # Import DoujinshiMenu
from .attempt_menu import AttemptMenu  # Import AttemptMenu
from .tool_menu import ToolMenu  # Import ToolMenu

class DatabaseMenu(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        tk.Label(self, text="Manage Database", font=("Arial", 14)).pack(pady=20)

        tk.Button(self, text="Manage Doujinshi", command=lambda: controller.show_frame(DoujinshiMenu)).pack(pady=5)
        tk.Button(self, text="Manage Attempts", command=lambda: controller.show_frame(AttemptMenu)).pack(pady=5)
        tk.Button(self, text="Manage Tools", command=lambda: controller.show_frame(ToolMenu)).pack(pady=5)
        tk.Button(self, text="Back", command=controller.go_back).pack(pady=5)
        tk.Button(self, text="Main Menu", command=controller.go_to_main_menu).pack(pady=5)