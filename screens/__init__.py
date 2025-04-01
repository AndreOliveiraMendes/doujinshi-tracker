# doujinshi_manager/screens/__init__.py
import tkinter as tk
from tkinter import messagebox, ttk
import os

# Import all screen classes
from .main_menu import MainMenu
from .database_menu import DatabaseMenu
from .directory_menu import DirectoryMenu
from .doujinshi_menu import DoujinshiMenu
from .doujinshi_view import DoujinshiViewScreen
from .doujinshi_insert import DoujinshiInsertScreen
from .doujinshi_modify import DoujinshiModifyScreen
from .attempt_menu import AttemptMenu
from .attempt_view import AttemptViewScreen
from .attempt_insert import AttemptInsertScreen
from .attempt_modify import AttemptModifyScreen
from .tool_menu import ToolMenu
from .tool_view import ToolViewScreen
from .tool_insert import ToolInsertScreen
from .tool_modify import ToolModifyScreen