import customtkinter as ctk
from tkinter import messagebox
import pyodbc
import requests
import threading
import re
import config_manager # Import the module instead of specific variables

# These will be dynamically generated based on CLIENT_FIELDS_CONFIG
FIELDS = []
VALIDATION_RULES = {}

def update_field_and_validation_rules():
    """Updates FIELDS and VALIDATION_RULES based on the current CLIENT_FIELDS_CONFIG."""
    global FIELDS, VALIDATION_RULES
    # Access the config directly from the imported module
    FIELDS = [field["name"] for field in config_manager.CLIENT_FIELDS_CONFIG if field["name"] != "XCLIENTES"]
    VALIDATION_RULES = {field["name"]: (field["max_length"], field["required"]) for field in config_manager.CLIENT_FIELDS_CONFIG}

# Initial update - this will use the initial loaded config
update_field_and_validation_rules()

def connect_to_database():
    """Conecta ao banco de dados"""
    try:
        conn_str = ';'.join(f"{key}={value}" for key, value in config_manager.DB_CONFIG.items())
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

        insert_columns = [field["db_column"] for field in config_manager.CLIENT_FIELDS_CONFIG]
        
        placeholders = ', '.join(['?'] * len(insert_columns))
        columns_str = ', '.join(insert_columns)

        query = f'''
        DECLARE @Status INT;

        IF NOT EXISTS (SELECT 1 FROM SM11_PROD.dbo.FBCLIENTES WHERE XCLIENTES = ?)
            BEGIN
                INSERT INTO SM11_PROD.dbo.FBCLIENTES
                    ({columns_str})
                VALUES ({placeholders});
                SET @Status = 1; -- Successfully inserted
            END
        ELSE
            BEGIN
                SET @Status = 0; -- Client already exists
            END

        SELECT @Status AS Resultado; -- Return the status
        '''
        values_for_insert_statement = [client_data.get(field["name"]) for field in CLIENT_FIELDS_CONFIG]
        
        values_to_insert = (client_data.get("XCLIENTES"),) + tuple(values_for_insert_statement)
        
        cursor.execute(query, values_to_insert)
        conn.commit()
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

def get_table_columns(table_name="FBCLIENTES"):
    """Fetches column names from the specified table in the database."""
    conn = connect_to_database()
    if conn is None:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute(f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table_name}' AND TABLE_SCHEMA = 'dbo'")
        columns = [row[0] for row in cursor.fetchall()]
        return columns
    except pyodbc.Error as e:
        messagebox.showerror("Database Error", f"Error fetching table columns: {e}")
        return []
    finally:
        conn.close()

class ClientRegistrationApp(ctk.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Client Registration")
        self.geometry("750x750")
        self.grab_set() # Make it a modal window

        # Configure grid weights for better resizing behavior
        self.grid_columnconfigure(1, weight=1)

        self.entry_widgets = {}
        self.setup_gui_elements()

    def setup_gui_elements(self):
        # Clear existing widgets if any, for dynamic updates
        for widget in self.winfo_children():
            widget.destroy()

        # Reload configuration from config_manager before updating GUI elements
        config_manager.app_config = config_manager.load_config()
        config_manager.CLIENT_FIELDS_CONFIG = config_manager.app_config["CLIENT_FIELDS_CONFIG"]
        config_manager.DB_CONFIG = config_manager.app_config["DB_CONFIG"]
        config_manager.INTERNAL_DEFAULT_FIELDS = config_manager.app_config["INTERNAL_DEFAULT_FIELDS"]

        # Re-initialize FIELDS and VALIDATION_RULES based on current CLIENT_FIELDS_CONFIG
        update_field_and_validation_rules()

        for idx, field in enumerate(FIELDS):
            ctk.CTkLabel(self, text=f"{field}:").grid(row=idx, column=0, padx=10, pady=5, sticky=ctk.W)
            entry = ctk.CTkEntry(self, width=300)
            entry.grid(row=idx, column=1, padx=5, pady=5, sticky=ctk.EW)
            self.entry_widgets[field] = entry

        if "CEP" in self.entry_widgets:
            self.entry_widgets["CEP"].bind("<FocusOut>", self.on_cep_focus_out)
        
        # Frame for buttons
        button_frame = ctk.CTkFrame(self)
        button_frame.grid(row=len(FIELDS), column=0, columnspan=2, pady=20, sticky="nsew")
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        button_frame.columnconfigure(2, weight=1) # Added column for settings button

        btn_register = ctk.CTkButton(button_frame, text="Register Client", command=self.handle_insert_client, fg_color="#1F6AA5", hover_color="#144870")
        btn_register.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        btn_clear = ctk.CTkButton(button_frame, text="Clear All", command=self.clear_form_fields, fg_color="#A51F1F", hover_color="#701414")
        btn_clear.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        btn_settings = ctk.CTkButton(button_frame, text="Settings", command=self.open_settings_window, fg_color="#23A51F", hover_color="#147023")
        btn_settings.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")

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
            conn.close()

    def handle_insert_client(self):
        """
        Coleta dados do formulário, valida-os e tenta inseri-los no banco de dados.
        """
        # Ensure XCLIENTES is updated from the latest INTERNAL_DEFAULT_FIELDS
        # Access INTERNAL_DEFAULT_FIELDS directly from the config_manager module
        current_internal_defaults = config_manager.INTERNAL_DEFAULT_FIELDS.copy()
        current_internal_defaults["XCLIENTES"] = self.get_next_xclientes()

        client_data = {field: self.entry_widgets[field].get().strip() for field in self.entry_widgets}
        client_data.update(current_internal_defaults)

        validation_errors = validate_fields(client_data)
        if validation_errors:
            messagebox.showerror("Validation Error", "\n".join(validation_errors))
            return

        if insert_client_data(client_data):
            messagebox.showinfo("sucesso", "cliente registrado com sucesso!")
            self.clear_form_fields()
        else:
            messagebox.showerror("Erro", "não foi possivel enviar.")

    def clear_form_fields(self):
        """Limpa todos os campos de entrada no formulário."""
        for field in FIELDS:
            if field in self.entry_widgets:
                self.entry_widgets[field].delete(0, ctk.END)

    def fetch_address_thread(self, cep):
        """Obtém detalhes de endereço da API ViaCEP em um thread para evitar travamentos na tela aguardando a API"""
        try:
            response = requests.get(f"https://viacep.com.br/ws/{cep}/json/", timeout=5)
            response.raise_for_status()
            data = response.json()

            if "erro" in data:
                self.after(0, lambda: messagebox.showwarning("Invalid CEP", "CEP not found."))
            else:
                self.after(0, self.fill_address_fields, data)
        except requests.exceptions.Timeout:
            self.after(0, lambda: messagebox.showerror("CEP Lookup Error", "CEP lookup timed out."))
        except requests.exceptions.RequestException as e:
            self.after(0, lambda: messagebox.showerror("CEP Lookup Error", f"Error fetching CEP: {e}"))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Unexpected Error", f"An unexpected error occurred: {e}"))

    def on_cep_focus_out(self, event):
        """Valida o CEP e retorna erro caso esteja errado"""
        cep = self.entry_widgets["CEP"].get().strip().replace("-", "").replace(".", "")
        if re.fullmatch(r'\d{8}', cep):
            threading.Thread(target=self.fetch_address_thread, args=(cep,), daemon=True).start()
        elif cep:
            messagebox.showwarning("Invalid CEP Format", "Please enter a valid 8-digit CEP.")

    def fill_address_fields(self, address_data):
        """adiciona os campos caso o cep esteja correto e a API tenha retornado"""
        field_mapping = {
            "ENDERECO": "logradouro",
            "LOGRA": "logradouro",
            "BAIRRO": "bairro",
            "CIDADE": "localidade",
            "ESTADO": "uf",
        }
        for form_field, json_key in field_mapping.items():
            self.entry_widgets[form_field].delete(0, ctk.END)
            self.entry_widgets[form_field].insert(0, address_data.get(json_key, ""))

class AddFieldDialog(ctk.CTkToplevel):
    def __init__(self, master, main_app_root, refresh_callback):
        super().__init__(master)
        self.master = master
        self.main_app_root = main_app_root
        self.refresh_callback = refresh_callback # Ensure this line is correct
        self.title("Adicionar Novo Campo")
        self.geometry("400x300")
        self.grab_set()

        self.create_widgets()

    def create_widgets(self):
        self.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self, text="Nome do Campo:").grid(row=0, column=0, padx=10, pady=5, sticky=ctk.W)
        self.name_entry = ctk.CTkEntry(self, width=250)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5, sticky=ctk.EW)
        self.name_entry.bind("<KeyRelease>", self.update_db_column_label)

        ctk.CTkLabel(self, text="Comprimento Máximo:").grid(row=1, column=0, padx=10, pady=5, sticky=ctk.W)
        self.max_length_entry = ctk.CTkEntry(self, width=250)
        self.max_length_entry.grid(row=1, column=1, padx=5, pady=5, sticky=ctk.EW)

        ctk.CTkLabel(self, text="Obrigatório:").grid(row=2, column=0, padx=10, pady=5, sticky=ctk.W)
        self.required_var = ctk.BooleanVar(value=True)
        self.required_checkbox = ctk.CTkCheckBox(self, text="", variable=self.required_var)
        self.required_checkbox.grid(row=2, column=1, padx=5, pady=5, sticky=ctk.W)

        ctk.CTkLabel(self, text="Coluna DB (Auto):").grid(row=3, column=0, padx=10, pady=5, sticky=ctk.W)
        self.db_column_label = ctk.CTkLabel(self, text="")
        self.db_column_label.grid(row=3, column=1, padx=5, pady=5, sticky=ctk.W)

        btn_save = ctk.CTkButton(self, text="Salvar Campo", command=self.save_new_field)
        btn_save.grid(row=4, column=0, columnspan=2, pady=20)

    def update_db_column_label(self, event=None):
        name = self.name_entry.get().strip()
        db_column = name.upper().replace(" ", "_")
        self.db_column_label.configure(text=db_column)

    def save_new_field(self):
        name = self.name_entry.get().strip()
        max_length_str = self.max_length_entry.get().strip()
        required = self.required_var.get()
        db_column = self.db_column_label.cget("text")

        if not name:
            messagebox.showerror("Erro de Validação", "Nome do campo não pode ser vazio.")
            return
        if not max_length_str:
            messagebox.showerror("Erro de Validação", "Comprimento máximo não pode ser vazio.")
            return
        try:
            max_length = int(max_length_str)
            if max_length <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Erro de Validação", "Comprimento máximo deve ser um número inteiro positivo.")
            return
        
        # Check if field name already exists
        if any(field["name"].lower() == name.lower() for field in config_manager.CLIENT_FIELDS_CONFIG):
            messagebox.showerror("Erro de Validação", f"Um campo com o nome '{name}' já existe.")
            return

        new_field = {
            "name": name,
            "max_length": max_length,
            "required": required,
            "db_column": db_column
        }
        config_manager.CLIENT_FIELDS_CONFIG.append(new_field)
        
        messagebox.showinfo("Campo Adicionado", "Novo campo adicionado com sucesso. Salve as configurações para aplicar.")
        self.refresh_callback() # Refresh the settings window's client fields display
        self.destroy() # Close the dialog

class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, master, main_app_root, refresh_callback):
        super().__init__(master)
        self.main_app_root = main_app_root
        self.refresh_callback = refresh_callback
        self.title("Configurações")
        self.geometry("800x600") # Increased size for CLIENT_FIELDS_CONFIG
        self.grab_set()  # Make it a modal window

        self.db_settings_entries = {}
        self.internal_default_entries = {}
        self.client_fields_frames = [] # To hold frames for each client field

        self.create_widgets()
        self.load_settings()

    def create_widgets(self):
        # Use a scrollable frame for client fields
        self.scrollable_frame = ctk.CTkScrollableFrame(self, width=750, height=300)
        self.scrollable_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        self.scrollable_frame.grid_columnconfigure(1, weight=1)

        # Database Settings
        ctk.CTkLabel(self.scrollable_frame, text="Configurações do Banco de Dados:", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=4, padx=10, pady=(10, 5), sticky=ctk.W)
        
        row_idx = 1
        for key in config_manager.DB_CONFIG.keys():
            ctk.CTkLabel(self.scrollable_frame, text=f"{key}:").grid(row=row_idx, column=0, padx=10, pady=5, sticky=ctk.W)
            entry = ctk.CTkEntry(self.scrollable_frame, width=250)
            entry.grid(row=row_idx, column=1, padx=5, pady=5, sticky=ctk.EW)
            self.db_settings_entries[key] = entry
            row_idx += 1
        
        # Internal Default Fields
        ctk.CTkLabel(self.scrollable_frame, text="Campos Padrão Internos:", font=ctk.CTkFont(weight="bold")).grid(row=row_idx, column=0, columnspan=4, padx=10, pady=(10, 5), sticky=ctk.W)
        row_idx += 1
        for key in config_manager.INTERNAL_DEFAULT_FIELDS.keys():
            if key == "XCLIENTES": # XCLIENTES is dynamically generated
                continue
            ctk.CTkLabel(self.scrollable_frame, text=f"{key}:").grid(row=row_idx, column=0, padx=10, pady=5, sticky=ctk.W)
            entry = ctk.CTkEntry(self.scrollable_frame, width=250)
            entry.grid(row=row_idx, column=1, padx=5, pady=5, sticky=ctk.EW)
            self.internal_default_entries[key] = entry
            row_idx += 1

        # CLIENT_FIELDS_CONFIG
        ctk.CTkLabel(self.scrollable_frame, text="Configuração de Campos do Cliente:", font=ctk.CTkFont(weight="bold")).grid(row=row_idx, column=0, columnspan=4, padx=10, pady=(10, 5), sticky=ctk.W)
        row_idx += 1

        self.client_fields_start_row = row_idx
        self.render_client_fields()

        # Add/Remove buttons for CLIENT_FIELDS_CONFIG
        button_frame = ctk.CTkFrame(self)
        button_frame.grid(row=1, column=0, columnspan=2, pady=10, sticky="ew")
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)

        btn_add_field = ctk.CTkButton(button_frame, text="Adicionar Campo", command=self.add_client_field)
        btn_add_field.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        btn_save = ctk.CTkButton(self, text="Salvar Configurações", command=self.save_settings)
        btn_save.grid(row=2, column=0, pady=20, padx=(10, 5), sticky="ew")

        btn_reset = ctk.CTkButton(self, text="Reset de Fábrica", command=self.reset_to_defaults, fg_color="orange", hover_color="darkorange")
        btn_reset.grid(row=2, column=1, pady=20, padx=(5, 10), sticky="ew")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1) # Ensure column 1 also expands

    def render_client_fields(self):
        # Clear existing client field widgets
        for field_data_dict in self.client_fields_frames:
            field_data_dict["frame"].destroy()
        self.client_fields_frames = []

        current_row = self.client_fields_start_row
        for idx, field_data in enumerate(config_manager.CLIENT_FIELDS_CONFIG):
            field_frame = ctk.CTkFrame(self.scrollable_frame)
            field_frame.grid(row=current_row + idx, column=0, columnspan=4, padx=5, pady=2, sticky="ew")
            field_frame.grid_columnconfigure(1, weight=1)
            field_frame.grid_columnconfigure(3, weight=1)

            ctk.CTkLabel(field_frame, text="Nome:").grid(row=0, column=0, padx=2, pady=2, sticky=ctk.W)
            name_entry = ctk.CTkEntry(field_frame, width=100)
            name_entry.insert(0, field_data["name"])
            name_entry.grid(row=0, column=1, padx=2, pady=2, sticky=ctk.EW)

            ctk.CTkLabel(field_frame, text="Max Len:").grid(row=0, column=2, padx=2, pady=2, sticky=ctk.W)
            max_length_entry = ctk.CTkEntry(field_frame, width=50)
            max_length_entry.insert(0, str(field_data["max_length"]))
            max_length_entry.grid(row=0, column=3, padx=2, pady=2, sticky=ctk.EW)

            ctk.CTkLabel(field_frame, text="Obrigatório:").grid(row=1, column=0, padx=2, pady=2, sticky=ctk.W)
            required_var = ctk.BooleanVar(value=field_data["required"])
            required_checkbox = ctk.CTkCheckBox(field_frame, text="", variable=required_var)
            required_checkbox.grid(row=1, column=1, padx=2, pady=2, sticky=ctk.W)

            ctk.CTkLabel(field_frame, text="Coluna DB:").grid(row=1, column=2, padx=2, pady=2, sticky=ctk.W)
            db_column_label = ctk.CTkLabel(field_frame, text=field_data["db_column"]) # Read-only
            db_column_label.grid(row=1, column=3, padx=2, pady=2, sticky=ctk.W)

            btn_remove = ctk.CTkButton(field_frame, text="Remover", command=lambda i=idx: self.remove_client_field(i), width=80, fg_color="red", hover_color="darkred")
            btn_remove.grid(row=0, column=4, rowspan=2, padx=5, pady=5, sticky="ns")

            self.client_fields_frames.append({
                "frame": field_frame,
                "name_entry": name_entry,
                "max_length_entry": max_length_entry,
                "required_var": required_var,
                "db_column": field_data["db_column"] # Store db_column as it's read-only
            })

    def add_client_field(self):
        # Open a new dialog for adding a field
        AddFieldDialog(self, self.main_app_root, self.render_client_fields)

    def remove_client_field(self, index):
        if messagebox.askyesno("Confirmar Remoção", f"Tem certeza que deseja remover o campo '{config_manager.CLIENT_FIELDS_CONFIG[index]['name']}'?"):
            # Destroy the specific frame
            self.client_fields_frames[index]["frame"].destroy()
            
            # Remove the field from CLIENT_FIELDS_CONFIG and self.client_fields_frames
            del config_manager.CLIENT_FIELDS_CONFIG[index]
            del self.client_fields_frames[index]

            # Re-grid the remaining frames to fill the gap
            current_row = self.client_fields_start_row
            for idx, field_data_dict in enumerate(self.client_fields_frames):
                field_data_dict["frame"].grid(row=current_row + idx, column=0, columnspan=4, padx=5, pady=2, sticky="ew")
                # Update the command for the remove button to reflect new indices
                field_data_dict["frame"].winfo_children()[-1].configure(command=lambda i=idx: self.remove_client_field(i))

            messagebox.showinfo("Campo Removido", "Campo removido com sucesso. Salve as configurações para aplicar.")

    def load_settings(self):
        for key, entry in self.db_settings_entries.items():
            entry.delete(0, ctk.END)
            entry.insert(0, config_manager.DB_CONFIG.get(key, ""))
        
        for key, entry in self.internal_default_entries.items():
            entry.delete(0, ctk.END)
            entry.insert(0, config_manager.INTERNAL_DEFAULT_FIELDS.get(key, ""))
        
        self.render_client_fields() # Load and render client fields

    def save_settings(self):
        new_db_config = {}
        for key, entry in self.db_settings_entries.items():
            value = entry.get().strip()
            if not value:
                messagebox.showerror("Erro de Validação", f"'{key}' não pode ser vazio.")
                return
            new_db_config[key] = value
        
        new_internal_default_fields = {}
        for key, entry in self.internal_default_entries.items():
            value = entry.get().strip()
            if not value:
                messagebox.showerror("Erro de Validação", f"'{key}' não pode ser vazio.")
                return
            new_internal_default_fields[key] = value

        new_client_fields_config = []
        for field_frame_data in self.client_fields_frames:
            name = field_frame_data["name_entry"].get().strip()
            max_length_str = field_frame_data["max_length_entry"].get().strip()
            required = field_frame_data["required_var"].get()
            db_column = field_frame_data["db_column"] # Use the stored db_column

            if not name:
                messagebox.showerror("Erro de Validação", "Nome do campo não pode ser vazio.")
                return
            try:
                max_length = int(max_length_str)
                if max_length <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Erro de Validação", f"Comprimento máximo para '{name}' deve ser um número inteiro positivo.")
                return
            
            new_client_fields_config.append({
                "name": name,
                "max_length": max_length,
                "required": required,
                "db_column": db_column
            })
        
        config_manager.update_and_save_config(
            new_client_fields_config=new_client_fields_config,
            new_db_config=new_db_config,
            new_internal_default_fields=new_internal_default_fields
        )
        
        messagebox.showinfo("Configurações Salvas", "Configurações atualizadas com sucesso.")
        self.refresh_callback() # Callback to refresh the main form
        self.destroy() # Close the settings window after saving

    def reset_to_defaults(self):
        if messagebox.askyesno("Confirmar Reset", "Tem certeza que deseja resetar todas as configurações para o padrão de fábrica? Esta ação não pode ser desfeita."):
            config_manager.reset_config_to_defaults()
            self.load_settings() # Reload settings in the current window
            self.refresh_callback() # Refresh the main form
            messagebox.showinfo("Reset Concluído", "Todas as configurações foram resetadas para o padrão de fábrica.")

    def remove_client_field(self, index):
        if messagebox.askyesno("Confirmar Remoção", f"Tem certeza que deseja remover o campo '{config_manager.CLIENT_FIELDS_CONFIG[index]['name']}'?"):
            del config_manager.CLIENT_FIELDS_CONFIG[index]
            self.render_client_fields()
            messagebox.showinfo("Campo Removido", "Campo removido com sucesso. Salve as configurações para aplicar.")

    def load_settings(self):
        for key, entry in self.db_settings_entries.items():
            entry.delete(0, ctk.END)
            entry.insert(0, config_manager.DB_CONFIG.get(key, ""))
        
        for key, entry in self.internal_default_entries.items():
            entry.delete(0, ctk.END)
            entry.insert(0, config_manager.INTERNAL_DEFAULT_FIELDS.get(key, ""))
        
        self.render_client_fields() # Load and render client fields

    def save_settings(self):
        new_db_config = {}
        for key, entry in self.db_settings_entries.items():
            value = entry.get().strip()
            if not value:
                messagebox.showerror("Erro de Validação", f"'{key}' não pode ser vazio.")
                return
            new_db_config[key] = value
        
        new_internal_default_fields = {}
        for key, entry in self.internal_default_entries.items():
            value = entry.get().strip()
            if not value:
                messagebox.showerror("Erro de Validação", f"'{key}' não pode ser vazio.")
                return
            new_internal_default_fields[key] = value

        new_client_fields_config = []
        for field_frame_data in self.client_fields_frames:
            name = field_frame_data["name_entry"].get().strip()
            max_length_str = field_frame_data["max_length_entry"].get().strip()
            required = field_frame_data["required_var"].get()
            db_column = field_frame_data["db_column"] # Use the stored db_column

            if not name:
                messagebox.showerror("Erro de Validação", "Nome do campo não pode ser vazio.")
                return
            try:
                max_length = int(max_length_str)
                if max_length <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Erro de Validação", f"Comprimento máximo para '{name}' deve ser um número inteiro positivo.")
                return
            
            new_client_fields_config.append({
                "name": name,
                "max_length": max_length,
                "required": required,
                "db_column": db_column
            })
        
        config_manager.update_and_save_config(
            new_client_fields_config=new_client_fields_config,
            new_db_config=new_db_config,
            new_internal_default_fields=new_internal_default_fields
        )
        
        messagebox.showinfo("Configurações Salvas", "Configurações atualizadas com sucesso.")
        self.refresh_callback() # Callback to refresh the main form
        self.destroy() # Close the settings window after saving


class ClientRegistrationApp(ctk.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Client Registration")
        self.geometry("750x750")
        self.grab_set() # Make it a modal window

        # Configure grid weights for better resizing behavior
        self.grid_columnconfigure(1, weight=1)

        self.entry_widgets = {}
        self.setup_gui_elements()

    def setup_gui_elements(self):
        for idx, field in enumerate(FIELDS):
            ctk.CTkLabel(self, text=f"{field}:").grid(row=idx, column=0, padx=10, pady=5, sticky=ctk.W)
            entry = ctk.CTkEntry(self, width=300)
            entry.grid(row=idx, column=1, padx=5, pady=5, sticky=ctk.EW)
            self.entry_widgets[field] = entry

        if "CEP" in self.entry_widgets:
            self.entry_widgets["CEP"].bind("<FocusOut>", self.on_cep_focus_out)
        
        # Frame for buttons
        button_frame = ctk.CTkFrame(self)
        button_frame.grid(row=len(FIELDS), column=0, columnspan=2, pady=20, sticky="nsew")
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        button_frame.columnconfigure(2, weight=1) # Added column for settings button

        btn_register = ctk.CTkButton(button_frame, text="Register Client", command=self.handle_insert_client, fg_color="#1F6AA5", hover_color="#144870")
        btn_register.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        btn_clear = ctk.CTkButton(button_frame, text="Clear All", command=self.clear_form_fields, fg_color="#A51F1F", hover_color="#701414")
        btn_clear.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        btn_settings = ctk.CTkButton(button_frame, text="Settings", command=self.open_settings_window, fg_color="#23A51F", hover_color="#147023")
        btn_settings.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")

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
            conn.close()

    def handle_insert_client(self):
        """
        Coleta dados do formulário, valida-os e tenta inseri-los no banco de dados.
        """
        # Access INTERNAL_DEFAULT_FIELDS directly from the config_manager module
        config_manager.INTERNAL_DEFAULT_FIELDS["XCLIENTES"] = self.get_next_xclientes()

        client_data = {field: self.entry_widgets[field].get().strip() for field in self.entry_widgets}
        client_data.update(config_manager.INTERNAL_DEFAULT_FIELDS)

        validation_errors = validate_fields(client_data)
        if validation_errors:
            messagebox.showerror("Validation Error", "\n".join(validation_errors))
            return

        if insert_client_data(client_data):
            messagebox.showinfo("sucesso", "cliente registrado com sucesso!")
            self.clear_form_fields()
        else:
            messagebox.showerror("Erro", "não foi possivel enviar.")

    def clear_form_fields(self):
        """Limpa todos os campos de entrada no formulário."""
        for field in FIELDS:
            if field in self.entry_widgets:
                self.entry_widgets[field].delete(0, ctk.END)

    def fetch_address_thread(self, cep):
        """Obtém detalhes de endereço da API ViaCEP em um thread para evitar travamentos na tela aguardando a API"""
        try:
            response = requests.get(f"https://viacep.com.br/ws/{cep}/json/", timeout=5)
            response.raise_for_status()
            data = response.json()

            if "erro" in data:
                self.after(0, lambda: messagebox.showwarning("Invalid CEP", "CEP not found."))
            else:
                self.after(0, self.fill_address_fields, data)
        except requests.exceptions.Timeout:
            self.after(0, lambda: messagebox.showerror("CEP Lookup Error", "CEP lookup timed out."))
        except requests.exceptions.RequestException as e:
            self.after(0, lambda: messagebox.showerror("CEP Lookup Error", f"Error fetching CEP: {e}"))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Unexpected Error", f"An unexpected error occurred: {e}"))

    def on_cep_focus_out(self, event):
        """Valida o CEP e retorna erro caso esteja errado"""
        cep = self.entry_widgets["CEP"].get().strip().replace("-", "").replace(".", "")
        if re.fullmatch(r'\d{8}', cep):
            threading.Thread(target=self.fetch_address_thread, args=(cep,), daemon=True).start()
        elif cep:
            messagebox.showwarning("Invalid CEP Format", "Please enter a valid 8-digit CEP.")

    def fill_address_fields(self, address_data):
        """adiciona os campos caso o cep esteja correto e a API tenha retornado"""
        field_mapping = {
            "ENDERECO": "logradouro",
            "LOGRA": "logradouro",
            "BAIRRO": "bairro",
            "CIDADE": "localidade",
            "ESTADO": "uf",
        }
        for form_field, json_key in field_mapping.items():
            self.entry_widgets[form_field].delete(0, ctk.END)
            self.entry_widgets[form_field].insert(0, address_data.get(json_key, ""))

    def open_settings_window(self):
        SettingsWindow(self, self.master, self.setup_gui_elements) # Pass master and a callback to refresh the form

if __name__ == "__main__":
    root = ctk.CTk()
    root.withdraw() # Hide the main window
    app = ClientRegistrationApp(root)
    root.mainloop()
