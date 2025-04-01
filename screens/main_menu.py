# doujinshi_manager/screens/main_menu.py
import tkinter as tk
from .database_menu import DatabaseMenu  # Import DatabaseMenu
from .directory_menu import DirectoryMenu  # Import DirectoryMenu

class MainMenu(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        tk.Label(self, text="Doujinshi Colorization Manager", font=("Arial", 16)).pack(pady=20)

        tk.Button(self, text="Manage Database", command=lambda: controller.show_frame(DatabaseMenu)).pack(pady=10)
        tk.Button(self, text="Manage Directories", command=lambda: controller.show_frame(DirectoryMenu)).pack(pady=10)
        # Disable the Back button since this is the main screen
        back_button = tk.Button(self, text="Back", command=controller.go_back)
        back_button.pack(pady=10)
        back_button.config(state="disabled")  # Disable the button
        tk.Button(self, text="Exit", command=controller.quit).pack(pady=10)