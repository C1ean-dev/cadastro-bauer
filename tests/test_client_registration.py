import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the parent directory to the Python path to allow imports from the main application
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from cadastro.client_registration_app import ClientRegistrationApp
import customtkinter as ctk

class TestClientRegistrationApp(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Initialize a dummy CTk root for the Toplevel window
        cls.root = ctk.CTk()
        cls.root.withdraw() # Hide the main window

    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()

    def setUp(self):
        # Patch messagebox where it is imported/used in cadastro.client_registration_app
        self.mock_messagebox = patch('cadastro.client_registration_app.messagebox').start()
        # Mock the super().__init__ to avoid full GUI initialization
        self.mock_super_init = patch('cadastro.client_registration_gui.ClientRegistrationGUI.__init__', MagicMock(return_value=None)).start()
        # Mock setup_gui_elements as it's called in __init__ and deals with GUI
        self.mock_setup_gui_elements = patch('cadastro.client_registration_gui.ClientRegistrationGUI.setup_gui_elements').start()
        # Mock clear_form_fields as it's called after successful registration (now in GUI class)
        self.mock_clear_form_fields = patch('cadastro.client_registration_gui.ClientRegistrationGUI.clear_form_fields').start()

        self.app = ClientRegistrationApp(self.root)
        
        # Manually set attributes that are normally set by ClientRegistrationGUI.__init__
        # and setup_gui_elements, but are needed for the business logic tests.
        self.app.entry_widgets = {
            "Nome": MagicMock(get=lambda: "Test Client"),
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

    def tearDown(self):
        patch.stopall()

    @patch('cadastro.client_registration_app.connect_to_database') # Patch where it's used
    @patch('cadastro.client_registration_app.insert_client_data') # Patch where it's used
    @patch('cadastro.client_registration_app.validate_fields') # Patch where it's used
    @patch('cadastro.client_registration_app.INTERNAL_DEFAULT_FIELDS', {"XCLIENTES": "000001", "FILIAL": "01"})
    def test_handle_insert_client_success(self, mock_validate_fields, mock_insert_client_data, mock_connect_to_database):
        mock_validate_fields.return_value = [] # No validation errors
        mock_insert_client_data.return_value = True # Successful insertion
        
        # Mock get_next_xclientes to return a predictable value
        with patch.object(self.app, 'get_next_xclientes', return_value="000002"):
            self.app.handle_insert_client() # Call the method directly

            mock_validate_fields.assert_called_once()
            mock_insert_client_data.assert_called_once()
            self.mock_messagebox.showinfo.assert_called_once_with("sucesso", "cliente registrado com sucesso!")
            self.mock_clear_form_fields.assert_called_once()

    @patch('cadastro.client_registration_app.connect_to_database') # Patch where it's used
    @patch('cadastro.client_registration_app.insert_client_data') # Patch where it's used
    @patch('cadastro.client_registration_app.validate_fields') # Patch where it's used
    @patch('cadastro.client_registration_app.INTERNAL_DEFAULT_FIELDS', {"XCLIENTES": "000001", "FILIAL": "01"})
    def test_handle_insert_client_validation_error(self, mock_validate_fields, mock_insert_client_data, mock_connect_to_database):
        mock_validate_fields.return_value = ["Name is required."] # Validation errors
        mock_insert_client_data.return_value = False # Should not be called

        self.app.handle_insert_client() # Call the method directly

        mock_validate_fields.assert_called_once()
        mock_insert_client_data.assert_not_called()
        self.mock_messagebox.showerror.assert_called_once_with("Validation Error", "Name is required.")
        self.mock_clear_form_fields.assert_not_called()

    @patch('cadastro.client_registration_app.connect_to_database') # Patch where it's used
    @patch('cadastro.client_registration_app.insert_client_data') # Patch where it's used
    @patch('cadastro.client_registration_app.validate_fields') # Patch where it's used
    @patch('cadastro.client_registration_app.INTERNAL_DEFAULT_FIELDS', {"XCLIENTES": "000001", "FILIAL": "01"})
    def test_handle_insert_client_db_error(self, mock_validate_fields, mock_insert_client_data, mock_connect_to_database):
        mock_validate_fields.return_value = []
        mock_insert_client_data.return_value = False # Database insertion failed

        with patch.object(self.app, 'get_next_xclientes', return_value="000002"):
            self.app.handle_insert_client() # Call the method directly

            mock_validate_fields.assert_called_once()
            mock_insert_client_data.assert_called_once()
            self.mock_messagebox.showerror.assert_called_once_with("Erro", "não foi possivel enviar.")
            self.mock_clear_form_fields.assert_not_called()

    @patch('cadastro.client_registration_app.connect_to_database') # Patch where it's used
    def test_get_next_xclientes_success(self, mock_connect_to_database):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_to_database.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (123,) # Simulate existing max XCLIENTES

        result = self.app.get_next_xclientes()
        self.assertEqual(result, "124")
        mock_cursor.execute.assert_called_once_with("SELECT MAX(CAST(XCLIENTES AS INT)) FROM SM11_PROD.dbo.FBCLIENTES")
        mock_conn.close.assert_called_once()

    @patch('cadastro.client_registration_app.connect_to_database') # Patch where it's used
    def test_get_next_xclientes_no_existing_data(self, mock_connect_to_database):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_to_database.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (None,) # Simulate no existing max XCLIENTES

        result = self.app.get_next_xclientes()
        self.assertEqual(result, "1")
        mock_conn.close.assert_called_once()

    @patch('cadastro.client_registration_app.connect_to_database', return_value=None) # Patch where it's used
    def test_get_next_xclientes_db_connection_fail(self, mock_connect_to_database):
        result = self.app.get_next_xclientes()
        self.assertIsNone(result)
        # The error message is handled by the caller, not this method directly
        self.mock_messagebox.showerror.assert_not_called() 

    @patch('cadastro.client_registration_app.connect_to_database') # Patch where it's used
    def test_get_next_xclientes_db_query_error(self, mock_connect_to_database):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_to_database.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("DB Query Error")

        result = self.app.get_next_xclientes()
        self.assertIsNone(result)
        self.mock_messagebox.showerror.assert_called_once_with("Database Error", "Error fetching next XCLIENTES: DB Query Error")
        mock_conn.close.assert_called_once()

if __name__ == '__main__':
    unittest.main()
