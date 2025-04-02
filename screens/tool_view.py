# doujinshi_manager/screens/tool_view.py
import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3

class ToolViewScreen(tk.Frame):
    def __init__(self, parent, controller, cursor, conn):
        super().__init__(parent)
        self.controller = controller  # Store controller for navigation
        self.cursor = cursor
        self.conn = conn
        tk.Label(self, text="View Tools", font=("Arial", 14)).pack(pady=10)

        self.tree = ttk.Treeview(self, columns=("Tool ID", "Tool Name", "Tool URL"), show="headings")
        self.tree.heading("Tool ID", text="Tool ID")
        self.tree.heading("Tool Name", text="Tool Name")
        self.tree.heading("Tool URL", text="Tool URL")

        self.tree.column("Tool ID", width=60)
        self.tree.column("Tool Name", width=150)
        self.tree.column("Tool URL", width=200)

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y")

        self.load_data()

        tk.Button(self, text="Edit Selected", command=self.edit_selected).pack(pady=5)
        tk.Button(self, text="Delete Selected", command=self.delete_selected).pack(pady=5)
        tk.Button(self, text="Back", command=controller.go_back).pack(pady=5)
        tk.Button(self, text="Main Menu", command=controller.go_to_main_menu).pack(pady=5)

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.cursor.execute("SELECT tool_id, tool_name, tool_url FROM color_tool")
        rows = self.cursor.fetchall()
        for row in rows:
            self.tree.insert("", "end", values=row)

    def edit_selected(self):
        from .tool_modify import ToolModifyScreen  # Move import here
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a tool to edit!")
            return
        tool_id = self.tree.item(selected_item)["values"][0]
        self.cursor.execute("SELECT * FROM color_tool WHERE tool_id = ?", (tool_id,))
        tool_data = self.cursor.fetchone()
        if tool_data:
            self.controller.frames[ToolModifyScreen].load_data(tool_data)
            self.controller.show_frame(ToolModifyScreen)

    def delete_selected(self):
        from .attempt_insert import AttemptInsertScreen  # Move import here
        from .attempt_modify import AttemptModifyScreen  # Move import here
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a tool to delete!")
            return
        tool_id = self.tree.item(selected_item)["values"][0]
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