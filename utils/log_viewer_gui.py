import customtkinter as ctk
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.centerWindow import centerWindow
from utils.config_manager import APP_SETTINGS

class LogViewerGUI(ctk.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("User Activity Logs")
        self.geometry(centerWindow.center_window(self, master, APP_SETTINGS["APP_WIDTH"], APP_SETTINGS["APP_HEIGHT"]))
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.create_widgets()

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.log_frame = ctk.CTkFrame(self)
        self.log_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.log_frame.grid_columnconfigure(0, weight=1)
        self.log_frame.grid_rowconfigure(0, weight=1)

        self.log_textbox = ctk.CTkTextbox(self.log_frame, wrap="word", state="disabled")
        self.log_textbox.grid(row=0, column=0, sticky="nsew")

        self.scrollbar = ctk.CTkScrollbar(self.log_frame, command=self.log_textbox.yview)
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.log_textbox.configure(yscrollcommand=self.scrollbar.set)

    def display_logs(self, logs_text):
        self.log_textbox.configure(state="normal")
        self.log_textbox.delete("1.0", "end")
        self.log_textbox.insert("1.0", logs_text)
        self.log_textbox.configure(state="disabled")

    def on_close(self):
        self.destroy()
