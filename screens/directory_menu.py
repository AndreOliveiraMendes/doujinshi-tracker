# doujinshi_manager/screens/directory_menu.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import os
import shutil
import sqlite3

class DirectoryMenu(tk.Frame):
    def __init__(self, parent, controller, cursor, conn):
        super().__init__(parent)
        self.controller = controller
        self.cursor = cursor
        self.conn = conn

        tk.Label(self, text="Directory Menu", font=("Arial", 14)).pack(pady=10)

        # Create a Treeview to display folders hierarchically
        self.tree = ttk.Treeview(self, columns=("Path", "Has Subfolders"), show="tree headings")
        self.tree.heading("#0", text="Folder Structure")
        self.tree.heading("Path", text="Full Path")
        self.tree.heading("Has Subfolders", text="Has Subfolders")
        self.tree.column("#0", width=200)
        self.tree.column("Path", width=300)
        self.tree.column("Has Subfolders", width=100)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y")

        # Load tools for folder creation
        self.tools = self.load_tools()

        # Load the folder data
        self.load_folders()

        # Buttons
        tk.Button(self, text="Create Folder", command=self.create_folder).pack(pady=5)
        tk.Button(self, text="Rename Selected", command=self.rename_selected).pack(pady=5)
        tk.Button(self, text="Delete Selected", command=self.delete_selected).pack(pady=5)
        tk.Button(self, text="Back", command=controller.go_back).pack(pady=5)
        tk.Button(self, text="Main Menu", command=controller.go_to_main_menu).pack(pady=5)

    def load_tools(self):
        """Load available tools from the color_tool table."""
        try:
            self.cursor.execute("SELECT tool_id, tool_name FROM color_tool")
            tools = {row[0]: row[1] for row in self.cursor.fetchall()}
            return tools
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load tools: {e}")
            return {}

    def has_subfolders(self, folder_path):
        """Check if the given folder has subfolders."""
        try:
            with os.scandir(folder_path) as entries:
                for entry in entries:
                    if entry.is_dir():
                        return True
            return False
        except OSError as e:
            messagebox.showerror("Error", f"Failed to check subfolders for {folder_path}: {e}")
            return False

    def load_folders(self):
        """Load all folders in doujinshi_collection into the Treeview hierarchically."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        base_path = "doujinshi_collection"
        if not os.path.exists(base_path):
            os.makedirs(base_path)

        def add_folder_to_tree(parent_id, folder_path, relative_path=""):
            folder_name = os.path.basename(folder_path)
            # Build the relative path using forward slashes
            current_relative_path = f"{relative_path}/{folder_name}" if relative_path else folder_name
            has_subs = self.has_subfolders(folder_path)
            node_id = self.tree.insert(
                parent_id,
                "end",
                text=folder_name,
                values=(current_relative_path, "Yes" if has_subs else "No")
            )
            if has_subs:
                try:
                    with os.scandir(folder_path) as entries:
                        for entry in sorted(entries, key=lambda e: e.name):
                            if entry.is_dir():
                                sub_path = os.path.join(folder_path, entry.name)
                                add_folder_to_tree(node_id, sub_path, current_relative_path)
                except OSError as e:
                    messagebox.showerror("Error", f"Failed to load subfolders for {folder_path}: {e}")

        try:
            with os.scandir(base_path) as entries:
                for entry in sorted(entries, key=lambda e: e.name):
                    if entry.is_dir():
                        folder_path = os.path.join(base_path, entry.name)
                        add_folder_to_tree("", folder_path)
        except OSError as e:
            messagebox.showerror("Error", f"Failed to load folders: {e}")

    def create_folder(self):
        """Create a new folder in doujinshi_collection with the correct structure."""
        # Prompt for the base path (cX or cX/pY)
        base_path = simpledialog.askstring(
            "Create Folder",
            "Enter the base path (e.g., c1 or c1/p1):",
            parent=self
        )
        if not base_path:
            return  # User cancelled

        # Clean the input
        base_path = base_path.strip("/\\").replace("\\", "/")
        if not base_path:
            messagebox.showerror("Error", "Base path cannot be empty!")
            return

        # Validate the base path format (should be cX or cX/pY or cX/pY)
        parts = base_path.split("/")
        if len(parts) not in [1, 2]:
            messagebox.showerror("Error", "Base path must be in the format 'cX' or 'cX/pY'!")
            return
        if not parts[0].startswith("c"):
            messagebox.showerror("Error", "Base path must start with a chapter (e.g., c1)!")
            return
        if len(parts) == 2 and not parts[1].startswith("p"):
            messagebox.showerror("Error", "Second part must be a part (e.g., p1)!")
            return

        # Prompt for the tool to use
        if not self.tools:
            messagebox.showerror("Error", "No tools available! Please add a tool first.")
            return

        tool_names = list(self.tools.values())
        tool_window = tk.Toplevel(self)
        tool_window.title("Select Tool")
        tool_window.geometry("300x150")

        tk.Label(tool_window, text="Select a tool for the folder:").pack(pady=5)
        tool_var = tk.StringVar(value=tool_names[0])
        tool_menu = ttk.Combobox(tool_window, textvariable=tool_var, values=tool_names, state="readonly")
        tool_menu.pack(pady=5)

        def on_confirm():
            tool_name = tool_var.get()
            tool_window.destroy()

            # Construct the full path
            full_path = os.path.join("doujinshi_collection", base_path, tool_name)

            # Check if the folder already exists
            if os.path.exists(full_path):
                messagebox.showerror("Error", f"Folder '{base_path}/{tool_name}' already exists!")
                return

            # Create the folder
            try:
                os.makedirs(full_path, exist_ok=True)
                messagebox.showinfo("Success", f"Created folder '{base_path}/{tool_name}'")
                self.load_folders()  # Refresh the Treeview
            except OSError as e:
                messagebox.showerror("Error", f"Failed to create folder: {e}")

        tk.Button(tool_window, text="Confirm", command=on_confirm).pack(pady=5)
        tk.Button(tool_window, text="Cancel", command=tool_window.destroy).pack(pady=5)
        tool_window.transient(self)
        tool_window.grab_set()
        self.wait_window(tool_window)

    def rename_selected(self):
        """Rename the selected folder."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a folder to rename!")
            return

        folder_name = self.tree.item(selected_item)["text"]
        old_relative_path = self.tree.item(selected_item)["values"][0]
        has_subfolders = self.tree.item(selected_item)["values"][1] == "Yes"

        # Warn if the folder has subfolders
        if has_subfolders:
            confirm = messagebox.askyesno(
                "Warning",
                f"The folder '{folder_name}' contains subfolders. Renaming it will only affect the selected folder. Proceed?"
            )
            if not confirm:
                return

        new_name = simpledialog.askstring("Rename Folder", f"Enter new name for '{folder_name}':", initialvalue=folder_name)
        if not new_name:
            return

        if new_name == folder_name:
            return

        # Construct the old and new full paths
        old_path = os.path.join("doujinshi_collection", old_relative_path)
        parent_relative_path = os.path.dirname(old_relative_path) if "/" in old_relative_path else ""
        new_relative_path = f"{parent_relative_path}/{new_name}" if parent_relative_path else new_name
        new_path = os.path.join("doujinshi_collection", new_relative_path)

        if os.path.exists(new_path):
            messagebox.showerror("Error", f"A folder named '{new_name}' already exists!")
            return

        # Validate the new name based on its level
        level = len(old_relative_path.split("/"))
        if level == 1 and not new_name.startswith("c"):
            messagebox.showerror("Error", "Top-level folder must start with 'c' (e.g., c1)!")
            return
        if level == 2 and old_relative_path.startswith("c") and not new_name.startswith("p"):
            messagebox.showerror("Error", "Second-level folder must start with 'p' (e.g., p1)!")
            return
        if level == 3 and new_name not in self.tools.values():
            messagebox.showerror("Error", "Third-level folder must be a valid tool name!")
            return

        try:
            os.rename(old_path, new_path)
            self.cursor.execute(
                "UPDATE color_subject SET folder_path = REPLACE(folder_path, ?, ?) WHERE folder_path LIKE ?",
                (old_relative_path, new_relative_path, old_relative_path + "%")
            )
            self.conn.commit()
            messagebox.showinfo("Success", f"Renamed folder to '{new_name}'")
            self.load_folders()
        except OSError as e:
            messagebox.showerror("Error", f"Failed to rename folder: {e}")
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Database error: {e}")

    def delete_selected(self):
        """Delete the selected folder and associated database entries."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a folder to delete!")
            return

        folder_name = self.tree.item(selected_item)["text"]
        relative_path = self.tree.item(selected_item)["values"][0]
        has_subfolders = self.tree.item(selected_item)["values"][1] == "Yes"

        if has_subfolders:
            confirm = messagebox.askyesno(
                "Warning",
                f"The folder '{folder_name}' contains subfolders. Deleting it will remove all subfolders and their contents. Proceed?"
            )
            if not confirm:
                return

        confirm = messagebox.askyesno("Confirm", f"Are you sure you want to delete the folder '{folder_name}' and its associated data?")
        if not confirm:
            return

        try:
            folder_path = os.path.join("doujinshi_collection", relative_path)
            self.cursor.execute("SELECT code FROM color_subject WHERE folder_path LIKE ?", (relative_path + "%",))
            codes = [row[0] for row in self.cursor.fetchall()]

            for code in codes:
                self.cursor.execute("DELETE FROM color_attempt WHERE code = ?", (code,))

            self.cursor.execute("DELETE FROM color_subject WHERE folder_path LIKE ?", (relative_path + "%",))
            self.conn.commit()

            if os.path.exists(folder_path):
                shutil.rmtree(folder_path)

            messagebox.showinfo("Success", f"Deleted folder '{folder_name}' and associated data")
            self.load_folders()
        except OSError as e:
            messagebox.showerror("Error", f"Failed to delete folder: {e}")
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Database error: {e}")
