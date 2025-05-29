import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from read.client_read_app import ClientReadApp
import customtkinter as ctk
from utils.config_manager import CLIENT_FIELDS_CONFIG

class TestClientReadApp(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.root = ctk.CTk()
        cls.root.withdraw()

    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()

    def setUp(self):
        # Patch messagebox where it is imported/used in read.client_read_app
        self.mock_messagebox = patch('read.client_read_app.messagebox').start()
        # Mock the super().__init__ to avoid full GUI initialization
        self.mock_super_init = patch('read.client_read_gui.ClientReadGUI.__init__', MagicMock(return_value=None)).start()
        # Mock setup_gui_elements as it's called in __init__ and deals with GUI
        self.mock_setup_gui_elements = patch('read.client_read_gui.ClientReadGUI.setup_gui_elements').start()
        # Mock GUI methods that are called by the business logic
        self.mock_populate_display_fields = patch('read.client_read_gui.ClientReadGUI.populate_display_fields').start()
        self.mock_clear_display_fields = patch('read.client_read_gui.ClientReadGUI.clear_display_fields').start()

        self.app = ClientReadApp(self.root)
        # Manually set search_entry as setup_gui_elements is mocked
        self.app.search_entry = MagicMock(get=MagicMock(return_value="12345"))
        # Manually set display_widgets and FIELDS as setup_gui_elements is mocked
        self.app.display_widgets = {
            "Nome": MagicMock(), "CGC": MagicMock(), "XCLIENTES": MagicMock()
        }
        self.app.FIELDS = [field["name"] for field in CLIENT_FIELDS_CONFIG]


    def tearDown(self):
        patch.stopall()

    @patch('read.client_read_app.get_client_data') # Patch where it's used
    def test_search_client_found(self, mock_get_client_data):
        mock_client_data = {"NOME": "Test Client", "CGC": "12345678901234", "XCLIENTES": "000001"}
        mock_get_client_data.return_value = mock_client_data
        
        self.app.search_client() # Call the method directly
        
        mock_get_client_data.assert_called_once_with("12345")
        self.mock_populate_display_fields.assert_called_once_with(mock_client_data)
        self.mock_messagebox.showwarning.assert_not_called()
        self.mock_clear_display_fields.assert_not_called()

    @patch('read.client_read_app.get_client_data') # Patch where it's used
    def test_search_client_not_found(self, mock_get_client_data):
        mock_get_client_data.return_value = None
        
        self.app.search_client() # Call the method directly
        
        mock_get_client_data.assert_called_once_with("12345")
        self.mock_populate_display_fields.assert_not_called()
        self.mock_messagebox.showwarning.assert_called_once_with("Not Found", "Client not found.")
        self.mock_clear_display_fields.assert_called_once()

    @patch('read.client_read_app.get_client_data') # Patch here to ensure it's not called
    def test_search_client_empty_identifier(self, mock_get_client_data):
        self.app.search_entry.get.return_value = ""
        
        self.app.search_client() # Call the method directly
        
        self.mock_messagebox.showerror.assert_called_once_with("Input Error", "Please enter NRECNO or CGC to search.")
        mock_get_client_data.assert_not_called() # Assert it was not called
        self.mock_populate_display_fields.assert_not_called()
        self.mock_clear_display_fields.assert_not_called()

if __name__ == '__main__':
    unittest.main()
