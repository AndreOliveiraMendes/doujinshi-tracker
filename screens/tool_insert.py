# doujinshi_manager/screens/tool_insert.py
import tkinter as tk
from tkinter import messagebox
import sqlite3
from .tool_view import ToolViewScreen
from .attempt_insert import AttemptInsertScreen  # Import to refresh dropdown
from .attempt_modify import AttemptModifyScreen  # Import to refresh dropdown

class ToolInsertScreen(tk.Frame):
    def __init__(self, parent, controller, cursor, conn):
        super().__init__(parent)
        self.controller = controller  # Store controller for navigation
        self.cursor = cursor
        self.conn = conn
        tk.Label(self, text="Insert New Tool", font=("Arial", 14)).pack(pady=10)

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
            ("Tool ID:", "tool_id_entry"),
            ("Tool Name:", "tool_name_entry"),
            ("Tool URL (optional):", "tool_url_entry")
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

        tk.Button(button_frame, text="Insert", command=self.insert_tool).pack(side="left", padx=5)
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

    def insert_tool(self):
        tool_id = self.tool_id_entry.get()
        tool_name = self.tool_name_entry.get()
        tool_url = self.tool_url_entry.get()

        if not tool_id or not tool_name:
            messagebox.showerror("Error", "Tool ID and Tool Name are required!")
            return

        try:
            tool_id = int(tool_id)
            tool_url = tool_url if tool_url else None

            self.cursor.execute("""
                INSERT INTO color_tool (tool_id, tool_name, tool_url)
                VALUES (?, ?, ?)
            """, (tool_id, tool_name, tool_url))
            self.conn.commit()
            messagebox.showinfo("Success", f"Added tool with ID {tool_id}")

            # Refresh the ToolViewScreen
            view_screen = self.controller.frames.get(ToolViewScreen)
            if view_screen:
                view_screen.dinamic_table.load_data()

            # Refresh the tool dropdown in AttemptInsertScreen and AttemptModifyScreen
            for screen_class in (AttemptInsertScreen, AttemptModifyScreen):
                screen = self.controller.frames.get(screen_class)
                if screen and hasattr(screen, "refresh_tools"):
                    screen.refresh_tools()

            # Navigate back to the view screen
            self.controller.show_frame(ToolViewScreen)

        except ValueError:
            messagebox.showerror("Error", "Tool ID must be a number!")
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Database error: {e}")