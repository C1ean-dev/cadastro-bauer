import customtkinter as ctk
from tkinter import messagebox
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.centerWindow import centerWindow
from utils.config_manager import ConfigManager # Import the class
from utils.log_viewer_app import LogViewerApp

class ClientDeleteGUI(ctk.CTkToplevel):
    def __init__(self, root=None):
        super().__init__(root)
        self.config_manager = ConfigManager() # Get the singleton instance
        self.title("Delete Client")
        self.geometry(centerWindow.center_window(self, root, self.config_manager.APP_SETTINGS["APP_WIDTH"], self.config_manager.APP_SETTINGS["APP_HEIGHT"]))
        self.grab_set()

        self.grid_columnconfigure(1, weight=1)
        self.entry_widgets = {}
        self.setup_gui_elements()

    def setup_gui_elements(self):
        for widget in self.winfo_children():
            widget.destroy()

        ctk.CTkLabel(self, text="Search by XCLIENTES, CGC, Name, or Inscrição:").grid(row=0, column=0, padx=10, pady=5, sticky=ctk.W)
        entry = ctk.CTkEntry(self, width=300)
        entry.grid(row=0, column=1, padx=5, pady=5, sticky=ctk.EW)
        self.entry_widgets["identifier"] = entry

        button_frame = ctk.CTkFrame(self)
        button_frame.grid(row=1, column=0, columnspan=2, pady=20, sticky="nsew")
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1) # Add a column for the new button

        btn_delete = ctk.CTkButton(button_frame, text="Delete Client", command=self.handle_delete_client, fg_color="#A51F1F", hover_color="#701414")
        btn_delete.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        btn_view_logs = ctk.CTkButton(button_frame, text="Ver Logs", command=self.open_log_viewer_screen)
        btn_view_logs.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

    def open_log_viewer_screen(self):
        # Open the log viewer screen as a Toplevel window
        log_viewer_app = LogViewerApp(self)
        log_viewer_app.grab_set() # Make it modal
