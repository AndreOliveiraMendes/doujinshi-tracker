# doujinshi_manager/screens/attempt_view.py
import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3

class AttemptViewScreen(tk.Frame):
    def __init__(self, parent, controller, cursor, conn):
        super().__init__(parent)
        self.controller = controller  # Store controller for navigation
        self.cursor = cursor
        self.conn = conn
        tk.Label(self, text="View Attempts", font=("Arial", 14)).pack(pady=10)

        self.tree = ttk.Treeview(self, columns=("Code", "Tool ID", "Folder Path", "Color Status", "Notes"), show="headings")
        self.tree.heading("Code", text="Code")
        self.tree.heading("Tool ID", text="Tool ID")
        self.tree.heading("Folder Path", text="Folder Path")
        self.tree.heading("Color Status", text="Color Status")
        self.tree.heading("Notes", text="Notes")

        self.tree.column("Code", width=60)
        self.tree.column("Tool ID", width=60)
        self.tree.column("Folder Path", width=100)
        self.tree.column("Color Status", width=100)
        self.tree.column("Notes", width=150)

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
        self.cursor.execute("SELECT code, tool_id, attempt_folder_path, attempt_color_status, attempt_notes FROM color_attempt")
        rows = self.cursor.fetchall()
        for row in rows:
            self.tree.insert("", "end", values=row)

    def edit_selected(self):
        from .attempt_modify import AttemptModifyScreen  # Move import here
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select an attempt to edit!")
            return
        code = self.tree.item(selected_item)["values"][0]
        tool_id = self.tree.item(selected_item)["values"][1]
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