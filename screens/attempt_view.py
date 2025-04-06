# doujinshi_manager/screens/attempt_view.py
import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
from .utility import DinamicTable

class AttemptViewScreen(tk.Frame):
    def __init__(self, parent, controller, cursor, conn):
        super().__init__(parent)
        self.controller = controller  # Store controller for navigation
        self.cursor = cursor
        self.conn = conn
        tk.Label(self, text="View Attempts", font=("Arial", 14)).pack(pady=10)

        # Define table configuration
        # Define table configuration
        table_config = {
            "table_name": "color_attempt",
            "columns": ['code', 'tool_id', 'attempt_folder_path', 'attempt_color_status', 'attempt_notes'],
            "column_display_names": {
                'code': 'Doujinshi Code',
                'tool_id': 'Tool Code',
                'attempt_folder_path': 'Folder Path',
                'attempt_color_status': 'Color Status',
                'attempt_notes': 'Notes'
            },
            "column_widths": {
                'code':60 ,
                'tool_id':60 ,
                'attempt_folder_path':100 ,
                'attempt_color_status':100 ,
                'attempt_notes':150
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

        tk.Button(self, text="Edit Selected", command=self.edit_selected).pack(pady=5)
        tk.Button(self, text="Delete Selected", command=self.delete_selected).pack(pady=5)
        tk.Button(self, text="Back", command=controller.go_back).pack(pady=5)
        tk.Button(self, text="Main Menu", command=controller.go_to_main_menu).pack(pady=5)

    def edit_selected(self):
        from .attempt_modify import AttemptModifyScreen  # Move import here
        data = self.dinamic_table.get_selected_data()
        if not data:
            messagebox.showerror("Error", "Please select a attempt to edit!")
            return
        code = data.get("code")
        tool_id = data.get("tool_id")
        if not code or not tool_id:
            messagebox.showerror("Error", "Cannot edit: either of 'code' column are hide!")
            return
        self.cursor.execute("SELECT * FROM color_attempt WHERE code = ? AND tool_id = ?", (code, tool_id))
        attempt_data = self.cursor.fetchone()
        if attempt_data:
            self.controller.frames[AttemptModifyScreen].load_data(attempt_data)
            self.controller.show_frame(AttemptModifyScreen)

    def delete_selected(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select an attempt to delete!")
            return
        code = self.tree.item(selected_item)["values"][0]
        tool_id = self.tree.item(selected_item)["values"][1]
        confirm = messagebox.askyesno("Confirm", f"Are you sure you want to delete attempt for code {code} with tool ID {tool_id}?")
        if confirm:
            try:
                self.cursor.execute("DELETE FROM color_attempt WHERE code = ? AND tool_id = ?", (code, tool_id))
                self.conn.commit()
                self.load_data()
                messagebox.showinfo("Success", f"Deleted attempt for code {code} with tool ID {tool_id}")
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Database error: {e}")