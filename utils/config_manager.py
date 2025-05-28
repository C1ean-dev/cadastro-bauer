import json
import os

class ConfigManager:
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

    DEFAULT_APP_SETTINGS = {
        "APP_WIDTH": 800,
        "APP_HEIGHT": 750
    }

    def __init__(self):
        self.app_config = self._load_config()
        self.CLIENT_FIELDS_CONFIG = self.app_config["CLIENT_FIELDS_CONFIG"]
        self.DB_CONFIG = self.app_config["DB_CONFIG"]
        self.INTERNAL_DEFAULT_FIELDS = self.app_config["INTERNAL_DEFAULT_FIELDS"]
        self.APP_SETTINGS = self.app_config["APP_SETTINGS"]

    def _load_config(self):
        """Loads configuration from app_config.json or returns defaults, merging new defaults if necessary."""
        config = {
            "CLIENT_FIELDS_CONFIG": self.DEFAULT_CLIENT_FIELDS_CONFIG,
            "DB_CONFIG": self.DEFAULT_DB_CONFIG,
            "INTERNAL_DEFAULT_FIELDS": self.DEFAULT_INTERNAL_DEFAULT_FIELDS,
            "APP_SETTINGS": self.DEFAULT_APP_SETTINGS
        }
        if os.path.exists(self.CONFIG_FILE):
            with open(self.CONFIG_FILE, 'r') as f:
                loaded_config = json.load(f)
                config.update(loaded_config)
                if "APP_SETTINGS" in loaded_config and isinstance(loaded_config["APP_SETTINGS"], dict):
                    config["APP_SETTINGS"].update(loaded_config["APP_SETTINGS"])
                self._save_config(config)
        return config

    def _save_config(self, config):
        """Saves the current configuration to app_config.json."""
        with open(self.CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)

    def update_and_save_config(self, new_client_fields_config=None, new_db_config=None, new_internal_default_fields=None, new_app_settings=None):
        """Updates config variables and saves the entire config."""
        if new_client_fields_config is not None:
            self.CLIENT_FIELDS_CONFIG = new_client_fields_config
            self.app_config["CLIENT_FIELDS_CONFIG"] = new_client_fields_config
        
        if new_db_config is not None:
            self.DB_CONFIG = new_db_config
            self.app_config["DB_CONFIG"] = new_db_config

        if new_internal_default_fields is not None:
            self.INTERNAL_DEFAULT_FIELDS = new_internal_default_fields
            self.app_config["INTERNAL_DEFAULT_FIELDS"] = new_internal_default_fields

        if new_app_settings is not None:
            self.APP_SETTINGS = new_app_settings
            self.app_config["APP_SETTINGS"] = new_app_settings

        self._save_config(self.app_config)

    def reset_config_to_defaults(self):
        """Resets all configurations to their default values and saves them."""
        self.CLIENT_FIELDS_CONFIG = self.DEFAULT_CLIENT_FIELDS_CONFIG
        self.DB_CONFIG = self.DEFAULT_DB_CONFIG
        self.INTERNAL_DEFAULT_FIELDS = self.DEFAULT_INTERNAL_DEFAULT_FIELDS
        self.APP_SETTINGS = self.DEFAULT_APP_SETTINGS
        
        self.app_config = {
            "CLIENT_FIELDS_CONFIG": self.CLIENT_FIELDS_CONFIG,
            "DB_CONFIG": self.DB_CONFIG,
            "INTERNAL_DEFAULT_FIELDS": self.INTERNAL_DEFAULT_FIELDS,
            "APP_SETTINGS": self.APP_SETTINGS
        }
        self._save_config(self.app_config)
