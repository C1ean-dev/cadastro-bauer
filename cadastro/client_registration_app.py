from tkinter import messagebox
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.db_operations import connect_to_database, insert_client_data
from utils.validation_utils import validate_fields
from utils.config_manager import INTERNAL_DEFAULT_FIELDS
from cadastro.client_registration_gui import ClientRegistrationGUI
import customtkinter as ctk # Keep ctk for the mainloop at the end

class ClientRegistrationApp(ClientRegistrationGUI):
    def __init__(self, master=None):
        super().__init__(master)
        # The GUI setup is now handled by ClientRegistrationGUI's __init__
        # We only need to ensure the commands for buttons are correctly linked
        # These commands are defined in this class (business logic)

    def get_next_xclientes(self):
        """Retorna o próximo valor de XCLIENTES baseado no maior existente no banco."""
        conn = connect_to_database()
        if conn is None:
            return None
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT MAX(CAST(XCLIENTES AS INT)) FROM SM11_PROD.dbo.FBCLIENTES")
            result = cursor.fetchone()[0]
            return str((int(result) + 1) if result is not None else 1)
        except Exception as e:
            messagebox.showerror("Database Error", f"Error fetching next XCLIENTES: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def handle_insert_client(self):
        """
        Coleta dados do formulário, valida-os e tenta inseri-los no banco de dados.
        """
        # Access INTERNAL_DEFAULT_FIELDS directly from the module
        current_internal_defaults = INTERNAL_DEFAULT_FIELDS.copy()
        current_internal_defaults["XCLIENTES"] = self.get_next_xclientes()

        client_data = {field: self.entry_widgets[field].get().strip() for field in self.entry_widgets}
        client_data.update(current_internal_defaults)

        validation_errors = validate_fields(client_data, self.VALIDATION_RULES)
        if validation_errors:
            messagebox.showerror("Validation Error", "\n".join(validation_errors))
            return

        if insert_client_data(client_data):
            messagebox.showinfo("sucesso", "cliente registrado com sucesso!")
            self.clear_form_fields() # clear_form_fields is now in ClientRegistrationGUI
        else:
            messagebox.showerror("Erro", "não foi possivel enviar.")

if __name__ == "__main__":
    master = ctk.CTk()
    master.withdraw() # Hide the main window
    app = ClientRegistrationApp(master)
    master.mainloop()
