# doujinshi_manager/screens/doujinshi_view.py
import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import os
import shutil

class DoujinshiViewScreen(tk.Frame):
    def __init__(self, parent, controller, cursor, conn):
        super().__init__(parent)
        self.controller = controller  # Store controller for navigation
        self.cursor = cursor
        self.conn = conn
        tk.Label(self, text="View Doujinshi", font=("Arial", 14)).pack(pady=10)

        self.tree = ttk.Treeview(self, columns=("Code", "Series ID", "Part ID", "Series Name", "Origin", "Artist", "Folder Path"), show="headings")
        self.tree.heading("Code", text="Code")
        self.tree.heading("Series ID", text="Series ID")
        self.tree.heading("Part ID", text="Part ID")
        self.tree.heading("Series Name", text="Series Name")
        self.tree.heading("Origin", text="Origin")
        self.tree.heading("Artist", text="Artist")
        self.tree.heading("Folder Path", text="Folder Path")

        self.tree.column("Code", width=60)
        self.tree.column("Series ID", width=60)
        self.tree.column("Part ID", width=60)
        self.tree.column("Series Name", width=150)
        self.tree.column("Origin", width=100)
        self.tree.column("Artist", width=100)
        self.tree.column("Folder Path", width=100)

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
        self.cursor.execute("SELECT code, series_id, part_id, series_name, origin, artist, folder_path FROM color_subject")
        rows = self.cursor.fetchall()
        for row in rows:
            self.tree.insert("", "end", values=row)

    def edit_selected(self):
        from .doujinshi_modify import DoujinshiModifyScreen  # Move import here
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a doujinshi to edit!")
            return
        code = self.tree.item(selected_item)["values"][0]
        self.cursor.execute("SELECT * FROM color_subject WHERE code = ?", (code,))
        doujinshi_data = self.cursor.fetchone()
        if doujinshi_data:
            self.controller.frames[DoujinshiModifyScreen].load_data(doujinshi_data)
            self.controller.show_frame(DoujinshiModifyScreen)

    def delete_selected(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a doujinshi to delete!")
            return
        code = self.tree.item(selected_item)["values"][0]
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
                self.load_data()
                messagebox.showinfo("Success", f"Deleted doujinshi with code {code}")
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Database error: {e}")