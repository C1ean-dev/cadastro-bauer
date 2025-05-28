import customtkinter as ctk
from tkinter import messagebox
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.db_operations import connect_to_database, delete_client_data
from utils.centerWindow import centerWindow
from utils.config_manager import APP_SETTINGS

class ClientDeleteApp(ctk.CTkToplevel):
    def __init__(self, root=None):
        super().__init__(root)
        self.title("Delete Client")
        self.geometry(centerWindow.center_window(self, root, APP_SETTINGS["APP_WIDTH"], APP_SETTINGS["APP_HEIGHT"]))
        self.grab_set() # Make it a modal window

        self.grid_columnconfigure(1, weight=1)
        self.entry_widgets = {}
        self.setup_gui_elements()

    def setup_gui_elements(self):
        for widget in self.winfo_children():
            widget.destroy()

        ctk.CTkLabel(self, text="NRECNO or CGC:").grid(row=0, column=0, padx=10, pady=5, sticky=ctk.W)
        entry = ctk.CTkEntry(self, width=300)
        entry.grid(row=0, column=1, padx=5, pady=5, sticky=ctk.EW)
        self.entry_widgets["identifier"] = entry

        button_frame = ctk.CTkFrame(self)
        button_frame.grid(row=1, column=0, columnspan=2, pady=20, sticky="nsew")
        button_frame.columnconfigure(0, weight=1)

        btn_delete = ctk.CTkButton(button_frame, text="Delete Client", command=self.handle_delete_client, fg_color="#A51F1F", hover_color="#701414")
        btn_delete.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    def handle_delete_client(self):
        identifier = self.entry_widgets["identifier"].get().strip()
        if not identifier:
            messagebox.showerror("Input Error", "Please enter NRECNO or CGC to delete.")
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
