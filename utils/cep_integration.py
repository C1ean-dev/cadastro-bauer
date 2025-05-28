import requests
import threading
import re
import customtkinter as ctk

def fetch_address_thread(cep, callback_success, callback_error):
    """Obtém detalhes de endereço da API ViaCEP em um thread para evitar travamentos na tela aguardando a API"""
    try:
        response = requests.get(f"https://viacep.com.br/ws/{cep}/json/", timeout=5)
        response.raise_for_status()
        data = response.json()

        if "erro" in data:
            callback_error("Invalid CEP", "CEP not found.")
        else:
            callback_success(data)
    except requests.exceptions.Timeout:
        callback_error("CEP Lookup Error", "CEP lookup timed out.")
    except requests.exceptions.RequestException as e:
        callback_error("CEP Lookup Error", f"Error fetching CEP: {e}")
    except Exception as e:
        callback_error("Unexpected Error", f"An unexpected error occurred: {e}")

def on_cep_focus_out(cep_entry_widget, fill_address_callback, show_warning_callback, show_error_callback):
    """Valida o CEP e retorna erro caso esteja errado"""
    cep = cep_entry_widget.get().strip().replace("-", "").replace(".", "")
    if re.fullmatch(r'\d{8}', cep):
        threading.Thread(target=fetch_address_thread, args=(cep, fill_address_callback, show_error_callback), daemon=True).start()
    elif cep:
        show_warning_callback("Invalid CEP Format", "Please enter a valid 8-digit CEP.")

def fill_address_fields(entry_widgets, address_data):
    """adiciona os campos caso o cep esteja correto e a API tenha retornado"""
    field_mapping = {
        "ENDERECO": "logradouro",
        "LOGRA": "logradouro",
        "BAIRRO": "bairro",
        "CIDADE": "localidade",
        "ESTADO": "uf",
    }
    for form_field, json_key in field_mapping.items():
        if form_field in entry_widgets:
            entry_widgets[form_field].delete(0, ctk.END) # ctk is not imported here, need to pass it or import
            entry_widgets[form_field].insert(0, address_data.get(json_key, ""))
