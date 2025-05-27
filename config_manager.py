import json
import os

CONFIG_FILE = "app_config.json"

DEFAULT_CLIENT_FIELDS_CONFIG = [
    {"name": "NRECNO", "max_length": 10, "required": False, "db_column": "NRECNO"},
    {"name": "CLIENTE", "max_length": 100, "required": True, "db_column": "RAZAO"},
    {"name": "CGC", "max_length": 20, "required": True, "db_column": "CGC"},
    {"name": "INSCRICAO", "max_length": 20, "required": False, "db_column": "INSCRICAO"},
    {"name": "LOGRADOURO", "max_length": 20, "required": False, "db_column": "LOGRA"},
    {"name": "ENDERECO", "max_length": 250, "required": False, "db_column": "ENDERECO"},
    {"name": "NUMERO", "max_length": 15, "required": False, "db_column": "NUMERO"},
    {"name": "BAIRRO", "max_length": 60, "required": False, "db_column": "BAIRRO"},
    {"name": "CIDADE", "max_length": 40, "required": False, "db_column": "CIDADE"},
    {"name": "ESTADO", "max_length": 10, "required": False, "db_column": "ESTADO"},
    {"name": "CJ", "max_length": 250, "required": False, "db_column": "CJ"},
    {"name": "CEP", "max_length": 10, "required": False, "db_column": "CEP"},
    {"name": "FAX", "max_length": 23, "required": False, "db_column": "FAX"},
    {"name": "TEL1", "max_length": 23, "required": False, "db_column": "TEL1"},
    {"name": "TEL2", "max_length": 23, "required": False, "db_column": "TEL2"},
    {"name": "EMAIL", "max_length": 255, "required": False, "db_column": "EMAIL"},
    {"name": "ZONA", "max_length": 20, "required": False, "db_column": "ZONA"},
    {"name": "XCLIENTES", "max_length": 10, "required": True, "db_column": "XCLIENTES"}
]

DEFAULT_DB_CONFIG = {
    'DRIVER': '{ODBC Driver 17 for SQL Server}',
    'SERVER': '192.168.4.17,1433',
    'DATABASE': 'SM11_PROD',
    'UID': 'sa',
    'PWD': '*f4lc40$'
}

DEFAULT_INTERNAL_DEFAULT_FIELDS = {
    "WORKFLOW_TYPE": "GENERAL",
    "APPROVAL_STATUS": "A",
    "ADIMPLENTE": "T",
}

def load_config():
    """Loads configuration from app_config.json or returns defaults."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {
        "CLIENT_FIELDS_CONFIG": DEFAULT_CLIENT_FIELDS_CONFIG,
        "DB_CONFIG": DEFAULT_DB_CONFIG,
        "INTERNAL_DEFAULT_FIELDS": DEFAULT_INTERNAL_DEFAULT_FIELDS
    }

def save_config(config):
    """Saves the current configuration to app_config.json."""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

# Initialize global config variables
app_config = load_config()
CLIENT_FIELDS_CONFIG = app_config["CLIENT_FIELDS_CONFIG"]
DB_CONFIG = app_config["DB_CONFIG"]
INTERNAL_DEFAULT_FIELDS = app_config["INTERNAL_DEFAULT_FIELDS"]

def update_and_save_config(new_client_fields_config=None, new_db_config=None, new_internal_default_fields=None):
    """Updates global config variables and saves the entire config."""
    global CLIENT_FIELDS_CONFIG, DB_CONFIG, INTERNAL_DEFAULT_FIELDS, app_config
    
    if new_client_fields_config is not None:
        CLIENT_FIELDS_CONFIG = new_client_fields_config
        app_config["CLIENT_FIELDS_CONFIG"] = new_client_fields_config
    
    if new_db_config is not None:
        DB_CONFIG = new_db_config
        app_config["DB_CONFIG"] = new_db_config

    if new_internal_default_fields is not None:
        INTERNAL_DEFAULT_FIELDS = new_internal_default_fields
        app_config["INTERNAL_DEFAULT_FIELDS"] = new_internal_default_fields

    save_config(app_config)

def reset_config_to_defaults():
    """Resets all configurations to their default values and saves them."""
    global CLIENT_FIELDS_CONFIG, DB_CONFIG, INTERNAL_DEFAULT_FIELDS, app_config
    
    CLIENT_FIELDS_CONFIG = DEFAULT_CLIENT_FIELDS_CONFIG
    DB_CONFIG = DEFAULT_DB_CONFIG
    INTERNAL_DEFAULT_FIELDS = DEFAULT_INTERNAL_DEFAULT_FIELDS
    
    app_config = {
        "CLIENT_FIELDS_CONFIG": CLIENT_FIELDS_CONFIG,
        "DB_CONFIG": DB_CONFIG,
        "INTERNAL_DEFAULT_FIELDS": INTERNAL_DEFAULT_FIELDS
    }
    save_config(app_config)
