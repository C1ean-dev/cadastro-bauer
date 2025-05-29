import customtkinter as ctk
from tkinter import messagebox
from cadastro.client_registration_app import ClientRegistrationApp
from update.client_update_app import ClientUpdateApp
from delete.client_delete_app import ClientDeleteApp
from read.client_read_app import ClientReadApp
from utils.centerWindow import centerWindow
from utils.config_manager import ConfigManager
from utils.updater import AppUpdater # Import the updater
from utils.settings_window import SettingsWindow # Import SettingsWindow

class MainMenuApp:
    def __init__(self, root):
        self.config_manager = ConfigManager() # Create an instance
        self.root = root
        self.root.title("Menu Principal")
        self.root.geometry(centerWindow.center_window(self,root, self.config_manager.APP_SETTINGS["APP_WIDTH"], self.config_manager.APP_SETTINGS["APP_HEIGHT"]))
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        # Initialize and check for updates
        current_app_version = "0.0.0-dev" # Default to development version
        try:
            import version
            current_app_version = version.__version__
            # Only run updater if a proper version is found (i.e., not in local dev)
            self.updater = AppUpdater(
                repo_owner="C1ean-dev", 
                repo_name="cadastro-bauer", 
                current_version=current_app_version
            )
            self.updater.check_for_updates()
        except ImportError:
            print("Warning: version.py not found. Running in development mode, update checks skipped.")
            # No updater initialized if in development mode

        self.create_widgets()

    def create_widgets(self):
        # Create a frame to hold the buttons
        button_frame = ctk.CTkFrame(self.root)
        button_frame.pack(expand=True, fill='both', pady=20) # Center the frame and make it expand

        # Botão Criar
        btn_create = ctk.CTkButton(button_frame, text="Criar Cliente", command=self.open_create_client_screen,
                                   fg_color="#28a745", hover_color="#218838")
        btn_create.pack(pady=10, fill='x', padx=20)

        # Botão Ler
        btn_read = ctk.CTkButton(button_frame, text="Ler Cliente", command=self.open_read_client_screen,
                                 fg_color="#007bff", hover_color="#0056b3")
        btn_read.pack(pady=10, fill='x', padx=20)

        # Botão Atualizar
        btn_update = ctk.CTkButton(button_frame, text="Atualizar Cliente", command=self.open_update_client_screen,
                                   fg_color="#9c07ff", hover_color="#41016b") 
        btn_update.pack(pady=10, fill='x', padx=20)

        # Botão Deletar
        btn_delete = ctk.CTkButton(button_frame, text="Deletar Cliente", command=self.open_delete_client_screen,
                                   fg_color="#dc3545", hover_color="#c82333")
        btn_delete.pack(pady=10, fill='x', padx=20)

        # Botão Configurações
        btn_settings = ctk.CTkButton(button_frame, text="Configurações", command=self.open_settings_screen,
                                     fg_color="#6c757d", hover_color="#5a6268")
        btn_settings.pack(pady=10, fill='x', padx=20)


    def open_create_client_screen(self):
        # esconde o menu enquanto client estiver aberto
        self.root.withdraw()
        
        # abre a tela do cliente 
        client_app = ClientRegistrationApp(self.root)
        client_app.protocol("WM_DELETE_WINDOW", lambda: self.on_client_app_close(client_app))
        
    def on_client_app_close(self, client_app_instance):
        # quando o cliente fechar a tela destroi a instancia do cliente
        client_app_instance.destroy()
        # aber novamente o menu 
        self.root.deiconify() 

    def open_read_client_screen(self):
        client_app = ClientReadApp(self.root)
        client_app.protocol("WM_DELETE_WINDOW", lambda: self.on_client_app_close(client_app))

    def open_update_client_screen(self):
        client_app = ClientUpdateApp(self.root)
        client_app.protocol("WM_DELETE_WINDOW", lambda: self.on_client_app_close(client_app))

    def open_delete_client_screen(self):
        client_app = ClientDeleteApp(self.root)
        client_app.protocol("WM_DELETE_WINDOW", lambda: self.on_client_app_close(client_app))

    def open_settings_screen(self):
        # Pass self.root as master and a dummy function for on_close_callback if not needed
        settings_window = SettingsWindow(self.root, self.root, lambda: None) 
        settings_window.protocol("WM_DELETE_WINDOW", lambda: self.on_client_app_close(settings_window))


if __name__ == "__main__":
    root = ctk.CTk()
    app = MainMenuApp(root)
    root.mainloop()
