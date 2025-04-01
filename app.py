# doujinshi_manager/app.py
import tkinter as tk
from database import Database
from screens import (
    MainMenu, DatabaseMenu, DirectoryMenu, DoujinshiMenu, DoujinshiViewScreen,
    DoujinshiInsertScreen, DoujinshiModifyScreen, AttemptMenu, AttemptViewScreen,
    AttemptInsertScreen, AttemptModifyScreen, ToolMenu, ToolViewScreen,
    ToolInsertScreen, ToolModifyScreen
)

class DoujinshiManagerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Doujinshi Colorization Manager")
        self.geometry("800x600")

        # Initialize the database
        self.db = Database()
        self.cursor = self.db.cursor
        self.conn = self.db.conn

        # Container for frames
        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Dictionary to store frames
        self.frames = {}

        # Navigation history to track the sequence of screens
        self.navigation_history = []

        # Create all frames, passing cursor and conn to screens that need them
        for F in (MainMenu, DatabaseMenu, DirectoryMenu, DoujinshiMenu, DoujinshiViewScreen,
                  DoujinshiInsertScreen, DoujinshiModifyScreen, AttemptMenu, AttemptViewScreen,
                  AttemptInsertScreen, AttemptModifyScreen, ToolMenu, ToolViewScreen,
                  ToolInsertScreen, ToolModifyScreen):
            # Screens that interact with the database need cursor and conn
            if F in (DoujinshiViewScreen, DoujinshiInsertScreen, DoujinshiModifyScreen,
                     AttemptViewScreen, AttemptInsertScreen, AttemptModifyScreen,
                     ToolViewScreen, ToolInsertScreen, ToolModifyScreen):
                frame = F(self.container, self, self.cursor, self.conn)
            else:
                # Screens that don't need database access (e.g., MainMenu, DatabaseMenu)
                frame = F(self.container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Show the MainMenu as the starting screen
        self.show_frame(MainMenu)

    def show_frame(self, cont):
        # Add the current frame to the navigation history (if it's not the same as the last one)
        if not self.navigation_history or self.navigation_history[-1] != cont:
            self.navigation_history.append(cont)
        # Raise the frame to the top
        frame = self.frames[cont]
        frame.tkraise()

    def go_back(self):
        # If there's at least one previous screen in the history (excluding the current one)
        if len(self.navigation_history) > 1:
            # Remove the current screen from the history
            self.navigation_history.pop()
            # Show the previous screen
            previous_screen = self.navigation_history[-1]
            self.show_frame(previous_screen)
        else:
            # If there's nowhere to go back to, show a message
            tk.messagebox.showinfo("Info", "You are at the main screen!")

    def go_to_main_menu(self):
        # Clear the navigation history and go to MainMenu
        self.navigation_history = [MainMenu]
        self.show_frame(MainMenu)

    def __del__(self):
        self.db.close()