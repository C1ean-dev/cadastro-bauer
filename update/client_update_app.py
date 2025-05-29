from tkinter import messagebox
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.db_operations import update_client_data, get_client_data
from utils.validation_utils import validate_fields
from update.client_update_gui import ClientUpdateGUI
import customtkinter as ctk # Keep ctk for the mainloop at the end
from utils.config_manager import CLIENT_FIELDS_CONFIG # Keep for db_column mapping

class ClientUpdateApp(ClientUpdateGUI):
    def __init__(self, root=None):
        super().__init__(root)
        # The GUI setup is now handled by ClientUpdateGUI's __init__
        self.current_xclientes = None # Initialize current_xclientes

    def search_client(self):
        identifier = self.search_entry.get().strip()
        if not identifier:
            messagebox.showerror("Input Error", "Please enter XCLIENTES, CGC, Name, or Inscrição to search.")
            return

        client_data = get_client_data(identifier)
        if client_data:
            self.populate_form_fields(client_data) # populate_form_fields is now in ClientUpdateGUI
            # Store the XCLIENTES for update operation
            self.current_xclientes = client_data.get(next((f["db_column"] for f in CLIENT_FIELDS_CONFIG if f["name"] == "XCLIENTES"), None))
        else:
            messagebox.showwarning("Not Found", "Client not found.")
            self.clear_form_fields() # clear_form_fields is now in ClientUpdateGUI

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

if __name__ == "__main__":
    root = ctk.CTk()
    root.withdraw()
    app = ClientUpdateApp(root)
    root.mainloop()
