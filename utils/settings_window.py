from tkinter import messagebox
from utils.config_manager import ConfigManager
from utils.settings_window_gui import SettingsWindowGUI

config_manager = ConfigManager()

class SettingsWindow(SettingsWindowGUI):
    def __init__(self, master, main_app_root, refresh_callback):
        super().__init__(master, main_app_root, refresh_callback)
        # The GUI setup is now handled by SettingsWindowGUI's __init__
        # We only need to ensure the commands for buttons are correctly linked
        # These commands are defined in this class (business logic)

import customtkinter as ctk # Import ctk to use ctk.END
from tkinter import messagebox
from utils.config_manager import ConfigManager
from utils.settings_window_gui import SettingsWindowGUI

config_manager = ConfigManager()

class SettingsWindow(SettingsWindowGUI):
    def __init__(self, master, main_app_root, refresh_callback):
        super().__init__(master, main_app_root, refresh_callback)
        # The GUI setup is now handled by SettingsWindowGUI's __init__
        # We only need to ensure the commands for buttons are correctly linked
        # These commands are defined in this class (business logic)

    def load_settings(self):
        # Override the GUI's load_settings to use the actual config_manager
        for key, entry in self.db_settings_entries.items():
            entry.delete(0, ctk.END) # Changed messagebox.END to ctk.END
            entry.insert(0, config_manager.DB_CONFIG.get(key, ""))
        
        for key, entry in self.internal_default_entries.items():
            entry.delete(0, ctk.END) # Changed messagebox.END to ctk.END
            entry.insert(0, config_manager.INTERNAL_DEFAULT_FIELDS.get(key, ""))
        
        self.render_client_fields()

    def add_client_field(self):
        # This method is called by the GUI, but the logic for adding a field
        # (which involves updating config_manager.CLIENT_FIELDS_CONFIG)
        # should be handled here.
        # The AddFieldDialog will call render_client_fields on completion.
        super().add_client_field() # Call the GUI method to open the dialog

    def remove_client_field(self, index):
        # This method is called by the GUI, but the logic for removing a field
        # (which involves updating config_manager.CLIENT_FIELDS_CONFIG)
        # should be handled here.
        if messagebox.askyesno("Confirmar Remoção", f"Tem certeza que deseja remover o campo '{config_manager.CLIENT_FIELDS_CONFIG[index]['name']}'?"):
            # Destroy the specific frame (GUI part)
            self.client_fields_frames[index]["frame"].destroy()
            
            # Remove the field from CLIENT_FIELDS_CONFIG (Logic part)
            del config_manager.CLIENT_FIELDS_CONFIG[index]
            # The line below is problematic as it removes from the list that is being iterated over
            # del self.client_fields_frames[index] # Also remove from GUI's list

            # Re-grid the remaining frames to fill the gap (GUI part)
            # This part needs to be re-evaluated as deleting from self.client_fields_frames
            # while iterating or immediately after can cause issues.
            # A simpler approach for testing is to just ensure the config is updated.
            # For the actual GUI, render_client_fields should be called to rebuild the GUI.
            # Let's simplify the test's interaction with this.
            # For the actual code, we should call render_client_fields after deletion.
            self.render_client_fields() # Re-render GUI after removal

            messagebox.showinfo("Campo Removido", "Campo removido com sucesso. Salve as configurações para aplicar.")


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
            db_column = field_frame_data["db_column"]

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
        self.refresh_callback()
        self.destroy()

    def reset_to_defaults(self):
        if messagebox.askyesno("Confirmar Reset", "Tem certeza que deseja resetar todas as configurações para o padrão de fábrica? Esta ação não pode ser desfeita."):
            config_manager.reset_config_to_defaults()
            self.load_settings()
            self.refresh_callback()
            messagebox.showinfo("Reset Concluído", "Todas as configurações foram resetadas para o padrão de fábrica.")
