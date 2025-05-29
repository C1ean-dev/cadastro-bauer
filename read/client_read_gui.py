import customtkinter as ctk
from tkinter import messagebox
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.centerWindow import centerWindow
from utils.config_manager import ConfigManager # Import the class

class ClientReadGUI(ctk.CTkToplevel):
    def __init__(self, root=None):
        super().__init__(root)
        self.config_manager = ConfigManager() # Get the singleton instance
        self.title("Read Client Data")
        self.geometry(centerWindow.center_window(self, root, self.config_manager.APP_SETTINGS["APP_WIDTH"], self.config_manager.APP_SETTINGS["APP_HEIGHT"]))
        self.grab_set()

        self.grid_columnconfigure(1, weight=1)
        self.display_widgets = {}
        self.FIELDS = []
        self.setup_gui_elements()

    def update_field_list(self):
        self.FIELDS = [field["name"] for field in self.config_manager.CLIENT_FIELDS_CONFIG]

    def setup_gui_elements(self):
        for widget in self.winfo_children():
            widget.destroy()

        ctk.CTkLabel(self, text="Search by XCLIENTES, CGC, Name, or Inscrição:").grid(row=0, column=0, padx=10, pady=5, sticky=ctk.W)
        self.search_entry = ctk.CTkEntry(self, width=300)
        self.search_entry.grid(row=0, column=1, padx=5, pady=5, sticky=ctk.EW)
        btn_search = ctk.CTkButton(self, text="Search", command=self.search_client)
        btn_search.grid(row=0, column=2, padx=5, pady=5)

        self.update_field_list()
        self.display_widgets = {}

        for idx, field in enumerate(self.FIELDS):
            label = ctk.CTkLabel(self, text=f"{field}:")
            label.grid(row=idx + 1, column=0, padx=10, pady=5, sticky=ctk.W)
            display_label = ctk.CTkLabel(self, text="", wraplength=250, justify=ctk.LEFT)
            display_label.grid(row=idx + 1, column=1, padx=5, pady=5, sticky=ctk.EW)
            self.display_widgets[field] = display_label

    def populate_display_fields(self, data):
        self.clear_display_fields()
        for field_name, display_label in self.display_widgets.items():
            db_column_name = next((f["db_column"] for f in self.config_manager.CLIENT_FIELDS_CONFIG if f["name"] == field_name), None)
            if db_column_name and db_column_name in data:
                display_label.configure(text=str(data[db_column_name]))

    def clear_display_fields(self):
        for field in self.FIELDS:
            if field in self.display_widgets:
                self.display_widgets[field].configure(text="")
