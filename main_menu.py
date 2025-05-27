import customtkinter as ctk
from tkinter import messagebox
from cliente_cadastro_gui import ClientRegistrationApp

class MainMenuApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Menu Principal")
        self.root.geometry("300x200")
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.create_widgets()

    def create_widgets(self):
        # Botão Criar
        btn_create = ctk.CTkButton(self.root, text="Criar Cliente", command=self.open_create_client_screen)
        btn_create.pack(pady=10)

        # Botão Ler
        btn_read = ctk.CTkButton(self.root, text="Ler Cliente", command=self.open_read_client_screen)
        btn_read.pack(pady=10)

        # Botão Atualizar
        btn_update = ctk.CTkButton(self.root, text="Atualizar Cliente", command=self.open_update_client_screen)
        btn_update.pack(pady=10)

        # Botão Deletar
        btn_delete = ctk.CTkButton(self.root, text="Deletar Cliente", command=self.open_delete_client_screen)
        btn_delete.pack(pady=10)

    def open_create_client_screen(self):
        # Hide the main menu window
        self.root.withdraw()
        
        # Open the client registration screen
        client_app = ClientRegistrationApp(self.root)
        client_app.protocol("WM_DELETE_WINDOW", lambda: self.on_client_app_close(client_app))
        
    def on_client_app_close(self, client_app_instance):
        client_app_instance.destroy()
        self.root.deiconify() # Show the main menu window again

    def open_read_client_screen(self):
        messagebox.showinfo("Ação", "Abrir tela de Ler Cliente")

    def open_update_client_screen(self):
        messagebox.showinfo("Ação", "Abrir tela de Atualizar Cliente")

    def open_delete_client_screen(self):
        messagebox.showinfo("Ação", "Abrir tela de Deletar Cliente")

if __name__ == "__main__":
    root = ctk.CTk()
    app = MainMenuApp(root)
    root.mainloop()
