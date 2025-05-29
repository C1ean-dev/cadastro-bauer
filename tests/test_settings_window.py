import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.settings_window import SettingsWindow
from utils.config_manager import ConfigManager
import customtkinter as ctk

class TestSettingsWindow(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.root = ctk.CTk()
        cls.root.withdraw()

    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()

    def setUp(self):
        # Patch messagebox and config_manager where they are imported/used in utils.settings_window
        self.patch_messagebox = patch('utils.settings_window.messagebox').start()
        self.mock_config_manager_instance = MagicMock(spec=ConfigManager)
        self.patch_config_manager_global = patch('utils.settings_window.config_manager', self.mock_config_manager_instance).start()

        # Configure the mocked config_manager_instance
        self.mock_config_manager_instance.DB_CONFIG = {"Server": "old_server", "Database": "old_db"}
        self.mock_config_manager_instance.INTERNAL_DEFAULT_FIELDS = {"Field1": "old_val1", "XCLIENTES": "123"}
        self.mock_config_manager_instance.CLIENT_FIELDS_CONFIG = [
            {"name": "Name1", "max_length": 10, "required": True, "db_column": "DB_NAME1"},
            {"name": "Name2", "max_length": 20, "required": False, "db_column": "DB_NAME2"}
        ]
        self.mock_config_manager_instance.APP_SETTINGS = {"APP_WIDTH": 800, "APP_HEIGHT": 600}

        # Mock the super().__init__ to avoid full GUI initialization
        self.mock_super_init = patch('utils.settings_window_gui.SettingsWindowGUI.__init__', MagicMock(return_value=None)).start()
        # Mock GUI methods that are called by the business logic
        self.mock_create_widgets = patch('utils.settings_window_gui.SettingsWindowGUI.create_widgets').start()
        self.mock_render_client_fields = patch('utils.settings_window_gui.SettingsWindowGUI.render_client_fields').start()
        
        # Mock AddFieldDialog's __init__ to prevent it from trying to create a real CTkToplevel
        # Mock AddFieldDialog class directly
        self.mock_add_field_dialog_class = patch('utils.settings_window_gui.AddFieldDialog').start()
        # Mock the destroy method of the SettingsWindow instance itself
        self.mock_destroy = patch.object(SettingsWindow, 'destroy', MagicMock()).start()


        self.mock_refresh_callback = MagicMock()
        self.app = SettingsWindow(self.root, self.root, self.mock_refresh_callback)

        # Manually set attributes that are normally set by GUI init/create_widgets
        self.app.main_app_root = self.root
        self.app.refresh_callback = self.mock_refresh_callback

        # Initialize entries with mock objects for their methods, allowing get.return_value to be set later
        self.app.db_settings_entries = {
            "Server": MagicMock(delete=MagicMock(), insert=MagicMock()),
            "Database": MagicMock(delete=MagicMock(), insert=MagicMock())
        }
        self.app.internal_default_entries = {
            "Field1": MagicMock(delete=MagicMock(), insert=MagicMock())
        }
        # Set default return values for get methods
        self.app.db_settings_entries["Server"].get.return_value = "new_server"
        self.app.db_settings_entries["Database"].get.return_value = "new_db"
        self.app.internal_default_entries["Field1"].get.return_value = "new_val1"

        # Ensure client_fields_frames is a list of mocks with a 'frame' attribute that has a 'destroy' method
        # Initialize name_entry and max_length_entry as MagicMocks to allow setting return_value
        self.app.client_fields_frames = [
            {"frame": MagicMock(destroy=MagicMock()), "name_entry": MagicMock(), "max_length_entry": MagicMock(), "required_var": MagicMock(get=lambda: False), "db_column": "DB_NAME1"},
            {"frame": MagicMock(destroy=MagicMock()), "name_entry": MagicMock(), "max_length_entry": MagicMock(), "required_var": MagicMock(get=lambda: True), "db_column": "DB_NAME2"}
        ]
        # Set default return values for client field entries
        self.app.client_fields_frames[0]["name_entry"].get.return_value = "UpdatedName1"
        self.app.client_fields_frames[0]["max_length_entry"].get.return_value = "15"
        self.app.client_fields_frames[1]["name_entry"].get.return_value = "UpdatedName2"
        self.app.client_fields_frames[1]["max_length_entry"].get.return_value = "25"
        self.app.client_fields_start_row = 10

    def tearDown(self):
        patch.stopall()

    def test_load_settings(self):
        self.app.load_settings()
        self.app.db_settings_entries["Server"].insert.assert_called_once_with(0, "old_server")
        self.app.db_settings_entries["Database"].insert.assert_called_once_with(0, "old_db")
        self.app.internal_default_entries["Field1"].insert.assert_called_once_with(0, "old_val1")
        self.mock_render_client_fields.assert_called_once()

    def test_save_settings_success(self):
        self.app.save_settings()
        self.mock_config_manager_instance.update_and_save_config.assert_called_once()
        args, kwargs = self.mock_config_manager_instance.update_and_save_config.call_args
        
        expected_db_config = {"Server": "new_server", "Database": "new_db"}
        expected_internal_defaults = {"Field1": "new_val1"}
        expected_client_fields = [
            {"name": "UpdatedName1", "max_length": 15, "required": False, "db_column": "DB_NAME1"},
            {"name": "UpdatedName2", "max_length": 25, "required": True, "db_column": "DB_NAME2"}
        ]

        self.assertEqual(kwargs["new_db_config"], expected_db_config)
        self.assertEqual(kwargs["new_internal_default_fields"], expected_internal_defaults)
        self.assertEqual(kwargs["new_client_fields_config"], expected_client_fields)

        self.patch_messagebox.showinfo.assert_called_once_with("Configurações Salvas", "Configurações atualizadas com sucesso.")
        self.mock_refresh_callback.assert_called_once()
        self.mock_destroy.assert_called_once() # Assert destroy was called

    def test_save_settings_validation_error_db_config(self):
        self.app.db_settings_entries["Server"].get.return_value = "" # Empty value
        self.app.save_settings()
        self.patch_messagebox.showerror.assert_called_once_with("Erro de Validação", "'Server' não pode ser vazio.")
        self.mock_config_manager_instance.update_and_save_config.assert_not_called()
        self.mock_destroy.assert_not_called()

    def test_save_settings_validation_error_client_field_name(self):
        self.app.client_fields_frames[0]["name_entry"].get.return_value = ""
        self.app.save_settings()
        self.patch_messagebox.showerror.assert_called_once_with("Erro de Validação", "Nome do campo não pode ser vazio.")
        self.mock_config_manager_instance.update_and_save_config.assert_not_called()
        self.mock_destroy.assert_not_called()

    def test_save_settings_validation_error_client_field_max_length(self):
        self.app.client_fields_frames[0]["max_length_entry"].get.return_value = "abc"
        self.app.save_settings()
        self.patch_messagebox.showerror.assert_called_once_with("Erro de Validação", "Comprimento máximo para 'UpdatedName1' deve ser um número inteiro positivo.")
        self.mock_config_manager_instance.update_and_save_config.assert_not_called()
        self.mock_destroy.assert_not_called()

    def test_reset_to_defaults_confirmed(self):
        self.patch_messagebox.askyesno.return_value = True
        self.app.reset_to_defaults()
        self.mock_config_manager_instance.reset_config_to_defaults.assert_called_once()
        self.mock_render_client_fields.assert_called_once() # Called by load_settings
        self.mock_refresh_callback.assert_called_once()
        self.patch_messagebox.showinfo.assert_called_once_with("Reset Concluído", "Todas as configurações foram resetadas para o padrão de fábrica.")

    def test_reset_to_defaults_cancelled(self):
        self.patch_messagebox.askyesno.return_value = False
        self.app.reset_to_defaults()
        self.mock_config_manager_instance.reset_config_to_defaults.assert_not_called()
        self.mock_refresh_callback.assert_not_called()
        self.patch_messagebox.showinfo.assert_not_called()

    def test_remove_client_field_confirmed(self):
        self.patch_messagebox.askyesno.return_value = True
        
        # Store original config for comparison
        original_config_len = len(self.mock_config_manager_instance.CLIENT_FIELDS_CONFIG)
        
        # Get the mock frame's destroy method before it might be "lost" by render_client_fields
        mock_frame_destroy = self.app.client_fields_frames[0]["frame"].destroy

        self.app.remove_client_field(0)

        mock_frame_destroy.assert_called_once() # Assert destroy was called on the specific mock frame
        self.assertEqual(len(self.mock_config_manager_instance.CLIENT_FIELDS_CONFIG), original_config_len - 1)
        self.mock_render_client_fields.assert_called_once() # render_client_fields is called after removal
        self.patch_messagebox.showinfo.assert_called_once_with("Campo Removido", "Campo removido com sucesso. Salve as configurações para aplicar.")

    def test_remove_client_field_cancelled(self):
        self.patch_messagebox.askyesno.return_value = False
        # Store original config for comparison
        original_config_len = len(self.mock_config_manager_instance.CLIENT_FIELDS_CONFIG)

        self.app.remove_client_field(0)
        self.patch_messagebox.showinfo.assert_not_called()
        # Assert no changes to config or frames
        self.assertEqual(len(self.mock_config_manager_instance.CLIENT_FIELDS_CONFIG), original_config_len) # Config should not change
        self.mock_render_client_fields.assert_not_called() # render_client_fields should not be called
        
    def test_add_client_field(self):
        self.app.add_client_field()
        self.mock_add_field_dialog_class.assert_called_once_with(self.app, self.app.main_app_root, self.mock_render_client_fields)

if __name__ == '__main__':
    unittest.main()
