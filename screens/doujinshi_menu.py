# doujinshi_manager/screens/doujinshi_menu.py
import tkinter as tk
from .doujinshi_view import DoujinshiViewScreen  # Import DoujinshiViewScreen
from .doujinshi_insert import DoujinshiInsertScreen  # Import DoujinshiInsertScreen

class DoujinshiMenu(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        tk.Label(self, text="Manage Doujinshi", font=("Arial", 14)).pack(pady=20)

        tk.Button(self, text="View Doujinshi", command=lambda: controller.show_frame(DoujinshiViewScreen)).pack(pady=5)
        tk.Button(self, text="Insert Doujinshi", command=lambda: controller.show_frame(DoujinshiInsertScreen)).pack(pady=5)
        tk.Button(self, text="Back", command=controller.go_back).pack(pady=5)
        tk.Button(self, text="Main Menu", command=controller.go_to_main_menu).pack(pady=5)