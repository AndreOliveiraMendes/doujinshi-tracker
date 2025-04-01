# doujinshi_manager/screens/attempt_insert.py
import tkinter as tk
from tkinter import messagebox
import sqlite3  # Add sqlite3 import for exception handling

class AttemptInsertScreen(tk.Frame):
    def __init__(self, parent, controller, cursor, conn):
        super().__init__(parent)
        self.controller = controller  # Store controller for navigation
        self.cursor = cursor
        self.conn = conn
        tk.Label(self, text="Insert New Attempt", font=("Arial", 14)).pack(pady=10)

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
            ("Code (Doujinshi Code):", "code_entry"),
            ("Tool ID:", "tool_id_entry"),
            ("Attempt Folder Path (e.g., deepai):", "attempt_folder_path_entry"),
            ("Color Status (e.g., partial, complete, failed):", "attempt_color_status_entry"),
            ("Notes (optional):", "attempt_notes_entry")
        ]

        for i, (label_text, entry_name) in enumerate(fields):
            tk.Label(self.scrollable_frame, text=label_text).grid(row=i, column=0, sticky="w", padx=5, pady=2)
            setattr(self, entry_name, tk.Entry(self.scrollable_frame, width=40))
            getattr(self, entry_name).grid(row=i, column=1, sticky="ew", padx=5, pady=2)

        # Configure the grid to expand the entry fields
        self.scrollable_frame.grid_columnconfigure(1, weight=1)

        # Add buttons at the bottom
        button_frame = tk.Frame(self.scrollable_frame)
        button_frame.grid(row=len(fields), column=0, columnspan=2, pady=10)

        tk.Button(button_frame, text="Insert", command=self.insert_attempt).pack(side="left", padx=5)
        tk.Button(button_frame, text="Back", command=controller.go_back).pack(side="left", padx=5)
        tk.Button(button_frame, text="Main Menu", command=controller.go_to_main_menu).pack(side="left", padx=5)

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

    def insert_attempt(self):
        code = self.code_entry.get()
        tool_id = self.tool_id_entry.get()
        attempt_folder_path = self.attempt_folder_path_entry.get()
        attempt_color_status = self.attempt_color_status_entry.get()
        attempt_notes = self.attempt_notes_entry.get()

        if not code or not tool_id or not attempt_folder_path or not attempt_color_status:
            messagebox.showerror("Error", "Code, Tool ID, Attempt Folder Path, and Color Status are required!")
            return

        try:
            code = int(code)
            tool_id = int(tool_id)
            attempt_notes = attempt_notes if attempt_notes else None

            # Check if the doujinshi code exists
            self.cursor.execute("SELECT 1 FROM color_subject WHERE code = ?", (code,))
            if not self.cursor.fetchone():
                messagebox.showerror("Error", f"Doujinshi with code {code} does not exist!")
                return

            # Check if the tool_id exists
            self.cursor.execute("SELECT 1 FROM color_tool WHERE tool_id = ?", (tool_id,))
            if not self.cursor.fetchone():
                messagebox.showerror("Error", f"Tool with ID {tool_id} does not exist!")
                return

            self.cursor.execute("""
                INSERT INTO color_attempt (code, tool_id, attempt_folder_path, attempt_color_status, attempt_notes)
                VALUES (?, ?, ?, ?, ?)
            """, (code, tool_id, attempt_folder_path, attempt_color_status, attempt_notes))
            self.conn.commit()
            messagebox.showinfo("Success", f"Added attempt for code {code} with tool ID {tool_id}")
        except ValueError:
            messagebox.showerror("Error", "Code and Tool ID must be numbers!")
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Database error: {e}")