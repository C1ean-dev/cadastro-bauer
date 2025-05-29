from tkinter import messagebox
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.db_operations import get_client_data
from read.client_read_gui import ClientReadGUI
import customtkinter as ctk # Keep ctk for the mainloop at the end
from utils.config_manager import CLIENT_FIELDS_CONFIG # Keep for db_column mapping

class ClientReadApp(ClientReadGUI):
    def __init__(self, root=None):
        super().__init__(root)
        # The GUI setup is now handled by ClientReadGUI's __init__

    def search_client(self):
        identifier = self.search_entry.get().strip()
        if not identifier:
            messagebox.showerror("Input Error", "Please enter NRECNO or CGC to search.")
            return

        client_data = get_client_data(identifier)
        if client_data:
            self.populate_display_fields(client_data) # populate_display_fields is now in ClientReadGUI
        else:
            messagebox.showwarning("Not Found", "Client not found.")
            self.clear_display_fields() # clear_display_fields is now in ClientReadGUI

if __name__ == "__main__":
    root = ctk.CTk()
    root.withdraw()
    app = ClientReadApp(root)
    root.mainloop()
