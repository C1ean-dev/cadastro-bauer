import customtkinter as ctk
from tkinter import messagebox
from utils.add_field_dialog import AddFieldDialog # Import the new dialog
from utils.centerWindow import centerWindow
from utils.config_manager import ConfigManager

config_manager = ConfigManager()

class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, master, main_app_root, refresh_callback):
        super().__init__(master)
        self.main_app_root = main_app_root
        self.refresh_callback = refresh_callback
        self.title("Configurações")
        # Increased size for CLIENT_FIELDS_CONFIG
        self.geometry(centerWindow.center_window(self, master,config_manager.APP_SETTINGS["APP_WIDTH"], config_manager.APP_SETTINGS["APP_HEIGHT"]))
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
