from tkinter import messagebox
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.db_operations import delete_client_data, get_client_data
from delete.client_delete_gui import ClientDeleteGUI
import customtkinter as ctk # Keep ctk for the mainloop at the end
from utils.logger import log_activity

class ClientDeleteApp(ClientDeleteGUI):
    def __init__(self, root=None):
        super().__init__(root)
        # The GUI setup is now handled by ClientDeleteGUI's __init__

    def handle_delete_client(self):
        identifier = self.entry_widgets["identifier"].get().strip()
        if not identifier:
            messagebox.showerror("Input Error", "Please enter XCLIENTES, CGC, Name, or Inscrição to delete.")
            return

        # Get client data before deletion for logging
        client_data_before_delete = get_client_data(identifier)

        if client_data_before_delete:
            log_activity(
                action="Client Delete - Before",
                user_data_before=client_data_before_delete,
                user_id=identifier # Using identifier as user_id for logging
            )
            if delete_client_data(identifier):
                messagebox.showinfo("Success", "Client deleted successfully!")
                self.entry_widgets["identifier"].delete(0, ctk.END)
                log_activity(
                    action="Client Delete - After",
                    user_data_after={"status": "deleted"}, # Indicate successful deletion
                    user_id=identifier
                )
            else:
                messagebox.showerror("Error", "Failed to delete client. Client not found or an error occurred.")
                log_activity(
                    action="Client Delete - Failed",
                    user_data_before=client_data_before_delete,
                    user_data_after={"status": "failed to delete"},
                    user_id=identifier
                )
        else:
            messagebox.showerror("Error", "Client not found for deletion.")
            log_activity(
                action="Client Delete - Not Found",
                user_data_before={"identifier": identifier, "status": "not found"},
                user_id=identifier
            )

if __name__ == "__main__":
    root = ctk.CTk()
    root.withdraw()
    app = ClientDeleteApp(root)
    root.mainloop()
