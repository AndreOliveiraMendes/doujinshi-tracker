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

        # Define all possible columns and their display names
        self.all_columns = ["code", "series_id", "part_id", "series_name", "series_alt_name", "part_name", "part_alt_name", "origin", "artist", "folder_path"]
        self.column_display_names = {
            "code": "Code",
            "series_id": "Series ID",
            "part_id": "Part ID",
            "series_name": "Series Name",
            "series_alt_name": "Series Name*",
            "part_name": "Chapter Name",
            "part_alt_name": "Chapter Name*",
            "origin": "Origin",
            "artist": "Artist",
            "folder_path": "Folder Path"
        }
        self.column_widths = {
            "code": 60,
            "series_id": 40,
            "part_id": 40,
            "series_name": 150,
            "series_alt_name": 150,
            "part_name": 100,
            "part_alt_name": 100,
            "origin": 100,
            "artist": 100,
            "folder_path": 40
        }
        # Track which columns are currently visible (initially all are visible)
        self.visible_columns = {col: tk.BooleanVar(value=True) for col in self.all_columns}

        # Frame for column selection checkboxes
        self.checkbox_frame = ttk.LabelFrame(self, text="Select Columns to Show", padding=10)
        self.checkbox_frame.pack(fill="x", padx=5, pady=5)

        # Create a checkbox for each column
        for col in self.all_columns:
            chk = ttk.Checkbutton(
                self.checkbox_frame,
                text=self.column_display_names[col],
                variable=self.visible_columns[col],
                command=self.update_columns
            )
            chk.pack(side="left", padx=5)

        # Frame for the table
        self.table_frame = ttk.Frame(self)
        self.table_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Create the Treeview table
        self.tree = ttk.Treeview(self.table_frame, show="headings")
        self.tree.pack(fill="both", expand=True)

        # Add a scrollbar
        scrollbar = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Initially set up the columns (all visible)
        self.load_data()

        # Buttons for actions
        tk.Button(self, text="Edit Selected", command=self.edit_selected).pack(pady=5)
        tk.Button(self, text="Delete Selected", command=self.delete_selected).pack(pady=5)
        tk.Button(self, text="Back", command=controller.go_back).pack(pady=5)
        tk.Button(self, text="Main Menu", command=controller.go_to_main_menu).pack(pady=5)

    def update_columns(self):
        # Get the currently visible columns
        visible_cols = [col for col in self.all_columns if self.visible_columns[col].get()]

        # Save the current data
        current_data = []
        for item in self.tree.get_children():
            values = self.tree.item(item, "values")
            # Map the values back to their column names
            data_dict = {self.all_columns[i]: val for i, val in enumerate(values)}
            current_data.append(data_dict)

        # Clear the current Treeview
        self.tree.delete(*self.tree.get_children())

        # Update the columns in the Treeview
        self.tree["columns"] = visible_cols
        for col in visible_cols:
            self.tree.heading(col, text=self.column_display_names[col])
            self.tree.column(col, width=self.column_widths[col], anchor="w")

        # Repopulate the data with only the visible columns
        for data_dict in current_data:
            # Create a tuple of values for the visible columns only
            values = tuple(data_dict.get(col, "") for col in visible_cols)
            self.tree.insert("", "end", values=values)
        
        # Refresh Data

        self.load_data()

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