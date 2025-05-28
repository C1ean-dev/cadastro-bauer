import customtkinter as ctk
from tkinter import messagebox
from utils.centerWindow import centerWindow
from utils.config_manager import ConfigManager

config_manager = ConfigManager()

class AddFieldDialog(ctk.CTkToplevel):
    def __init__(self, master, main_app_root, refresh_callback):
        super().__init__(master)
        self.master = master
        self.main_app_root = main_app_root
        self.refresh_callback = refresh_callback
        self.title("Adicionar Novo Campo")
        self.geometry(centerWindow.center_window(self, config_manager.APP_SETTINGS["APP_WIDTH"], config_manager.APP_SETTINGS["APP_HEIGHT"]))
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
