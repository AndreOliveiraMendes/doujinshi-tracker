# doujinshi_manager/screens/attempt_insert.py
import tkinter as tk
from tkinter import ttk, messagebox
import os

class AttemptInsertScreen(tk.Frame):
    def __init__(self, parent, controller, cursor, conn):
        super().__init__(parent)
        self.controller = controller
        self.cursor = cursor
        self.conn = conn

        tk.Label(self, text="Insert Color Attempt", font=("Arial", 14)).pack(pady=10)

        # Fetch available codes from color_subject
        self.codes = self.load_codes()
        if not self.codes:
            tk.Label(self, text="No doujinshi available! Please insert a doujinshi first.").pack()
            tk.Button(self, text="Back", command=controller.go_back).pack(pady=5)
            tk.Button(self, text="Main Menu", command=controller.go_to_main_menu).pack(pady=5)
            return

        # Code dropdown
        tk.Label(self, text="Code").pack()
        self.code_var = tk.StringVar(value=self.codes[0])  # Default to the first code
        self.code_combobox = ttk.Combobox(self, textvariable=self.code_var, values=self.codes, state="readonly")
        self.code_combobox.pack()

        # Tool dropdown
        self.tools = self.load_tools()
        if not self.tools:
            tk.Label(self, text="No tools available! Please add a tool first.").pack()
            tk.Button(self, text="Back", command=controller.go_back).pack(pady=5)
            tk.Button(self, text="Main Menu", command=controller.go_to_main_menu).pack(pady=5)
            return

        tk.Label(self, text="Tool").pack()
        tool_names = list(self.tools.values())
        self.tool_var = tk.StringVar(value=tool_names[0])
        self.tool_combobox = ttk.Combobox(self, textvariable=self.tool_var, values=tool_names, state="readonly")
        self.tool_combobox.pack()

        # Attempt Folder Path (relative to color_subject folder_path)
        tk.Label(self, text="Attempt Folder Path (relative to doujinshi folder, e.g., 'deepai')").pack()
        self.attempt_folder_path_entry = tk.Entry(self)
        self.attempt_folder_path_entry.pack()
        self.attempt_folder_path_entry.insert(0, tool_names[0])  # Default to tool name

        # Attempt Color Status dropdown
        tk.Label(self, text="Attempt Color Status").pack()
        self.statuses = ["Pending", "Completed", "Failed"]
        self.status_var = tk.StringVar(value="Pending")  # Default to Pending
        self.status_combobox = ttk.Combobox(self, textvariable=self.status_var, values=self.statuses, state="readonly")
        self.status_combobox.pack()

        # Attempt Notes
        tk.Label(self, text="Attempt Notes").pack()
        self.attempt_notes_entry = tk.Entry(self)
        self.attempt_notes_entry.pack()

        tk.Button(self, text="Insert", command=self.insert_attempt).pack(pady=10)
        tk.Button(self, text="Back", command=controller.go_back).pack(pady=5)
        tk.Button(self, text="Main Menu", command=controller.go_to_main_menu).pack(pady=5)

    def load_codes(self):
        """Load all codes from the color_subject table."""
        try:
            self.cursor.execute("SELECT code FROM color_subject")
            codes = [str(row[0]) for row in self.cursor.fetchall()]
            return codes
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load codes: {e}")
            return []

    def load_tools(self):
        """Load available tools from the color_tool table."""
        try:
            self.cursor.execute("SELECT tool_id, tool_name FROM color_tool")
            tools = {row[0]: row[1] for row in self.cursor.fetchall()}
            return tools
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load tools: {e}")
            return {}

    def insert_attempt(self):
        """Insert a new attempt into the color_attempt table."""
        from .attempt_view import AttemptViewScreen
        code = self.code_var.get()
        tool_name = self.tool_var.get()
        tool_id = [tid for tid, tname in self.tools.items() if tname == tool_name][0]
        attempt_folder_path = self.attempt_folder_path_entry.get().strip()
        attempt_color_status = self.status_var.get()
        attempt_notes = self.attempt_notes_entry.get().strip()

        # Validate inputs
        if not code:
            messagebox.showerror("Error", "Code is required!")
            return
        if not tool_id:
            messagebox.showerror("Error", "Tool is required!")
            return
        if not attempt_folder_path:
            attempt_folder_path = tool_name  # Default to tool name if empty
            self.attempt_folder_path_entry.delete(0, tk.END)
            self.attempt_folder_path_entry.insert(0, attempt_folder_path)
        if not attempt_color_status:
            messagebox.showerror("Error", "Attempt color status is required!")
            return

        # Fetch the folder_path from color_subject to construct the full path
        self.cursor.execute("SELECT folder_path FROM color_subject WHERE code = ?", (code,))
        result = self.cursor.fetchone()
        if not result:
            messagebox.showerror("Error", "Invalid code!")
            return
        base_folder_path = result[0]  # e.g., c1 or c1/p1

        # Insert into the database (store only the relative attempt_folder_path)
        try:
            self.cursor.execute(
                "INSERT INTO color_attempt (code, tool_id, attempt_folder_path, attempt_color_status, attempt_notes) VALUES (?, ?, ?, ?, ?)",
                (code, tool_id, attempt_folder_path, attempt_color_status, attempt_notes)
            )
            self.conn.commit()

            # Create the attempt folder
            full_path = os.path.join("doujinshi_collection", base_folder_path, attempt_folder_path)
            os.makedirs(full_path, exist_ok=True)
            messagebox.showinfo("Success", "Attempt inserted successfully!")

            # Reflesh screen
            AttemptView_screen = self.controller.frames.get(AttemptViewScreen)
            if AttemptView_screen:
                AttemptView_screen.load_data()

            # optional, go to AttemptViewScreen
            self.controller.show_frame(AttemptViewScreen)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to insert attempt: {e}")
        except OSError as e:
            messagebox.showerror("Error", f"Failed to create attempt folder: {e}")