# doujinshi_manager/screens/doujinshi_view.py
import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import os
import shutil
from .utility import DinamicTable

class DoujinshiViewScreen(tk.Frame):
    def __init__(self, parent, controller, cursor, conn):
        super().__init__(parent)
        self.controller = controller
        self.cursor = cursor
        self.conn = conn
        tk.Label(self, text="View Doujinshi", font=("Arial", 14)).pack(pady=10)

        # Define table configuration
        table_config = {
            "table_name": "color_subject",
            "columns": ['code', 'series_id', 'part_id', 'series_name', 'series_alt_name', 'part_name', 'part_alt_name', 'origin', 'artist', 'folder_path'],
            "column_display_names": {
                'code': 'Code',
                'series_id': 'Series ID',
                'part_id': 'Part ID',
                'series_name':'Series Name',
                'series_alt_name': 'Series Name*',
                'part_name': 'Chapter Name',
                'part_alt_name': 'Chapter Name*',
                'origin': 'Origin',
                'artist': 'Artist',
                'folder_path': 'Folder Path'
            },
            "column_widths": {
                'code': 60,
                'series_id': 40,
                'part_id': 40,
                'series_name': 150,
                'series_alt_name': 150,
                'part_name': 100,
                'part_alt_name': 100,
                'origin': 100,
                'artist': 100,
                'folder_path': 40
            }
        }

        # Create the dinamic table
        self.dinamic_table = DinamicTable(
            self,
            cursor=self.cursor,
            table_name=table_config["table_name"],
            columns=table_config["columns"],
            column_display_names=table_config["column_display_names"],
            column_widths=table_config["column_widths"]
        )
        self.dinamic_table.pack(fill="both", expand=True)

        # Buttons for actions
        tk.Button(self, text="Edit Selected", command=self.edit_selected).pack(pady=5)
        tk.Button(self, text="Delete Selected", command=self.delete_selected).pack(pady=5)
        tk.Button(self, text="Back", command=controller.go_back).pack(pady=5)
        tk.Button(self, text="Main Menu", command=controller.go_to_main_menu).pack(pady=5)

    def edit_selected(self):
        from .doujinshi_modify import DoujinshiModifyScreen
        data = self.dinamic_table.get_selected_data()
        if not data:
            messagebox.showerror("Error", "Please select a doujinshi to edit!")
            return
        code = data.get("code")
        if not code:
            messagebox.showerror("Error", "Cannot edit: 'Code' column is hidden!")
            return
        self.cursor.execute("SELECT * FROM color_subject WHERE code = ?", (code,))
        doujinshi_data = self.cursor.fetchone()
        if doujinshi_data:
            self.controller.frames[DoujinshiModifyScreen].load_data(doujinshi_data)
            self.controller.show_frame(DoujinshiModifyScreen)

    def delete_selected(self):
        data = self.dinamic_table.get_selected_data()
        if not data:
            messagebox.showerror("Error", "Please select a doujinshi to delete!")
            return
        code = data.get("code")
        if not code:
            messagebox.showerror("Error", "Cannot delete: 'Code' column is hidden!")
            return
        confirm = messagebox.askyesno("Confirm", f"Are you sure you want to delete doujinshi with code {code}?")
        if confirm:
            try:
                self.cursor.execute("DELETE FROM color_attempt WHERE code = ?", (code,))
                self.cursor.execute("SELECT folder_path FROM color_subject WHERE code = ?", (code,))
                result = self.cursor.fetchone()
                if result:
                    folder_path = result[0]
                    full_path = os.path.join("doujinshi_collection", folder_path)
                    if os.path.exists(full_path):
                        try:
                            shutil.rmtree(full_path)
                        except OSError as e:
                            messagebox.showwarning("Warning", f"Failed to delete directory {full_path}: {e}")
                self.cursor.execute("DELETE FROM color_subject WHERE code = ?", (code,))
                self.conn.commit()
                self.dinamic_table.load_data()
                messagebox.showinfo("Success", f"Deleted doujinshi with code {code}")
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Database error: {e}")