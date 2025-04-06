# doujinshi_manager/screens/doujinshi_view.py
import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import os
from .utility import *

class DoujinshiViewScreen(tk.Frame):
    def __init__(self, parent, controller, cursor, conn):
        super().__init__(parent)
        self.controller = controller  # Store controller for navigation
        self.cursor = cursor
        self.conn = conn
        conf = {"code":{"name":"code", "width":60},
        "series_id":{"name":"Series ID", "width":40},
        "part_id":{"name":"Part ID", "width":40},
        "series_name":{"name":"Series Name", "width":150},
        "series_alt_name":{"name":"Series Name*", "width":150},
        "part_name":{"name":"Chapter Name", "width":100},
        "part_alt_name":{"name":"Chapter Name*", "width":100},
        "origin":{"name":"Origin", "width":100},
        "artist":{"name":"Artist", "width":100},
        "folder_path":{"name":"Folder Path", "width":40}}
        contruct_table_header(self, conf)
    
        tk.Label(self, text="View Doujinshi", font=("Arial", 14)).pack(pady=10)

    update_columns = contruct_table_updater()

    def load_data(self):
        # Fetch all data from the database
        self.cursor.execute("SELECT code, series_id, part_id, series_name, series_alt_name, part_name, part_alt_name, origin, artist, folder_path FROM color_subject")
        rows = self.cursor.fetchall()

        # Clear the current Treeview
        self.tree.delete(*self.tree.get_children())

        # Get the currently visible columns
        visible_cols = [col for col in self.all_columns if self.visible_columns[col].get()]

        # Set up the columns in the Treeview
        self.tree["columns"] = visible_cols
        for col in visible_cols:
            self.tree.heading(col, text=self.column_display_names[col])
            self.tree.column(col, width=self.column_widths[col], anchor="w")

        # Insert the data
        for row in rows:
            # Map the row to a dictionary for easier column access
            data_dict = {
                "code": row[0],
                "series_id": row[1],
                "part_id": row[2],
                "series_name": row[3],
                "series_alt_name": row[4],
                "part_name": row[5],
                "part_alt_name": row[6],
                "origin": row[7],
                "artist": row[8],
                "folder_path": row[9]
            }
            # Create a tuple of values for the visible columns only
            values = tuple(data_dict[col] for col in visible_cols)
            self.tree.insert("", "end", values=values)

    def edit_selected(self):
        from .doujinshi_modify import DoujinshiModifyScreen  # Move import here
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a doujinshi to edit!")
            return
        # Get the code from the selected row (it might not be the first column if columns are hidden)
        values = self.tree.item(selected_item)["values"]
        visible_cols = [col for col in self.all_columns if self.visible_columns[col].get()]
        data_dict = {visible_cols[i]: val for i, val in enumerate(values)}
        code = data_dict.get("code")  # Safely get the code
        if not code:
            messagebox.showerror("Error", "Cannot edit: 'Code' column is hidden!")
            return
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
        # Get the code from the selected row (it might not be the first column if columns are hidden)
        values = self.tree.item(selected_item)["values"]
        visible_cols = [col for col in self.all_columns if self.visible_columns[col].get()]
        data_dict = {visible_cols[i]: val for i, val in enumerate(values)}
        code = data_dict.get("code")  # Safely get the code
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
                self.load_data()
                messagebox.showinfo("Success", f"Deleted doujinshi with code {code}")
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Database error: {e}")