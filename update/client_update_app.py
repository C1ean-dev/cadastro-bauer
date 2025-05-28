import customtkinter as ctk
from tkinter import messagebox
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.db_operations import connect_to_database, update_client_data, get_client_data
from utils.validation_utils import validate_fields
from utils.cep_integration import on_cep_focus_out, fill_address_fields
from utils.centerWindow import centerWindow
from utils.config_manager import APP_SETTINGS, CLIENT_FIELDS_CONFIG

class ClientUpdateApp(ctk.CTkToplevel):
    def __init__(self, root=None):
        super().__init__(root)
        self.title("Update Client")
        self.geometry(centerWindow.center_window(self, root, APP_SETTINGS["APP_WIDTH"], APP_SETTINGS["APP_HEIGHT"]))
        self.grab_set() # Make it a modal window

        self.grid_columnconfigure(1, weight=1)
        self.entry_widgets = {}
        self.FIELDS = []
        self.VALIDATION_RULES = {}
        self.setup_gui_elements()

    def update_field_and_validation_rules(self):
        self.FIELDS = [field["name"] for field in CLIENT_FIELDS_CONFIG if field["name"] != "XCLIENTES"]
        self.VALIDATION_RULES = {field["name"]: (field["max_length"], field["required"]) for field in CLIENT_FIELDS_CONFIG}

    def setup_gui_elements(self):
        for widget in self.winfo_children():
            widget.destroy()

        # Search section
        ctk.CTkLabel(self, text="Search by XCLIENTES, CGC, Name, or Inscrição:").grid(row=0, column=0, padx=10, pady=5, sticky=ctk.W)
        self.search_entry = ctk.CTkEntry(self, width=300)
        self.search_entry.grid(row=0, column=1, padx=5, pady=5, sticky=ctk.EW)
        btn_search = ctk.CTkButton(self, text="Search", command=self.search_client)
        btn_search.grid(row=0, column=2, padx=5, pady=5)

        # Client data fields (initially hidden or empty)
        self.update_field_and_validation_rules()
        self.field_widgets = {} # To store labels and entries for client data

        for idx, field in enumerate(self.FIELDS):
            label = ctk.CTkLabel(self, text=f"{field}:")
            label.grid(row=idx + 1, column=0, padx=10, pady=5, sticky=ctk.W)
            entry = ctk.CTkEntry(self, width=300)
            entry.grid(row=idx + 1, column=1, padx=5, pady=5, sticky=ctk.EW)
            self.entry_widgets[field] = entry
            self.field_widgets[field] = {"label": label, "entry": entry}

        if "CEP" in self.entry_widgets:
            self.entry_widgets["CEP"].bind("<FocusOut>", self.on_cep_focus_out_wrapper)

        # Buttons
        button_frame = ctk.CTkFrame(self)
        button_frame.grid(row=len(self.FIELDS) + 1, column=0, columnspan=3, pady=20, sticky="nsew")
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)

        btn_update = ctk.CTkButton(button_frame, text="Update Client", command=self.handle_update_client, fg_color="#1F6AA5", hover_color="#144870")
        btn_update.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        btn_clear = ctk.CTkButton(button_frame, text="Clear Form", command=self.clear_form_fields, fg_color="#A51F1F", hover_color="#701414")
        btn_clear.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

    def search_client(self):
        identifier = self.search_entry.get().strip()
        if not identifier:
            messagebox.showerror("Input Error", "Please enter XCLIENTES, CGC, Name, or Inscrição to search.")
            return

        client_data = get_client_data(identifier)
        if client_data:
            
            self.populate_form_fields(client_data)

        else:
            messagebox.showwarning("Not Found", "Client not found.")
            self.clear_form_fields()

    def populate_form_fields(self, data):
        self.clear_form_fields()
        for field_name, entry_widget in self.entry_widgets.items():
            db_column_name = next((f["db_column"] for f in CLIENT_FIELDS_CONFIG if f["name"] == field_name), None)
            if db_column_name and db_column_name in data:
                entry_widget.insert(0, str(data[db_column_name]))
        # Store the XCLIENTES for update operation
        self.current_xclientes = data.get(next((f["db_column"] for f in CLIENT_FIELDS_CONFIG if f["name"] == "XCLIENTES"), None))

    def handle_update_client(self):
        client_data = {field: self.entry_widgets[field].get().strip() for field in self.entry_widgets}
        
        # Add XCLIENTES back to client_data for the update operation
        if hasattr(self, 'current_xclientes') and self.current_xclientes:
            client_data["XCLIENTES"] = self.current_xclientes
        else:
            messagebox.showerror("Error", "No client loaded for update. Please search for a client first.")
            return

        validation_errors = validate_fields(client_data, self.VALIDATION_RULES)
        if validation_errors:
            messagebox.showerror("Validation Error", "\n".join(validation_errors))
            return
        if update_client_data(client_data):
            messagebox.showinfo("Success", "Client updated successfully!")
        else:
            messagebox.showerror("Error", "Failed to update client.")

    def clear_form_fields(self):
        for field in self.FIELDS:
            if field in self.entry_widgets:
                self.entry_widgets[field].delete(0, ctk.END)
        self.current_xclientes = None # Clear the stored XCLIENTES

    def on_cep_focus_out_wrapper(self, event):
        on_cep_focus_out(
            self.entry_widgets["CEP"],
            lambda data: self.after(0, fill_address_fields, self.entry_widgets, data),
            lambda title, msg: self.after(0, messagebox.showwarning, title, msg),
            lambda title, msg: self.after(0, messagebox.showerror, title, msg)
        )

if __name__ == "__main__":
    root = ctk.CTk()
    root.withdraw()
    app = ClientUpdateApp(root)
    root.mainloop()
