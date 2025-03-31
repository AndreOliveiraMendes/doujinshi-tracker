import sqlite3
import os
import tkinter as tk
from tkinter import messagebox, ttk

# Connect to the database
db_path = "db/tracker.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Main application class with navigation
class DoujinshiManagerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Doujinshi Colorization Manager")
        self.geometry("600x400")

        # Stack to keep track of navigation history
        self.history = []

        # Container to hold all frames (screens)
        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)

        # Dictionary to store all frames
        self.frames = {}

        # Create all screens (frames)
        for F in (MainMenu, DatabaseMenu, DirectoryMenu,
                  DoujinshiMenu, DoujinshiViewScreen, DoujinshiInsertScreen, DoujinshiModifyScreen,
                  AttemptMenu, AttemptViewScreen, AttemptInsertScreen, AttemptModifyScreen,
                  ToolMenu, ToolViewScreen, ToolInsertScreen, ToolModifyScreen):
            frame = F(self.container, self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Show the main menu initially
        self.show_frame("MainMenu")

    def show_frame(self, frame_name):
        """Show a frame and add it to the navigation history."""
        frame = self.frames[frame_name]
        if frame_name != "MainMenu" or len(self.history) > 0:
            self.history.append(frame_name)
        frame.tkraise()

    def go_back(self):
        """Go back to the previous frame."""
        if len(self.history) <= 1:
            messagebox.showinfo("Info", "No previous screen to go back to!")
            return
        self.history.pop()
        previous_frame = self.history[-1]
        self.frames[previous_frame].tkraise()

    def go_to_main_menu(self):
        """Go back to the main menu and clear history."""
        self.history = []
        self.show_frame("MainMenu")

# Main Menu Screen
class MainMenu(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        tk.Label(self, text="Doujinshi Colorization Manager", font=("Arial", 16)).pack(pady=20)

        tk.Button(self, text="Manage Database", command=lambda: controller.show_frame("DatabaseMenu")).pack(pady=10)
        tk.Button(self, text="Manage Directories", command=lambda: controller.show_frame("DirectoryMenu")).pack(pady=10)
        tk.Button(self, text="Exit", command=controller.quit).pack(pady=10)

# Database Menu Screen
class DatabaseMenu(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        tk.Label(self, text="Manage Database", font=("Arial", 14)).pack(pady=20)

        tk.Button(self, text="Manage Doujinshi", command=lambda: controller.show_frame("DoujinshiMenu")).pack(pady=5)
        tk.Button(self, text="Manage Attempts", command=lambda: controller.show_frame("AttemptMenu")).pack(pady=5)
        tk.Button(self, text="Manage Tools", command=lambda: controller.show_frame("ToolMenu")).pack(pady=5)
        tk.Button(self, text="Back", command=controller.go_back).pack(pady=5)
        tk.Button(self, text="Main Menu", command=controller.go_to_main_menu).pack(pady=5)

# Directory Menu Screen
class DirectoryMenu(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        tk.Label(self, text="Manage Directories", font=("Arial", 14)).pack(pady=20)

        tk.Button(self, text="Create Directory", command=self.create_directory).pack(pady=5)
        tk.Button(self, text="Delete Directory", command=self.delete_directory).pack(pady=5)
        tk.Button(self, text="Back", command=controller.go_back).pack(pady=5)
        tk.Button(self, text="Main Menu", command=controller.go_to_main_menu).pack(pady=5)

    def create_directory(self):
        folder_path = tk.simpledialog.askstring("Input", "Enter folder path (e.g., c12):", parent=self)
        if not folder_path:
            return
        full_path = os.path.join("doujinshi_collection", folder_path)
        try:
            os.makedirs(full_path, exist_ok=True)
            messagebox.showinfo("Success", f"Created directory: {full_path}")
        except OSError as e:
            messagebox.showerror("Error", f"Failed to create directory: {e}")

    def delete_directory(self):
        folder_path = tk.simpledialog.askstring("Input", "Enter folder path to delete (e.g., c12):", parent=self)
        if not folder_path:
            return
        full_path = os.path.join("doujinshi_collection", folder_path)
        if not os.path.exists(full_path):
            messagebox.showerror("Error", f"Directory {full_path} does not exist!")
            return
        confirm = messagebox.askyesno("Confirm", f"Are you sure you want to delete {full_path}?")
        if confirm:
            try:
                os.rmtree(full_path)
                messagebox.showinfo("Success", f"Deleted directory: {full_path}")
            except OSError as e:
                messagebox.showerror("Error", f"Failed to delete directory: {e}")

# Doujinshi Menu Screen (for color_subject)
class DoujinshiMenu(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        tk.Label(self, text="Manage Doujinshi", font=("Arial", 14)).pack(pady=20)

        tk.Button(self, text="View Doujinshi", command=lambda: controller.show_frame("DoujinshiViewScreen")).pack(pady=5)
        tk.Button(self, text="Insert Doujinshi", command=lambda: controller.show_frame("DoujinshiInsertScreen")).pack(pady=5)
        tk.Button(self, text="Back", command=controller.go_back).pack(pady=5)
        tk.Button(self, text="Main Menu", command=controller.go_to_main_menu).pack(pady=5)

# Doujinshi View Screen
class DoujinshiViewScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        tk.Label(self, text="View Doujinshi", font=("Arial", 14)).pack(pady=10)

        self.tree = ttk.Treeview(self, columns=("Code", "Series ID", "Part ID", "Series Name", "Origin", "Artist", "Folder Path"), show="headings")
        self.tree.heading("Code", text="Code")
        self.tree.heading("Series ID", text="Series ID")
        self.tree.heading("Part ID", text="Part ID")
        self.tree.heading("Series Name", text="Series Name")
        self.tree.heading("Origin", text="Origin")
        self.tree.heading("Artist", text="Artist")
        self.tree.heading("Folder Path", text="Folder Path")

        self.tree.column("Code", width=60)
        self.tree.column("Series ID", width=60)
        self.tree.column("Part ID", width=60)
        self.tree.column("Series Name", width=150)
        self.tree.column("Origin", width=100)
        self.tree.column("Artist", width=100)
        self.tree.column("Folder Path", width=100)

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y")

        self.load_data()

        tk.Button(self, text="Edit Selected", command=lambda: self.edit_selected(controller)).pack(pady=5)
        tk.Button(self, text="Delete Selected", command=self.delete_selected).pack(pady=5)
        tk.Button(self, text="Back", command=controller.go_back).pack(pady=5)
        tk.Button(self, text="Main Menu", command=controller.go_to_main_menu).pack(pady=5)

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        cursor.execute("SELECT code, series_id, part_id, series_name, origin, artist, folder_path FROM color_subject")
        rows = cursor.fetchall()
        for row in rows:
            self.tree.insert("", "end", values=row)

    def edit_selected(self, controller):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a doujinshi to edit!")
            return
        code = self.tree.item(selected_item)["values"][0]
        cursor.execute("SELECT * FROM color_subject WHERE code = ?", (code,))
        doujinshi_data = cursor.fetchone()
        if doujinshi_data:
            controller.frames["DoujinshiModifyScreen"].load_data(doujinshi_data)
            controller.show_frame("DoujinshiModifyScreen")

    def delete_selected(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a doujinshi to delete!")
            return
        code = self.tree.item(selected_item)["values"][0]
        confirm = messagebox.askyesno("Confirm", f"Are you sure you want to delete doujinshi with code {code}?")
        if confirm:
            try:
                cursor.execute("DELETE FROM color_attempt WHERE code = ?", (code,))
                cursor.execute("SELECT folder_path FROM color_subject WHERE code = ?", (code,))
                result = cursor.fetchone()
                if result:
                    folder_path = result[0]
                    full_path = os.path.join("doujinshi_collection", folder_path)
                    if os.path.exists(full_path):
                        os.rmtree(full_path)
                cursor.execute("DELETE FROM color_subject WHERE code = ?", (code,))
                conn.commit()
                self.load_data()
                messagebox.showinfo("Success", f"Deleted doujinshi with code {code}")
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Database error: {e}")

# Doujinshi Insert Screen
class DoujinshiInsertScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        tk.Label(self, text="Insert New Doujinshi", font=("Arial", 14)).pack(pady=10)

        self.canvas = tk.Canvas(self)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        tk.Label(self.scrollable_frame, text="Series ID:").pack()
        self.series_id_entry = tk.Entry(self.scrollable_frame)
        self.series_id_entry.pack()

        tk.Label(self.scrollable_frame, text="Part ID (optional):").pack()
        self.part_id_entry = tk.Entry(self.scrollable_frame)
        self.part_id_entry.pack()

        tk.Label(self.scrollable_frame, text="Code (nhentai code):").pack()
        self.code_entry = tk.Entry(self.scrollable_frame)
        self.code_entry.pack()

        tk.Label(self.scrollable_frame, text="Series Name:").pack()
        self.series_name_entry = tk.Entry(self.scrollable_frame)
        self.series_name_entry.pack()

        tk.Label(self.scrollable_frame, text="Series Alt Name (optional):").pack()
        self.series_alt_name_entry = tk.Entry(self.scrollable_frame)
        self.series_alt_name_entry.pack()

        tk.Label(self.scrollable_frame, text="Part Name (optional):").pack()
        self.part_name_entry = tk.Entry(self.scrollable_frame)
        self.part_name_entry.pack()

        tk.Label(self.scrollable_frame, text="Part Alt Name (optional):").pack()
        self.part_alt_name_entry = tk.Entry(self.scrollable_frame)
        self.part_alt_name_entry.pack()

        tk.Label(self.scrollable_frame, text="Origin (optional):").pack()
        self.origin_entry = tk.Entry(self.scrollable_frame)
        self.origin_entry.pack()

        tk.Label(self.scrollable_frame, text="Artist (optional):").pack()
        self.artist_entry = tk.Entry(self.scrollable_frame)
        self.artist_entry.pack()

        tk.Label(self.scrollable_frame, text="Tags (optional, semicolon-separated):").pack()
        self.tags_entry = tk.Entry(self.scrollable_frame)
        self.tags_entry.pack()

        tk.Label(self.scrollable_frame, text="Folder Path (e.g., c12):").pack()
        self.folder_entry = tk.Entry(self.scrollable_frame)
        self.folder_entry.pack()

        tk.Button(self.scrollable_frame, text="Insert", command=self.insert_doujinshi).pack(pady=5)
        tk.Button(self.scrollable_frame, text="Back", command=controller.go_back).pack(pady=5)
        tk.Button(self.scrollable_frame, text="Main Menu", command=controller.go_to_main_menu).pack(pady=5)

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

            cursor.execute("""
                INSERT INTO color_subject (series_id, part_id, code, series_name, series_alt_name, part_name, part_alt_name, origin, artist, tags, folder_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (series_id, part_id, code, series_name, series_alt_name, part_name, part_alt_name, origin, artist, tags, folder_path))
            conn.commit()

            full_path = os.path.join("doujinshi_collection", folder_path)
            os.makedirs(full_path, exist_ok=True)
            messagebox.showinfo("Success", f"Added doujinshi and created folder: {full_path}")
        except ValueError:
            messagebox.showerror("Error", "Series ID, Part ID, and Code must be numbers!")
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Database error: {e}")

# Doujinshi Modify Screen
class DoujinshiModifyScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        tk.Label(self, text="Modify Doujinshi", font=("Arial", 14)).pack(pady=10)

        self.canvas = tk.Canvas(self)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        tk.Label(self.scrollable_frame, text="Code:").pack()
        self.code_entry = tk.Entry(self.scrollable_frame)
        self.code_entry.pack()

        tk.Label(self.scrollable_frame, text="Series ID (leave blank to keep current):").pack()
        self.series_id_entry = tk.Entry(self.scrollable_frame)
        self.series_id_entry.pack()

        tk.Label(self.scrollable_frame, text="Part ID (leave blank to keep current):").pack()
        self.part_id_entry = tk.Entry(self.scrollable_frame)
        self.part_id_entry.pack()

        tk.Label(self.scrollable_frame, text="Series Name (leave blank to keep current):").pack()
        self.series_name_entry = tk.Entry(self.scrollable_frame)
        self.series_name_entry.pack()

        tk.Label(self.scrollable_frame, text="Series Alt Name (leave blank to keep current):").pack()
        self.series_alt_name_entry = tk.Entry(self.scrollable_frame)
        self.series_alt_name_entry.pack()

        tk.Label(self.scrollable_frame, text="Part Name (leave blank to keep current):").pack()
        self.part_name_entry = tk.Entry(self.scrollable_frame)
        self.part_name_entry.pack()

        tk.Label(self.scrollable_frame, text="Part Alt Name (leave blank to keep current):").pack()
        self.part_alt_name_entry = tk.Entry(self.scrollable_frame)
        self.part_alt_name_entry.pack()

        tk.Label(self.scrollable_frame, text="Origin (leave blank to keep current):").pack()
        self.origin_entry = tk.Entry(self.scrollable_frame)
        self.origin_entry.pack()

        tk.Label(self.scrollable_frame, text="Artist (leave blank to keep current):").pack()
        self.artist_entry = tk.Entry(self.scrollable_frame)
        self.artist_entry.pack()

        tk.Label(self.scrollable_frame, text="Tags (leave blank to keep current):").pack()
        self.tags_entry = tk.Entry(self.scrollable_frame)
        self.tags_entry.pack()

        tk.Label(self.scrollable_frame, text="Folder Path (leave blank to keep current):").pack()
        self.folder_entry = tk.Entry(self.scrollable_frame)
        self.folder_entry.pack()

        tk.Button(self.scrollable_frame, text="Modify", command=self.modify_doujinshi).pack(pady=5)
        tk.Button(self.scrollable_frame, text="Back", command=controller.go_back).pack(pady=5)
        tk.Button(self.scrollable_frame, text="Main Menu", command=controller.go_to_main_menu).pack(pady=5)

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
        self.artist_entry.insert(0, artist if artist is not None else "")
        self.tags_entry.insert(0, tags if tags is not None else "")
        self.folder_entry.insert(0, folder_path if folder_path is not None else "")

    def modify_doujinshi(self):
        code = self.code_entry.get()
        if not code:
            messagebox.showerror("Error", "Please enter a doujinshi code!")
            return

        try:
            code = int(code)
            cursor.execute("SELECT * FROM color_subject WHERE code = ?", (code,))
            result = cursor.fetchone()
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

            cursor.execute("""
                UPDATE color_subject
                SET series_id = ?, part_id = ?, series_name = ?, series_alt_name = ?, part_name = ?, part_alt_name = ?, origin = ?, artist = ?, tags = ?, folder_path = ?
                WHERE code = ?
            """, (series_id, part_id, series_name, series_alt_name, part_name, part_alt_name, origin, artist, tags, new_folder_path, code))
            conn.commit()

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

# Attempt Menu Screen (for color_attempt)
class AttemptMenu(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        tk.Label(self, text="Manage Attempts", font=("Arial", 14)).pack(pady=20)

        tk.Button(self, text="View Attempts", command=lambda: controller.show_frame("AttemptViewScreen")).pack(pady=5)
        tk.Button(self, text="Insert Attempt", command=lambda: controller.show_frame("AttemptInsertScreen")).pack(pady=5)
        tk.Button(self, text="Back", command=controller.go_back).pack(pady=5)
        tk.Button(self, text="Main Menu", command=controller.go_to_main_menu).pack(pady=5)

# Attempt View Screen
class AttemptViewScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        tk.Label(self, text="View Attempts", font=("Arial", 14)).pack(pady=10)

        self.tree = ttk.Treeview(self, columns=("Code", "Tool ID", "Folder Path", "Status", "Notes"), show="headings")
        self.tree.heading("Code", text="Code")
        self.tree.heading("Tool ID", text="Tool ID")
        self.tree.heading("Folder Path", text="Folder Path")
        self.tree.heading("Status", text="Status")
        self.tree.heading("Notes", text="Notes")

        self.tree.column("Code", width=60)
        self.tree.column("Tool ID", width=60)
        self.tree.column("Folder Path", width=100)
        self.tree.column("Status", width=80)
        self.tree.column("Notes", width=200)

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y")

        self.load_data()

        tk.Button(self, text="Edit Selected", command=lambda: self.edit_selected(controller)).pack(pady=5)
        tk.Button(self, text="Delete Selected", command=self.delete_selected).pack(pady=5)
        tk.Button(self, text="Back", command=controller.go_back).pack(pady=5)
        tk.Button(self, text="Main Menu", command=controller.go_to_main_menu).pack(pady=5)

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        cursor.execute("SELECT code, tool_id, attempt_folder_path, attempt_color_status, attempt_notes FROM color_attempt")
        rows = cursor.fetchall()
        for row in rows:
            self.tree.insert("", "end", values=row)

    def edit_selected(self, controller):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select an attempt to edit!")
            return
        code = self.tree.item(selected_item)["values"][0]
        tool_id = self.tree.item(selected_item)["values"][1]
        cursor.execute("SELECT * FROM color_attempt WHERE code = ? AND tool_id = ?", (code, tool_id))
        attempt_data = cursor.fetchone()
        if attempt_data:
            controller.frames["AttemptModifyScreen"].load_data(attempt_data)
            controller.show_frame("AttemptModifyScreen")

    def delete_selected(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select an attempt to delete!")
            return
        code = self.tree.item(selected_item)["values"][0]
        tool_id = self.tree.item(selected_item)["values"][1]
        confirm = messagebox.askyesno("Confirm", f"Are you sure you want to delete attempt for code {code} with tool ID {tool_id}?")
        if confirm:
            try:
                cursor.execute("DELETE FROM color_attempt WHERE code = ? AND tool_id = ?", (code, tool_id))
                conn.commit()
                self.load_data()
                messagebox.showinfo("Success", f"Deleted attempt for code {code} with tool ID {tool_id}")
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Database error: {e}")

# Attempt Insert Screen
class AttemptInsertScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        tk.Label(self, text="Insert New Attempt", font=("Arial", 14)).pack(pady=10)

        tk.Label(self, text="Code (Doujinshi Code):").pack()
        self.code_entry = tk.Entry(self)
        self.code_entry.pack()

        tk.Label(self, text="Tool ID:").pack()
        self.tool_id_entry = tk.Entry(self)
        self.tool_id_entry.pack()

        tk.Label(self, text="Attempt Folder Path (e.g., deepai):").pack()
        self.folder_path_entry = tk.Entry(self)
        self.folder_path_entry.pack()

        tk.Label(self, text="Color Status (e.g., partial, complete, failed):").pack()
        self.status_entry = tk.Entry(self)
        self.status_entry.pack()

        tk.Label(self, text="Notes (optional):").pack()
        self.notes_entry = tk.Entry(self)
        self.notes_entry.pack()

        tk.Button(self, text="Insert", command=self.insert_attempt).pack(pady=5)
        tk.Button(self, text="Back", command=controller.go_back).pack(pady=5)
        tk.Button(self, text="Main Menu", command=controller.go_to_main_menu).pack(pady=5)

    def insert_attempt(self):
        code = self.code_entry.get()
        tool_id = self.tool_id_entry.get()
        folder_path = self.folder_path_entry.get()
        status = self.status_entry.get()
        notes = self.notes_entry.get()

        if not code or not tool_id or not folder_path or not status:
            messagebox.showerror("Error", "Code, Tool ID, Folder Path, and Status are required!")
            return

        try:
            code = int(code)
            tool_id = int(tool_id)
            notes = notes if notes else None

            # Check if the doujinshi code exists
            cursor.execute("SELECT 1 FROM color_subject WHERE code = ?", (code,))
            if not cursor.fetchone():
                messagebox.showerror("Error", f"Doujinshi with code {code} does not exist!")
                return

            # Check if the tool_id exists
            cursor.execute("SELECT 1 FROM color_tool WHERE id = ?", (tool_id,))
            if not cursor.fetchone():
                messagebox.showerror("Error", f"Tool with ID {tool_id} does not exist!")
                return

            cursor.execute("""
                INSERT INTO color_attempt (code, tool_id, attempt_folder_path, attempt_color_status, attempt_notes)
                VALUES (?, ?, ?, ?, ?)
            """, (code, tool_id, folder_path, status, notes))
            conn.commit()
            messagebox.showinfo("Success", f"Added attempt for code {code} with tool ID {tool_id}")
        except ValueError:
            messagebox.showerror("Error", "Code and Tool ID must be numbers!")
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Database error: {e}")

# Attempt Modify Screen
class AttemptModifyScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        tk.Label(self, text="Modify Attempt", font=("Arial", 14)).pack(pady=10)

        tk.Label(self, text="Code:").pack()
        self.code_entry = tk.Entry(self)
        self.code_entry.pack()

        tk.Label(self, text="Tool ID:").pack()
        self.tool_id_entry = tk.Entry(self)
        self.tool_id_entry.pack()

        tk.Label(self, text="Attempt Folder Path (leave blank to keep current):").pack()
        self.folder_path_entry = tk.Entry(self)
        self.folder_path_entry.pack()

        tk.Label(self, text="Color Status (leave blank to keep current):").pack()
        self.status_entry = tk.Entry(self)
        self.status_entry.pack()

        tk.Label(self, text="Notes (leave blank to keep current):").pack()
        self.notes_entry = tk.Entry(self)
        self.notes_entry.pack()

        tk.Button(self, text="Modify", command=self.modify_attempt).pack(pady=5)
        tk.Button(self, text="Back", command=controller.go_back).pack(pady=5)
        tk.Button(self, text="Main Menu", command=controller.go_to_main_menu).pack(pady=5)

    def load_data(self, attempt_data):
        code, tool_id, folder_path, status, notes = attempt_data
        self.code_entry.delete(0, tk.END)
        self.tool_id_entry.delete(0, tk.END)
        self.folder_path_entry.delete(0, tk.END)
        self.status_entry.delete(0, tk.END)
        self.notes_entry.delete(0, tk.END)

        self.code_entry.insert(0, str(code))
        self.tool_id_entry.insert(0, str(tool_id))
        self.folder_path_entry.insert(0, folder_path if folder_path is not None else "")
        self.status_entry.insert(0, status if status is not None else "")
        self.notes_entry.insert(0, notes if notes is not None else "")

    def modify_attempt(self):
        code = self.code_entry.get()
        tool_id = self.tool_id_entry.get()
        if not code or not tool_id:
            messagebox.showerror("Error", "Code and Tool ID are required!")
            return

        try:
            code = int(code)
            tool_id = int(tool_id)
            cursor.execute("SELECT * FROM color_attempt WHERE code = ? AND tool_id = ?", (code, tool_id))
            result = cursor.fetchone()
            if not result:
                messagebox.showerror("Error", f"Attempt for code {code} with tool ID {tool_id} not found!")
                return

            current_folder_path, current_status, current_notes = result[2], result[3], result[4]

            folder_path = self.folder_path_entry.get()
            folder_path = folder_path if folder_path else current_folder_path

            status = self.status_entry.get()
            status = status if status else current_status

            notes = self.notes_entry.get()
            notes = notes if notes else current_notes

            cursor.execute("""
                UPDATE color_attempt
                SET attempt_folder_path = ?, attempt_color_status = ?, attempt_notes = ?
                WHERE code = ? AND tool_id = ?
            """, (folder_path, status, notes, code, tool_id))
            conn.commit()
            messagebox.showinfo("Success", f"Updated attempt for code {code} with tool ID {tool_id}")
        except ValueError:
            messagebox.showerror("Error", "Code and Tool ID must be numbers!")
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Database error: {e}")

# Tool Menu Screen (for color_tool)
class ToolMenu(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        tk.Label(self, text="Manage Tools", font=("Arial", 14)).pack(pady=20)

        tk.Button(self, text="View Tools", command=lambda: controller.show_frame("ToolViewScreen")).pack(pady=5)
        tk.Button(self, text="Insert Tool", command=lambda: controller.show_frame("ToolInsertScreen")).pack(pady=5)
        tk.Button(self, text="Back", command=controller.go_back).pack(pady=5)
        tk.Button(self, text="Main Menu", command=controller.go_to_main_menu).pack(pady=5)

# Tool View Screen
class ToolViewScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        tk.Label(self, text="View Tools", font=("Arial", 14)).pack(pady=10)

        self.tree = ttk.Treeview(self, columns=("Tool ID", "Tool Name", "Tool URL"), show="headings")
        self.tree.heading("Tool ID", text="Tool ID")
        self.tree.heading("Tool Name", text="Tool Name")
        self.tree.heading("Tool URL", text="Tool URL")

        self.tree.column("Tool ID", width=60)
        self.tree.column("Tool Name", width=150)
        self.tree.column("Tool URL", width=300)

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y")

        self.load_data()

        tk.Button(self, text="Edit Selected", command=lambda: self.edit_selected(controller)).pack(pady=5)
        tk.Button(self, text="Delete Selected", command=self.delete_selected).pack(pady=5)
        tk.Button(self, text="Back", command=controller.go_back).pack(pady=5)
        tk.Button(self, text="Main Menu", command=controller.go_to_main_menu).pack(pady=5)

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        cursor.execute("SELECT id, name, url FROM color_tool")
        rows = cursor.fetchall()
        for row in rows:
            self.tree.insert("", "end", values=row)

    def edit_selected(self, controller):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a tool to edit!")
            return
        tool_id = self.tree.item(selected_item)["values"][0]
        cursor.execute("SELECT * FROM color_tool WHERE id = ?", (tool_id,))
        tool_data = cursor.fetchone()
        if tool_data:
            controller.frames["ToolModifyScreen"].load_data(tool_data)
            controller.show_frame("ToolModifyScreen")

    def delete_selected(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a tool to delete!")
            return
        tool_id = self.tree.item(selected_item)["values"][0]
        confirm = messagebox.askyesno("Confirm", f"Are you sure you want to delete tool with ID {tool_id}?")
        if confirm:
            try:
                cursor.execute("DELETE FROM color_attempt WHERE id = ?", (tool_id,))
                cursor.execute("DELETE FROM color_tool WHERE id = ?", (tool_id,))
                conn.commit()
                self.load_data()
                messagebox.showinfo("Success", f"Deleted tool with ID {tool_id}")
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Database error: {e}")

# Tool Insert Screen
class ToolInsertScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        tk.Label(self, text="Insert New Tool", font=("Arial", 14)).pack(pady=10)

        tk.Label(self, text="Tool ID:").pack()
        self.tool_id_entry = tk.Entry(self)
        self.tool_id_entry.pack()

        tk.Label(self, text="Tool Name:").pack()
        self.tool_name_entry = tk.Entry(self)
        self.tool_name_entry.pack()

        tk.Label(self, text="Tool URL (optional):").pack()
        self.tool_url_entry = tk.Entry(self)
        self.tool_url_entry.pack()

        tk.Button(self, text="Insert", command=self.insert_tool).pack(pady=5)
        tk.Button(self, text="Back", command=controller.go_back).pack(pady=5)
        tk.Button(self, text="Main Menu", command=controller.go_to_main_menu).pack(pady=5)

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

            cursor.execute("""
                INSERT INTO color_tool (tool_id, tool_name, tool_url)
                VALUES (?, ?, ?)
            """, (tool_id, tool_name, tool_url))
            conn.commit()
            messagebox.showinfo("Success", f"Added tool with ID {tool_id}")
        except ValueError:
            messagebox.showerror("Error", "Tool ID must be a number!")
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Database error: {e}")

# Tool Modify Screen
class ToolModifyScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        tk.Label(self, text="Modify Tool", font=("Arial", 14)).pack(pady=10)

        tk.Label(self, text="Tool ID:").pack()
        self.tool_id_entry = tk.Entry(self)
        self.tool_id_entry.pack()

        tk.Label(self, text="Tool Name (leave blank to keep current):").pack()
        self.tool_name_entry = tk.Entry(self)
        self.tool_name_entry.pack()

        tk.Label(self, text="Tool URL (leave blank to keep current):").pack()
        self.tool_url_entry = tk.Entry(self)
        self.tool_url_entry.pack()

        tk.Button(self, text="Modify", command=self.modify_tool).pack(pady=5)
        tk.Button(self, text="Back", command=controller.go_back).pack(pady=5)
        tk.Button(self, text="Main Menu", command=controller.go_to_main_menu).pack(pady=5)

    def load_data(self, tool_data):
        tool_id, tool_name, tool_url = tool_data
        self.tool_id_entry.delete(0, tk.END)
        self.tool_name_entry.delete(0, tk.END)
        self.tool_url_entry.delete(0, tk.END)

        self.tool_id_entry.insert(0, str(tool_id))
        self.tool_name_entry.insert(0, tool_name if tool_name is not None else "")
        self.tool_url_entry.insert(0, tool_url if tool_url is not None else "")

    def modify_tool(self):
        tool_id = self.tool_id_entry.get()
        if not tool_id:
            messagebox.showerror("Error", "Tool ID is required!")
            return

        try:
            tool_id = int(tool_id)
            cursor.execute("SELECT * FROM color_tool WHERE id = ?", (tool_id,))
            result = cursor.fetchone()
            if not result:
                messagebox.showerror("Error", f"Tool with ID {tool_id} not found!")
                return

            current_tool_name, current_tool_url = result[1], result[2]

            tool_name = self.tool_name_entry.get()
            tool_name = tool_name if tool_name else current_tool_name

            tool_url = self.tool_url_entry.get()
            tool_url = tool_url if tool_url else current_tool_url

            cursor.execute("""
                UPDATE color_tool
                SET name = ?, url = ?
                WHERE id = ?
            """, (tool_name, tool_url, tool_id))
            conn.commit()
            messagebox.showinfo("Success", f"Updated tool with ID {tool_id}")
        except ValueError:
            messagebox.showerror("Error", "Tool ID must be a number!")
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Database error: {e}")

# Run the application
if __name__ == "__main__":
    app = DoujinshiManagerApp()
    app.mainloop()

# Close the database connection
conn.close()