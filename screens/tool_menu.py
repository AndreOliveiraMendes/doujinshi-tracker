# doujinshi_manager/screens/tool_menu.py
import tkinter as tk
from .tool_view import ToolViewScreen  # Import ToolViewScreen
from .tool_insert import ToolInsertScreen  # Import ToolInsertScreen

class ToolMenu(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        tk.Label(self, text="Manage Tools", font=("Arial", 14)).pack(pady=20)

        tk.Button(self, text="View Tools", command=lambda: controller.show_frame(ToolViewScreen)).pack(pady=5)
        tk.Button(self, text="Insert Tool", command=lambda: controller.show_frame(ToolInsertScreen)).pack(pady=5)
        tk.Button(self, text="Back", command=controller.go_back).pack(pady=5)
        tk.Button(self, text="Main Menu", command=controller.go_to_main_menu).pack(pady=5)