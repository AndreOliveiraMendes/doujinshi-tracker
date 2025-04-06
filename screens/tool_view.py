# doujinshi_manager/screens/tool_view.py
import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
from .utility import DinamicTable

class ToolViewScreen(tk.Frame):
    def __init__(self, parent, controller, cursor, conn):
        super().__init__(parent)
        self.controller = controller  # Store controller for navigation
        self.cursor = cursor
        self.conn = conn
        tk.Label(self, text="View Tools", font=("Arial", 14)).pack(pady=10)

        # Define table configuration
        table_config = {
            "table_name": "color_tool",
            "columns": ['tool_id', 'tool_name', 'tool_url'],
            "column_display_names": {
                'tool_id':'code',
                'tool_name': 'Name',
                'tool_url': 'URL'
            },
            "column_widths": {
                'tool_id': 60,
                'tool_name': 150,
                'tool_url': 200
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
        from .tool_modify import ToolModifyScreen  # Move import here
        data = self.dinamic_table.get_selected_data()
        if not data:
            messagebox.showerror("Error", "Please select a tool to edit!")
            return
        tool_id = data.get("tool_id")
        if not tool_id:
            messagebox.showerror("Error", "Cannot edit: 'Code' column is hidden!")
            return
        self.cursor.execute("SELECT * FROM color_tool WHERE tool_id = ?", (tool_id,))
        tool_data = self.cursor.fetchone()
        if tool_data:
            self.controller.frames[ToolModifyScreen].load_data(tool_data)
            self.controller.show_frame(ToolModifyScreen)

    def delete_selected(self):
        from .attempt_insert import AttemptInsertScreen  # Move import here
        from .attempt_modify import AttemptModifyScreen  # Move import here
        data = self.dinamic_table.get_selected_data()
        if not data:
            messagebox.showerror("Error", "Please select a tool to delete!")
            return
        tool_id = data.get("tool_id")
        if not tool_id:
            messagebox.showerror("Error", "Cannot delete: 'Code' column is hidden!")
            return
        confirm = messagebox.askyesno("Confirm", f"Are you sure you want to delete tool with ID {tool_id}?")
        if confirm:
            try:
                # Check if the tool is used in any attempts
                self.cursor.execute("SELECT 1 FROM color_attempt WHERE tool_id = ?", (tool_id,))
                if self.cursor.fetchone():
                    messagebox.showerror("Error", f"Cannot delete tool with ID {tool_id} because it is used in existing attempts!")
                    return

                self.cursor.execute("DELETE FROM color_tool WHERE tool_id = ?", (tool_id,))
                self.conn.commit()
                self.load_data()
                messagebox.showinfo("Success", f"Deleted tool with ID {tool_id}")

                # Refresh the tool dropdown in AttemptInsertScreen and AttemptModifyScreen
                for screen_class in (AttemptInsertScreen, AttemptModifyScreen):
                    screen = self.controller.frames.get(screen_class)
                    if screen and hasattr(screen, "refresh_tools"):
                        screen.refresh_tools()

            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Database error: {e}")