import tkinter as tk
from tkinter import messagebox, ttk
def contruct_table_header(self, conf):

    all_columns = list(conf.keys())
    column_display_names = {}
    column_widths = {}
    for k, v in conf.items():
        column_display_names[k] = v["name"]
        column_widths[k] = v["width"]
    
    self.all_columns = all_columns
    self.column_display_names = column_display_names
    self.column_widths = column_widths

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
    tk.Button(self, text="Back", command=self.controller.go_back).pack(pady=5)
    tk.Button(self, text="Main Menu", command=self.controller.go_to_main_menu).pack(pady=5)

def contruct_table_updater():
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
    
    return update_columns