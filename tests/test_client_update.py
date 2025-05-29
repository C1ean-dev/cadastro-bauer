import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from update.client_update_app import ClientUpdateApp
import customtkinter as ctk
from utils.config_manager import CLIENT_FIELDS_CONFIG

class TestClientUpdateApp(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.root = ctk.CTk()
        cls.root.withdraw()

    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()

    def setUp(self):
        # Patch messagebox where it is imported/used in update.client_update_app
        self.mock_messagebox = patch('update.client_update_app.messagebox').start()
        # Mock the super().__init__ to avoid full GUI initialization
        self.mock_super_init = patch('update.client_update_gui.ClientUpdateGUI.__init__', MagicMock(return_value=None)).start()
        # Mock setup_gui_elements as it's called in __init__ and deals with GUI
        self.mock_setup_gui_elements = patch('update.client_update_gui.ClientUpdateGUI.setup_gui_elements').start()
        # Mock GUI methods that are called by the business logic
        self.mock_populate_form_fields = patch('update.client_update_gui.ClientUpdateGUI.populate_form_fields').start()
        self.mock_clear_form_fields = patch('update.client_update_gui.ClientUpdateGUI.clear_form_fields').start()

        self.app = ClientUpdateApp(self.root)
        # Manually set attributes as setup_gui_elements is mocked
        self.app.search_entry = MagicMock(get=MagicMock(return_value="12345"))
        self.app.entry_widgets = {
            "Nome": MagicMock(get=lambda: "Updated Name"),
            "CGC": MagicMock(get=lambda: "12345678901234"),
            "CEP": MagicMock(get=lambda: "12345-678"),
            "Endereco": MagicMock(get=lambda: "Rua Teste"),
            "Numero": MagicMock(get=lambda: "123"),
            "Bairro": MagicMock(get=lambda: "Bairro Teste"),
            "Cidade": MagicMock(get=lambda: "Cidade Teste"),
            "Estado": MagicMock(get=lambda: "TS"),
            "Telefone": MagicMock(get=lambda: "99999999999"),
            "Email": MagicMock(get=lambda: "test@example.com")
        }
        self.app.VALIDATION_RULES = {
            "Nome": (50, True),
            "CGC": (14, True),
            "CEP": (9, True),
            "Endereco": (100, True),
            "Numero": (10, True),
            "Bairro": (50, True),
            "Cidade": (50, True),
            "Estado": (2, True),
            "Telefone": (11, False),
            "Email": (50, False)
        }
        self.app.FIELDS = list(self.app.entry_widgets.keys()) # Ensure FIELDS is populated
        self.app.current_xclientes = None # Initialize as it's used in handle_update_client

    def tearDown(self):
        patch.stopall()

    @patch('update.client_update_app.get_client_data') # Patch where it's used
    def test_search_client_found(self, mock_get_client_data):
        mock_client_data = {"NOME": "Old Name", "CGC": "12345678901234", "XCLIENTES": "000001"}
        mock_get_client_data.return_value = mock_client_data
        
        self.app.search_client() # Call the method directly
        
        mock_get_client_data.assert_called_once_with("12345")
        self.mock_populate_form_fields.assert_called_once_with(mock_client_data)
        self.assertEqual(self.app.current_xclientes, "000001")
        self.mock_messagebox.showwarning.assert_not_called()
        self.mock_clear_form_fields.assert_not_called()

    @patch('update.client_update_app.get_client_data') # Patch where it's used
    def test_search_client_not_found(self, mock_get_client_data):
        mock_get_client_data.return_value = None
        
        self.app.search_client() # Call the method directly
        
        mock_get_client_data.assert_called_once_with("12345")
        self.mock_populate_form_fields.assert_not_called()
        self.assertIsNone(self.app.current_xclientes)
        self.mock_messagebox.showwarning.assert_called_once_with("Not Found", "Client not found.")
        self.mock_clear_form_fields.assert_called_once()

    @patch('update.client_update_app.get_client_data') # Patch here to ensure it's not called
    def test_search_client_empty_identifier(self, mock_get_client_data):
        self.app.search_entry.get.return_value = ""
        
        self.app.search_client() # Call the method directly
        
        self.mock_messagebox.showerror.assert_called_once_with("Input Error", "Please enter XCLIENTES, CGC, Name, or Inscrição to search.")
        mock_get_client_data.assert_not_called()
        self.mock_populate_form_fields.assert_not_called()
        self.mock_clear_form_fields.assert_not_called()

    @patch('update.client_update_app.update_client_data') # Patch where it's used
    @patch('update.client_update_app.validate_fields') # Patch where it's used
    def test_handle_update_client_success(self, mock_validate_fields, mock_update_client_data):
        self.app.current_xclientes = "000001" # Simulate client loaded
        mock_validate_fields.return_value = []
        mock_update_client_data.return_value = True

        self.app.handle_update_client() # Call the method directly

        mock_validate_fields.assert_called_once()
        mock_update_client_data.assert_called_once()
        self.mock_messagebox.showinfo.assert_called_once_with("Success", "Client updated successfully!")

    @patch('update.client_update_app.update_client_data') # Patch where it's used
    @patch('update.client_update_app.validate_fields') # Patch where it's used
    def test_handle_update_client_no_client_loaded(self, mock_validate_fields, mock_update_client_data):
        self.app.current_xclientes = None # No client loaded
        self.app.handle_update_client() # Call the method directly
        self.mock_messagebox.showerror.assert_called_once_with("Error", "No client loaded for update. Please search for a client first.")
        mock_validate_fields.assert_not_called()
        mock_update_client_data.assert_not_called()

    @patch('update.client_update_app.update_client_data') # Patch where it's used
    @patch('update.client_update_app.validate_fields') # Patch where it's used
    def test_handle_update_client_validation_error(self, mock_validate_fields, mock_update_client_data):
        self.app.current_xclientes = "000001"
        mock_validate_fields.return_value = ["Name is required."]
        self.app.handle_update_client() # Call the method directly
        mock_validate_fields.assert_called_once()
        mock_update_client_data.assert_not_called()
        self.mock_messagebox.showerror.assert_called_once_with("Validation Error", "Name is required.")

    @patch('update.client_update_app.update_client_data') # Patch where it's used
    @patch('update.client_update_app.validate_fields') # Patch where it's used
    def test_handle_update_client_db_error(self, mock_validate_fields, mock_update_client_data):
        self.app.current_xclientes = "000001"
        mock_validate_fields.return_value = []
        mock_update_client_data.return_value = False
        self.app.handle_update_client() # Call the method directly
        mock_validate_fields.assert_called_once()
        mock_update_client_data.assert_called_once()
        self.mock_messagebox.showerror.assert_called_once_with("Error", "Failed to update client.")

if __name__ == '__main__':
    unittest.main()
