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
from utils.logger import log_activity

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
        if not hasattr(self, 'current_xclientes') or not self.current_xclientes:
            messagebox.showerror("Error", "No client loaded for update. Please search for a client first.")
            return

        # Fetch current data from the database to retain values for empty, non-cleared fields
        current_db_data = get_client_data(self.current_xclientes)
        if not current_db_data:
            messagebox.showerror("Error", "Could not retrieve current client data from database.")
            return

        updated_client_data = {"XCLIENTES": self.current_xclientes}

        for field_name, entry_widget in self.entry_widgets.items():
            user_input = entry_widget.get().strip()
            clear_field = self.clear_checkboxes[field_name].get() # Get state of the clear checkbox

            db_column_name = next((f["db_column"] for f in CLIENT_FIELDS_CONFIG if f["name"] == field_name), None)
            if not db_column_name:
                continue # Skip if no corresponding db_column

            if clear_field:
                # If checkbox is checked, explicitly set to an empty string
                updated_client_data[field_name] = ""
            elif user_input:
                # If user provided input, use it
                updated_client_data[field_name] = user_input
            else:
                # If user input is empty AND checkbox is not checked, retain existing DB value
                updated_client_data[field_name] = current_db_data.get(db_column_name)

        # Validate fields based on the new updated_client_data
        # Note: Validation rules might need adjustment if 'required' fields can now be explicitly cleared.
        # For now, we'll assume validation still applies to non-cleared fields.
        validation_errors = validate_fields(updated_client_data, self.VALIDATION_RULES)
        if validation_errors:
            messagebox.showerror("Validation Error", "\n".join(validation_errors))
            return
        
        # Log data before update
        log_activity(
            action="Client Update - Before",
            user_data_before=current_db_data,
            user_id=self.current_xclientes
        )

        if update_client_data(updated_client_data):
            messagebox.showinfo("Success", "Client updated successfully!")
            # Re-populate form to show the updated data from DB, including cleared fields
            self.search_client()
            # Log data after successful update
            log_activity(
                action="Client Update - After",
                user_data_after=updated_client_data,
                user_id=self.current_xclientes
            )
        else:
            messagebox.showerror("Error", "Failed to update client.")
            # Log failed update
            log_activity(
                action="Client Update - Failed",
                user_data_before=current_db_data,
                user_data_after=updated_client_data,
                user_id=self.current_xclientes
            )

if __name__ == "__main__":
    root = ctk.CTk()
    root.withdraw()
    app = ClientUpdateApp(root)
    root.mainloop()
