# doujinshi_manager/app.py
import tkinter as tk
import sqlite3
from screens.main_menu import MainMenu
from screens.directory_menu import DirectoryMenu
from screens.database_menu import DatabaseMenu
from screens.attempt_menu import AttemptMenu
from screens.tool_menu import ToolMenu
from screens.attempt_insert import AttemptInsertScreen
from screens.attempt_modify import AttemptModifyScreen
from screens.attempt_view import AttemptViewScreen
from screens.tool_insert import ToolInsertScreen
from screens.tool_modify import ToolModifyScreen
from screens.tool_view import ToolViewScreen
from screens.doujinshi_menu import DoujinshiMenu
from screens.doujinshi_insert import DoujinshiInsertScreen
from screens.doujinshi_modify import DoujinshiModifyScreen
from screens.doujinshi_view import DoujinshiViewScreen

class DoujinshiManagerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Doujinshi Colorization Manager")
        self.geometry("600x400")

        self.conn = sqlite3.connect("db/tracker.db")
        self.cursor = self.conn.cursor()

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        self.frame_history = []

        for F in (MainMenu, DatabaseMenu, DirectoryMenu, DoujinshiMenu, DoujinshiViewScreen,
                  DoujinshiInsertScreen, DoujinshiModifyScreen, AttemptMenu, AttemptViewScreen,
                  AttemptInsertScreen, AttemptModifyScreen, ToolMenu, ToolViewScreen,
                  ToolInsertScreen, ToolModifyScreen):
            # Screens that interact with the database need cursor and conn
            if F in (DoujinshiViewScreen, DoujinshiInsertScreen, DoujinshiModifyScreen,
                     AttemptViewScreen, AttemptInsertScreen, AttemptModifyScreen,
                     ToolViewScreen, ToolInsertScreen, ToolModifyScreen, DirectoryMenu):
                frame = F(container, self, self.cursor, self.conn)
            else:
                # Screens that don't need database access (e.g., MainMenu, DatabaseMenu)
                frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(MainMenu)

    def show_frame(self, frame_class):
        frame = self.frames[frame_class]
        # Refresh tools if the frame has a refresh_tools method
        if hasattr(frame, "refresh_tools"):
            frame.refresh_tools()
        frame.tkraise()
        if not self.frame_history or frame_class != self.frame_history[-1]:
            self.frame_history.append(frame_class)

    def go_back(self):
        if len(self.frame_history) > 1:
            self.frame_history.pop()  # Remove current frame
            previous_frame = self.frame_history[-1]
            self.show_frame(previous_frame)

    def go_to_main_menu(self):
        self.frame_history = [MainMenu]
        self.show_frame(MainMenu)

    def destroy(self):
        self.conn.close()
        super().destroy()

if __name__ == "__main__":
    app = DoujinshiManagerApp()
    app.mainloop()