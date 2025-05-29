import customtkinter as ctk
from tkinter import messagebox
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.cep_integration import on_cep_focus_out, fill_address_fields
from utils.settings_window import SettingsWindow
from utils.centerWindow import centerWindow
from utils.config_manager import APP_SETTINGS, CLIENT_FIELDS_CONFIG

class ClientRegistrationGUI(ctk.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Client Registration")
        self.geometry(centerWindow.center_window(self, master, APP_SETTINGS["APP_WIDTH"], APP_SETTINGS["APP_HEIGHT"]))
        self.grab_set() # Make it a modal window

        # Configure grid weights for better resizing behavior
        self.grid_columnconfigure(1, weight=1)

        self.entry_widgets = {}
        self.FIELDS = []
        self.VALIDATION_RULES = {}
        self.setup_gui_elements()

    def update_field_and_validation_rules(self):
        """Updates FIELDS and VALIDATION_RULES based on the current CLIENT_FIELDS_CONFIG."""
        self.FIELDS = [field["name"] for field in CLIENT_FIELDS_CONFIG if field["name"] != "XCLIENTES"]
        self.VALIDATION_RULES = {field["name"]: (field["max_length"], field["required"]) for field in CLIENT_FIELDS_CONFIG}

    def setup_gui_elements(self):
        # Clear existing widgets if any, for dynamic updates
        for widget in self.winfo_children():
            widget.destroy()

        # Re-initialize FIELDS and VALIDATION_RULES based on current CLIENT_FIELDS_CONFIG
        self.update_field_and_validation_rules()

        for idx, field in enumerate(self.FIELDS):
            ctk.CTkLabel(self, text=f"{field}:").grid(row=idx, column=0, padx=10, pady=5, sticky=ctk.W)
            entry = ctk.CTkEntry(self, width=300)
            entry.grid(row=idx, column=1, padx=5, pady=5, sticky=ctk.EW)
            self.entry_widgets[field] = entry

        if "CEP" in self.entry_widgets:
            self.entry_widgets["CEP"].bind("<FocusOut>", self.on_cep_focus_out_wrapper)
        
        # Frame for buttons
        button_frame = ctk.CTkFrame(self)
        button_frame.grid(row=len(self.FIELDS), column=0, columnspan=2, pady=20, sticky="nsew")
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        # Removed column for settings button as it's moved to main menu
        button_frame.columnconfigure(2, weight=0) 

        btn_register = ctk.CTkButton(button_frame, text="Register Client", command=self.handle_insert_client, fg_color="#1F6AA5", hover_color="#144870")
        btn_register.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        btn_clear = ctk.CTkButton(button_frame, text="Clear All", command=self.clear_form_fields, fg_color="#A51F1F", hover_color="#701414")
        btn_clear.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

    def clear_form_fields(self):
        """Limpa todos os campos de entrada no formulário."""
        for field in self.FIELDS:
            if field in self.entry_widgets:
                self.entry_widgets[field].delete(0, ctk.END)

    def on_cep_focus_out_wrapper(self, event):
        """Wrapper for on_cep_focus_out from cep_integration."""
        on_cep_focus_out(
            self.entry_widgets["CEP"],
            lambda data: self.after(0, fill_address_fields, self.entry_widgets, data),
            lambda title, msg: self.after(0, messagebox.showwarning, title, msg),
            lambda title, msg: self.after(0, messagebox.showerror, title, msg)
        )
