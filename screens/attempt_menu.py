# doujinshi_manager/screens/attempt_menu.py
import tkinter as tk
from .attempt_view import AttemptViewScreen  # Import AttemptViewScreen
from .attempt_insert import AttemptInsertScreen  # Import AttemptInsertScreen

class AttemptMenu(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        tk.Label(self, text="Manage Attempts", font=("Arial", 14)).pack(pady=20)

        tk.Button(self, text="View Attempts", command=lambda: controller.show_frame(AttemptViewScreen)).pack(pady=5)
        tk.Button(self, text="Insert Attempt", command=lambda: controller.show_frame(AttemptInsertScreen)).pack(pady=5)
        tk.Button(self, text="Back", command=controller.go_back).pack(pady=5)
        tk.Button(self, text="Main Menu", command=controller.go_to_main_menu).pack(pady=5)