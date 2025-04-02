# doujinshi_manager/screens/doujinshi_insert.py
import tkinter as tk
from tkinter import messagebox
import sqlite3
import os
from .doujinshi_view import DoujinshiViewScreen  # Import DoujinshiViewScreen

class DoujinshiInsertScreen(tk.Frame):
    def __init__(self, parent, controller, cursor, conn):
        super().__init__(parent)
        self.controller = controller  # Store controller for navigation
        self.cursor = cursor
        self.conn = conn
        tk.Label(self, text="Insert New Doujinshi", font=("Arial", 14)).pack(pady=10)

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
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)  # Windows
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)    # Linux (scroll up)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)    # Linux (scroll down)

        # Use a grid layout for better alignment
        fields = [
            ("Series ID:", "series_id_entry"),
            ("Part ID (optional):", "part_id_entry"),
            ("Code (nhentai code):", "code_entry"),
            ("Series Name:", "series_name_entry"),
            ("Series Alt Name (optional):", "series_alt_name_entry"),
            ("Part Name (optional):", "part_name_entry"),
            ("Part Alt Name (optional):", "part_alt_name_entry"),
            ("Origin (optional):", "origin_entry"),
            ("Artist (optional):", "artist_entry"),
            ("Tags (optional, semicolon-separated):", "tags_entry"),
            ("Folder Path (e.g., c12):", "folder_entry")
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

        tk.Button(button_frame, text="Insert", command=self.insert_doujinshi).pack(side="left", padx=5)
        tk.Button(button_frame, text="Back", command=controller.go_back).pack(side="left", padx=5)
        tk.Button(button_frame, text="Main Menu", command=controller.go_to_main_menu).pack(side="left", padx=5)

    def _update_scrollregion(self, event=None):
        # Update the scroll region to encompass all content
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        # Update the width of the scrollable frame to match the canvas
        canvas_width = self.canvas.winfo_width()
        if canvas_width > 0:  # Ensure the canvas has a valid width
            self.canvas.itemconfig(self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw"), width=canvas_width)

    def _on_mousewheel(self, event):
        # Handle mouse wheel scrolling
        if event.num == 5 or event.delta < 0:  # Scroll down
            self.canvas.yview_scroll(1, "units")
        elif event.num == 4 or event.delta > 0:  # Scroll up
            self.canvas.yview_scroll(-1, "units")

    def insert_doujinshi(self):
        series_id = self.series_id_entry.get()
        part_id = self.part_id_entry.get()
        code = self.code_entry.get()
        series_name = self.series_name_entry.get()
        series_alt_name = self.series_alt_name_entry.get()
        part_name = self.part_name_entry.get()
        part_alt_name = self.part_alt_name_entry.get()
        origin = self.origin_entry.get()
        artist = self.artist_entry.get()
        tags = self.tags_entry.get()
        folder_path = self.folder_entry.get()

        if not series_id or not code or not series_name or not folder_path:
            messagebox.showerror("Error", "Series ID, Code, Series Name, and Folder Path are required!")
            return

        try:
            series_id = int(series_id)
            code = int(code)
            part_id = int(part_id) if part_id else None
            series_alt_name = series_alt_name if series_alt_name else None
            part_name = part_name if part_name else None
            part_alt_name = part_alt_name if part_alt_name else None
            origin = origin if origin else None
            artist = artist if artist else None
            tags = tags if tags else None

            self.cursor.execute("""
                INSERT INTO color_subject (series_id, part_id, code, series_name, series_alt_name, part_name, part_alt_name, origin, artist, tags, folder_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (series_id, part_id, code, series_name, series_alt_name, part_name, part_alt_name, origin, artist, tags, folder_path))
            self.conn.commit()

            full_path = os.path.join("doujinshi_collection", folder_path)
            os.makedirs(full_path, exist_ok=True)
            messagebox.showinfo("Success", f"Added doujinshi and created folder: {full_path}")

            # Refresh the DoujinshiViewScreen
            view_screen = self.controller.frames.get(DoujinshiViewScreen)
            if view_screen:
                view_screen.load_data()

            # Optionally, navigate back to the view screen
            self.controller.show_frame(DoujinshiViewScreen)

        except ValueError:
            messagebox.showerror("Error", "Series ID, Part ID, and Code must be numbers!")
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Database error: {e}")