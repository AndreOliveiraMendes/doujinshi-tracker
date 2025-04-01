# doujinshi_manager/screens/doujinshi_modify.py
import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import os

class DoujinshiModifyScreen(tk.Frame):
    def __init__(self, parent, controller, cursor, conn):
        super().__init__(parent)
        self.controller = controller  # Store controller for navigation
        self.cursor = cursor
        self.conn = conn
        tk.Label(self, text="Modify Doujinshi", font=("Arial", 14)).pack(pady=10)

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
            ("Series ID (leave blank to keep current):", "series_id_entry"),
            ("Part ID (leave blank to keep current):", "part_id_entry"),
            ("Series Name (leave blank to keep current):", "series_name_entry"),
            ("Series Alt Name (leave blank to keep current):", "series_alt_name_entry"),
            ("Part Name (leave blank to keep current):", "part_name_entry"),
            ("Part Alt Name (leave blank to keep current):", "part_alt_name_entry"),
            ("Origin (leave blank to keep current):", "origin_entry"),
            ("Artist (leave blank to keep current):", "artist_entry"),
            ("Tags (leave blank to keep current):", "tags_entry"),
            ("Folder Path (leave blank to keep current):", "folder_entry")
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

        tk.Button(button_frame, text="Modify", command=self.modify_doujinshi).pack(side="left", padx=5)
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

    def load_data(self, doujinshi_data):
        series_id, part_id, code, series_name, series_alt_name, part_name, part_alt_name, origin, artist, tags, folder_path = doujinshi_data
        self.code_entry.delete(0, tk.END)
        self.series_id_entry.delete(0, tk.END)
        self.part_id_entry.delete(0, tk.END)
        self.series_name_entry.delete(0, tk.END)
        self.series_alt_name_entry.delete(0, tk.END)
        self.part_name_entry.delete(0, tk.END)
        self.part_alt_name_entry.delete(0, tk.END)
        self.origin_entry.delete(0, tk.END)
        self.artist_entry.delete(0, tk.END)
        self.tags_entry.delete(0, tk.END)
        self.folder_entry.delete(0, tk.END)

        self.code_entry.insert(0, str(code))
        self.series_id_entry.insert(0, str(series_id))
        self.part_id_entry.insert(0, str(part_id) if part_id is not None else "")
        self.series_name_entry.insert(0, series_name if series_name is not None else "")
        self.series_alt_name_entry.insert(0, series_alt_name if series_alt_name is not None else "")
        self.part_name_entry.insert(0, part_name if part_name is not None else "")
        self.part_alt_name_entry.insert(0, part_alt_name if part_alt_name is not None else "")
        self.origin_entry.insert(0, origin if origin is not None else "")
        self.artist_entry.insert(0, artist if artist else "")
        self.tags_entry.insert(0, tags if tags else "")
        self.folder_entry.insert(0, folder_path if folder_path else "")

    def modify_doujinshi(self):
        code = self.code_entry.get()
        if not code:
            messagebox.showerror("Error", "Please enter a doujinshi code!")
            return

        try:
            code = int(code)
            self.cursor.execute("SELECT * FROM color_subject WHERE code = ?", (code,))
            result = self.cursor.fetchone()
            if not result:
                messagebox.showerror("Error", f"Doujinshi with code {code} not found!")
                return

            current_series_id, current_part_id, _, current_series_name, current_series_alt_name, current_part_name, current_part_alt_name, current_origin, current_artist, current_tags, current_folder_path = result

            series_id = self.series_id_entry.get()
            series_id = int(series_id) if series_id else current_series_id

            part_id = self.part_id_entry.get()
            part_id = int(part_id) if part_id else current_part_id

            series_name = self.series_name_entry.get()
            series_name = series_name if series_name else current_series_name

            series_alt_name = self.series_alt_name_entry.get()
            series_alt_name = series_alt_name if series_alt_name else current_series_alt_name

            part_name = self.part_name_entry.get()
            part_name = part_name if part_name else current_part_name

            part_alt_name = self.part_alt_name_entry.get()
            part_alt_name = part_alt_name if part_alt_name else current_part_alt_name

            origin = self.origin_entry.get()
            origin = origin if origin else current_origin

            artist = self.artist_entry.get()
            artist = artist if artist else current_artist

            tags = self.tags_entry.get()
            tags = tags if tags else current_tags

            folder_path = self.folder_entry.get()
            new_folder_path = folder_path if folder_path else current_folder_path

            self.cursor.execute("""
                UPDATE color_subject
                SET series_id = ?, part_id = ?, series_name = ?, series_alt_name = ?, part_name = ?, part_alt_name = ?, origin = ?, artist = ?, tags = ?, folder_path = ?
                WHERE code = ?
            """, (series_id, part_id, series_name, series_alt_name, part_name, part_alt_name, origin, artist, tags, new_folder_path, code))
            self.conn.commit()

            if folder_path and folder_path != current_folder_path:
                old_path = os.path.join("doujinshi_collection", current_folder_path)
                new_path = os.path.join("doujinshi_collection", folder_path)
                if os.path.exists(old_path):
                    os.rename(old_path, new_path)

            messagebox.showinfo("Success", f"Updated doujinshi with code {code}")
        except ValueError:
            messagebox.showerror("Error", "Code, Series ID, and Part ID must be numbers!")
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Database error: {e}")