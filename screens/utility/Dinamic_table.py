# doujinshi_manager/widgets/dynamic_table.py
import tkinter as tk
from tkinter import ttk

class DinamicTable(tk.Frame):
    def __init__(self, parent, cursor, table_name, columns, column_display_names, column_widths, data_fetch_callback=None):
        super().__init__(parent)
        self.cursor = cursor
        self.table_name = table_name
        self.all_columns = columns
        self.column_display_names = column_display_names
        self.column_widths = column_widths
        self.data_fetch_callback = data_fetch_callback  # Optional callback to customize data fetching

        # Track which columns are currently visible
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

        # Initially load the data
        self.load_data()

        parent.load_data = self.load_data

    def update_columns(self):
        # Get the currently visible columns
        visible_cols = [col for col in self.all_columns if self.visible_columns[col].get()]

        # Save the current data
        current_data = []
        for item in self.tree.get_children():
            values = self.tree.item(item, "values")
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
            values = tuple(data_dict.get(col, "") for col in visible_cols)
            self.tree.insert("", "end", values=values)

        self.load_data()

    def load_data(self):
        # Fetch data using the callback if provided, otherwise use default query
        if self.data_fetch_callback:
            rows = self.data_fetch_callback()
        else:
            columns_str = ", ".join(self.all_columns)
            query = f"SELECT {columns_str} FROM {self.table_name}"
            self.cursor.execute(query)
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
            data_dict = {self.all_columns[i]: val for i, val in enumerate(row)}
            values = tuple(data_dict[col] for col in visible_cols)
            self.tree.insert("", "end", values=values)

    def get_selected_data(self):
        selected_item = self.tree.selection()
        if not selected_item:
            return None
        values = self.tree.item(selected_item)["values"]
        visible_cols = [col for col in self.all_columns if self.visible_columns[col].get()]
        data_dict = {visible_cols[i]: val for i, val in enumerate(values)}
        return data_dict