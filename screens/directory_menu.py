# doujinshi_manager/screens/directory_menu.py
import tkinter as tk
from tkinter import messagebox
import os
import shutil  # Import shutil for rmtree

class DirectoryMenu(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        tk.Label(self, text="Manage Directories", font=("Arial", 14)).pack(pady=20)

        tk.Button(self, text="Create Directory", command=self.create_directory).pack(pady=5)
        tk.Button(self, text="Delete Directory", command=self.delete_directory).pack(pady=5)
        tk.Button(self, text="Back", command=controller.go_back).pack(pady=5)
        tk.Button(self, text="Main Menu", command=controller.go_to_main_menu).pack(pady=5)

    def create_directory(self):
        folder_path = tk.simpledialog.askstring("Input", "Enter folder path (e.g., c12):", parent=self)
        if not folder_path:
            return
        full_path = os.path.join("doujinshi_collection", folder_path)
        try:
            os.makedirs(full_path, exist_ok=True)
            messagebox.showinfo("Success", f"Created directory: {full_path}")
        except OSError as e:
            messagebox.showerror("Error", f"Failed to create directory: {e}")

    def delete_directory(self):
        folder_path = tk.simpledialog.askstring("Input", "Enter folder path to delete (e.g., c12):", parent=self)
        if not folder_path:
            return
        full_path = os.path.join("doujinshi_collection", folder_path)
        if not os.path.exists(full_path):
            messagebox.showerror("Error", f"Directory {full_path} does not exist!")
            return
        confirm = messagebox.askyesno("Confirm", f"Are you sure you want to delete {full_path}?")
        if confirm:
            try:
                shutil.rmtree(full_path)  # Use shutil.rmtree instead of os.rmtree
                messagebox.showinfo("Success", f"Deleted directory: {full_path}")
            except OSError as e:
                messagebox.showerror("Error", f"Failed to delete directory: {e}")