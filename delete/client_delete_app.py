from tkinter import messagebox
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.db_operations import delete_client_data
from delete.client_delete_gui import ClientDeleteGUI
import customtkinter as ctk # Keep ctk for the mainloop at the end

class ClientDeleteApp(ClientDeleteGUI):
    def __init__(self, root=None):
        super().__init__(root)
        # The GUI setup is now handled by ClientDeleteGUI's __init__

    def handle_delete_client(self):
        identifier = self.entry_widgets["identifier"].get().strip()
        if not identifier:
            messagebox.showerror("Input Error", "Please enter XCLIENTES, CGC, Name, or Inscrição to delete.")
            return

        if delete_client_data(identifier):
            messagebox.showinfo("Success", "Client deleted successfully!")
            self.entry_widgets["identifier"].delete(0, ctk.END)
        else:
            messagebox.showerror("Error", "Failed to delete client. Client not found or an error occurred.")

if __name__ == "__main__":
    root = ctk.CTk()
    root.withdraw()
    app = ClientDeleteApp(root)
    root.mainloop()
