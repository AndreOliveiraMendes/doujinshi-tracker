# doujinshi_manager/screens/attempt_modify.py
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk  # Import ttk for Combobox
import sqlite3

class AttemptModifyScreen(tk.Frame):
    def __init__(self, parent, controller, cursor, conn):
        super().__init__(parent)
        self.controller = controller  # Store controller for navigation
        self.cursor = cursor
        self.conn = conn
        tk.Label(self, text="Modify Attempt", font=("Arial", 14)).pack(pady=10)

        # Create a frame to hold the canvas and scrollbar
        self.canvas_frame = tk.Frame(self)
        self.canvas_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Create the canvas and scrollbar
        self.canvas = tk.Canvas(self.canvas_frame)
        self.scrollbar = tk.Scrollbar(self.canvas_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        # Configure the canvas
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Pack the canvas and scrollbar
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        # Add the scrollable frame to the canvas
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        # Update the scroll region when the scrollable frame changes size
        self.scrollable_frame.bind(
            "<Configure>",
            self._update_scrollregion
        )

        # Bind mouse wheel scrolling
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

        # Use a grid layout for better alignment
        fields = [
            ("Code:", "code_entry", tk.Entry),
            ("Tool:", "tool_combobox", None),  # We'll create the Combobox separately
            ("Attempt Folder Path (leave blank to keep current):", "attempt_folder_path_entry", tk.Entry),
            ("Color Status (leave blank to keep current):", "attempt_color_status_entry", tk.Entry),
            ("Notes (leave blank to keep current):", "attempt_notes_entry", tk.Entry)
        ]

        # Dictionary to store tool_id to tool_name mapping
        self.tool_map = {}
        self._load_tools()

        for i, (label_text, widget_name, widget_class) in enumerate(fields):
            tk.Label(self.scrollable_frame, text=label_text).grid(row=i, column=0, sticky="w", padx=5, pady=2)
            if widget_name == "tool_combobox":
                # Create a Combobox for tool selection
                self.tool_combobox = ttk.Combobox(self.scrollable_frame, values=list(self.tool_map.values()), width=37, state="readonly")
                self.tool_combobox.grid(row=i, column=1, sticky="ew", padx=5, pady=2)
            else:
                # Create Entry widgets for other fields
                setattr(self, widget_name, widget_class(self.scrollable_frame, width=40))
                getattr(self, widget_name).grid(row=i, column=1, sticky="ew", padx=5, pady=2)

        # Configure the grid to expand the entry fields
        self.scrollable_frame.grid_columnconfigure(1, weight=1)

        # Add buttons at the bottom
        button_frame = tk.Frame(self.scrollable_frame)
        button_frame.grid(row=len(fields), column=0, columnspan=2, pady=10)

        tk.Button(button_frame, text="Modify", command=self.modify_attempt).pack(side="left", padx=5)
        tk.Button(button_frame, text="Back", command=controller.go_back).pack(side="left", padx=5)
        tk.Button(button_frame, text="Main Menu", command=controller.go_to_main_menu).pack(side="left", padx=5)

    def _load_tools(self):
        """Load tools from the color_tool table into the tool_map dictionary."""
        try:
            self.cursor.execute("SELECT tool_id, tool_name FROM color_tool")
            tools = self.cursor.fetchall()
            self.tool_map = {tool_id: f"{tool_id} - {tool_name}" for tool_id, tool_name in tools}
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Failed to load tools: {e}")
            self.tool_map = {}

    def _update_scrollregion(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        canvas_width = self.canvas.winfo_width()
        if canvas_width > 0:
            self.canvas.itemconfig(self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw"), width=canvas_width)

    def _on_mousewheel(self, event):
        if event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")
        elif event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")

    def load_data(self, attempt_data):
        code, tool_id, folder_path, status, notes = attempt_data
        self.code_entry.delete(0, tk.END)
        self.attempt_folder_path_entry.delete(0, tk.END)
        self.attempt_color_status_entry.delete(0, tk.END)
        self.attempt_notes_entry.delete(0, tk.END)

        self.code_entry.insert(0, str(code))
        # Set the Combobox to the current tool_id
        if tool_id in self.tool_map:
            self.tool_combobox.set(self.tool_map[tool_id])
        else:
            self.tool_combobox.set("")
        self.attempt_folder_path_entry.insert(0, folder_path if folder_path is not None else "")
        self.attempt_color_status_entry.insert(0, status if status is not None else "")
        self.attempt_notes_entry.insert(0, notes if notes is not None else "")

    def modify_attempt(self):
        code = self.code_entry.get()
        # Get the selected tool from the Combobox
        selected_tool = self.tool_combobox.get()
        if not code or not selected_tool:
            messagebox.showerror("Error", "Code and Tool are required!")
            return

        try:
            code = int(code)
            # Extract tool_id from the selected tool string (format: "tool_id - tool_name")
            tool_id = int(selected_tool.split(" - ")[0])
            self.cursor.execute("SELECT * FROM color_attempt WHERE code = ? AND tool_id = ?", (code, tool_id))
            result = self.cursor.fetchone()
            if not result:
                messagebox.showerror("Error", f"Attempt for code {code} with tool ID {tool_id} not found!")
                return

            current_folder_path, current_status, current_notes = result[2], result[3], result[4]

            folder_path = self.attempt_folder_path_entry.get()
            folder_path = folder_path if folder_path else current_folder_path

            status = self.attempt_color_status_entry.get()
            status = status if status else current_status

            notes = self.attempt_notes_entry.get()
            notes = notes if notes else current_notes

            self.cursor.execute("""
                UPDATE color_attempt
                SET attempt_folder_path = ?, attempt_color_status = ?, attempt_notes = ?
                WHERE code = ? AND tool_id = ?
            """, (folder_path, status, notes, code, tool_id))
            self.conn.commit()
            messagebox.showinfo("Success", f"Updated attempt for code {code} with tool ID {tool_id}")
        except ValueError:
            messagebox.showerror("Error", "Code must be a number!")
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Database error: {e}")