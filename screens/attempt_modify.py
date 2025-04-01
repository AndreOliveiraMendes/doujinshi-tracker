# doujinshi_manager/screens/attempt_modify.py
import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import os

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
            ("Code:", "code_entry"),
            ("Tool ID:", "tool_id_entry"),
            ("Attempt Folder Path (leave blank to keep current):", "attempt_folder_path_entry"),
            ("Color Status (leave blank to keep current):", "attempt_color_status_entry"),
            ("Notes (leave blank to keep current):", "attempt_notes_entry")
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

        tk.Button(button_frame, text="Modify", command=self.modify_attempt).pack(side="left", padx=5)
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

    def load_data(self, attempt_data):
        code, tool_id, folder_path, status, notes = attempt_data
        self.code_entry.delete(0, tk.END)
        self.tool_id_entry.delete(0, tk.END)
        self.attempt_folder_path_entry.delete(0, tk.END)
        self.attempt_color_status_entry.delete(0, tk.END)
        self.attempt_notes_entry.delete(0, tk.END)

        self.code_entry.insert(0, str(code))
        self.tool_id_entry.insert(0, str(tool_id))
        self.attempt_folder_path_entry.insert(0, folder_path if folder_path is not None else "")
        self.attempt_color_status_entry.insert(0, status if status is not None else "")
        self.attempt_notes_entry.insert(0, notes if notes is not None else "")

    def modify_attempt(self):
        code = self.code_entry.get()
        tool_id = self.tool_id_entry.get()
        if not code or not tool_id:
            messagebox.showerror("Error", "Code and Tool ID are required!")
            return

        try:
            code = int(code)
            tool_id = int(tool_id)
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
            messagebox.showerror("Error", "Code and Tool ID must be numbers!")
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Database error: {e}")