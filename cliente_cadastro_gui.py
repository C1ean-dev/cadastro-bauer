import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
import pyodbc
import requests
import threading
import re

FIELDS = [
    "NRECNO", "RAZAO", "CGC", "INSCRICAO", "CEP", "LOGRA", "ENDERECO", "NUMERO", "CJ", "BAIRRO",
    "CIDADE", "ESTADO", "TEL1", "TEL2", "FAX", "EMAIL", "ZONA",
]

INTERNAL_DEFAULT_FIELDS = {
    "WORKFLOW_TYPE": "GENERAL",
    "APPROVAL_STATUS": "A",
    "ADIMPLENTE": "T",
}

# Global dictionary for database configuration
DB_CONFIG = {
    'DRIVER': '{ODBC Driver 17 for SQL Server}',
    'SERVER': '192.168.4.17,1433',
    'DATABASE': 'SM11_PROD',
    'UID': 'sa',
    'PWD': '*f4lc40$'
}

VALIDATION_RULES = {
    "NRECNO": (10, False),
    "RAZAO": (100, True),
    "CGC": (20, True),
    "INSCRICAO": (20, False),
    "LOGRA": (20, False),
    "ENDERECO": (250, False),
    "NUMERO": (15, False),
    "CJ": (250, False),
    "BAIRRO": (60, False),
    "CIDADE": (40, False),
    "ESTADO": (10, False),
    "CEP": (10, False),
    "FAX": (23, False),
    "TEL1": (23, False),
    "TEL2": (23, False),
    "EMAIL": (255, False),
    "ZONA": (20, False),
    "XCLIENTES": (10, True)
}

def connect_to_database():
    """Conecta ao banco de dados"""
    try:
        conn_str = ';'.join(f"{key}={value}" for key, value in DB_CONFIG.items())
        conn = pyodbc.connect(conn_str)
        return conn
    except pyodbc.Error as e:
        messagebox.showerror("Database Connection Error", f"Failed to connect to the database: {e}")
        return None

def insert_client_data(client_data):
    """
    Insere um novo cliente na tabela FBCLIENTES ou indica se o cliente já existe.
    Retorna Verdadeiro em caso de inserção bem-sucedida, Falso se o cliente já existir ou em caso de erro.
    """
    conn = connect_to_database()
    if conn is None:
        return False

    try:
        cursor = conn.cursor()
        query = '''
        DECLARE @Status INT;

        IF NOT EXISTS (SELECT 1 FROM SM11_PROD.dbo.FBCLIENTES WHERE XCLIENTES = ?)
            BEGIN
                INSERT INTO SM11_PROD.dbo.FBCLIENTES
                    (NRECNO, RAZAO, CGC, INSCRICAO, LOGRA, ENDERECO, NUMERO, CJ, BAIRRO, CIDADE,
                    ESTADO, CEP, FAX, TEL1, TEL2, XCLIENTES, EMAIL, ZONA)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                SET @Status = 1; -- Successfully inserted
            END
        ELSE
            BEGIN
                SET @Status = 0; -- Client already exists
            END

        SELECT @Status AS Resultado; -- Return the status
        '''
        values_to_insert = (
            client_data.get("XCLIENTES"), # For the EXISTS check
            client_data.get("NRECNO"),
            client_data.get("RAZAO"),
            client_data.get("CGC"),
            client_data.get("INSCRICAO"),
            client_data.get("LOGRA"),
            client_data.get("ENDERECO"),
            client_data.get("NUMERO"),
            client_data.get("CJ"),
            client_data.get("BAIRRO"),
            client_data.get("CIDADE"),
            client_data.get("ESTADO"),
            client_data.get("CEP"),
            client_data.get("FAX"),
            client_data.get("TEL1"),
            client_data.get("TEL2"),
            client_data.get("XCLIENTES"), # For the INSERT statement
            client_data.get("EMAIL"),
            client_data.get("ZONA")
        )
        
        cursor.execute(query, values_to_insert)
        conn.commit()
        if conn:
            conn.close()
            return True
            
    except pyodbc.Error as e:
        messagebox.showerror("Database Error", f"An error occurred during insertion: {e}")
        return False


def validate_fields(data):
    """
    Valida os dados de entrada em relação a regras predefinidas.
    Retorna uma lista de mensagens de erro.
    """
    errors = []
    for field, (max_length, required) in VALIDATION_RULES.items():
        value = data.get(field, "").strip()

        if required and not value:
            errors.append(f"'{field}' is required.")
        elif value and len(value) > max_length:
            if field == "LOGRA":
                data[field] = value[:max_length]
            else:
                errors.append(f"'{field}' o campo passou do maximo de {max_length} characters.")
    return errors

def get_next_xclientes():
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
        conn.close()

def handle_insert_client():
    """
    Coleta dados do formulário, valida-os e tenta inseri-los no banco de dados.
    """
    INTERNAL_DEFAULT_FIELDS["XCLIENTES"] = get_next_xclientes()

    client_data = {field: entry_widgets[field].get().strip() for field in entry_widgets}
    client_data.update(INTERNAL_DEFAULT_FIELDS)

    validation_errors = validate_fields(client_data)
    if validation_errors:
        messagebox.showerror("Validation Error", "\n".join(validation_errors))
        return

    if insert_client_data(client_data):
        messagebox.showinfo("sucesso", "cliente registrado com sucesso!")
        clear_form_fields()
    else:
        messagebox.showerror("Erro", "não foi possivel enviar.")

def clear_form_fields():
    """Limpa todos os campos de entrada no formulário."""
    for field in FIELDS:
        if field in entry_widgets:
            entry_widgets[field].delete(0, ctk.END)

def fetch_address_thread(cep):
    """Obtém detalhes de endereço da API ViaCEP em um thread para evitar travamentos na tela aguardando a API"""
    try:
        response = requests.get(f"https://viacep.com.br/ws/{cep}/json/", timeout=5)
        response.raise_for_status()
        data = response.json()

        if "erro" in data:
            app.after(0, lambda: messagebox.showwarning("Invalid CEP", "CEP not found."))
        else:
            app.after(0, fill_address_fields, data)
    except requests.exceptions.Timeout:
        app.after(0, lambda: messagebox.showerror("CEP Lookup Error", "CEP lookup timed out."))
    except requests.exceptions.RequestException as e:
        app.after(0, lambda: messagebox.showerror("CEP Lookup Error", f"Error fetching CEP: {e}"))
    except Exception as e:
        app.after(0, lambda: messagebox.showerror("Unexpected Error", f"An unexpected error occurred: {e}"))

def on_cep_focus_out(event):
    """Valida o CEP e retorna erro caso esteja errado"""
    cep = entry_widgets["CEP"].get().strip().replace("-", "").replace(".", "")
    if re.fullmatch(r'\d{8}', cep):
        threading.Thread(target=fetch_address_thread, args=(cep,), daemon=True).start()
    elif cep:
        messagebox.showwarning("Invalid CEP Format", "Please enter a valid 8-digit CEP.")

def fill_address_fields(address_data):
    """adiciona os campos caso o cep esteja correto e a API tenha retornado"""
    field_mapping = {
        "ENDERECO": "logradouro",
        "LOGRA": "logradouro",
        "BAIRRO": "bairro",
        "CIDADE": "localidade",
        "ESTADO": "uf",
    }
    for form_field, json_key in field_mapping.items():
        entry_widgets[form_field].delete(0, ctk.END)
        entry_widgets[form_field].insert(0, address_data.get(json_key, ""))

class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Database Settings")
        self.geometry("400x300")
        self.grab_set()  # Make it a modal window

        self.settings_entries = {}
        self.create_widgets()
        self.load_settings()

    def create_widgets(self):
        for idx, (key, value) in enumerate(DB_CONFIG.items()):
            ctk.CTkLabel(self, text=f"{key}:").grid(row=idx, column=0, padx=10, pady=5, sticky=ctk.W)
            entry = ctk.CTkEntry(self, width=250)
            entry.grid(row=idx, column=1, padx=5, pady=5, sticky=ctk.EW)
            self.settings_entries[key] = entry
            self.grid_columnconfigure(1, weight=1) # Makes the entry widgets expand

        btn_save = ctk.CTkButton(self, text="Save Settings", command=self.save_settings)
        btn_save.grid(row=len(DB_CONFIG), column=0, columnspan=2, pady=20)

    def load_settings(self):
        for key, entry in self.settings_entries.items():
            entry.delete(0, ctk.END)
            entry.insert(0, DB_CONFIG.get(key, ""))

    def save_settings(self):
        global DB_CONFIG
        new_settings = {}
        for key, entry in self.settings_entries.items():
            value = entry.get().strip()
            if not value:
                messagebox.showerror("Validation Error", f"'{key}' cannot be empty.")
                return
            new_settings[key] = value
        
        DB_CONFIG.update(new_settings)
        messagebox.showinfo("Settings Saved", "Database settings updated successfully.")
        self.destroy() # Close the settings window after saving

def open_settings_window():
    SettingsWindow(app)


def setup_gui():
    """inicia a GUI"""
    global app, entry_widgets

    app = ctk.CTk()
    app.title("Client Registration")
    app.geometry("750x750")

    # Configure grid weights for better resizing behavior
    app.grid_columnconfigure(1, weight=1)

    entry_widgets = {}

    for idx, field in enumerate(FIELDS):
        ctk.CTkLabel(app, text=f"{field}:").grid(row=idx, column=0, padx=10, pady=5, sticky=ctk.W)
        entry = ctk.CTkEntry(app, width=300)
        entry.grid(row=idx, column=1, padx=5, pady=5, sticky=ctk.EW)
        entry_widgets[field] = entry

    if "CEP" in entry_widgets:
        entry_widgets["CEP"].bind("<FocusOut>", on_cep_focus_out)
    
    # Frame for buttons
    button_frame = ctk.CTkFrame(app)
    button_frame.grid(row=len(FIELDS), column=0, columnspan=2, pady=20, sticky="nsew")
    button_frame.columnconfigure(0, weight=1)
    button_frame.columnconfigure(1, weight=1)
    button_frame.columnconfigure(2, weight=1) # Added column for settings button

    btn_register = ctk.CTkButton(button_frame, text="Register Client", command=handle_insert_client, fg_color="#1F6AA5", hover_color="#144870")
    btn_register.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    btn_clear = ctk.CTkButton(button_frame, text="Clear All", command=clear_form_fields, fg_color="#A51F1F", hover_color="#701414")
    btn_clear.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

    btn_settings = ctk.CTkButton(button_frame, text="Settings", command=open_settings_window, fg_color="#23A51F", hover_color="#147023")
    btn_settings.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")

    app.mainloop()

if __name__ == "__main__":
    setup_gui()
