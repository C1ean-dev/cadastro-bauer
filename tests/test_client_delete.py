import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from delete.client_delete_app import ClientDeleteApp
import customtkinter as ctk

class TestClientDeleteApp(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.root = ctk.CTk()
        cls.root.withdraw()

    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()

    def setUp(self):
        # Patch messagebox where it is imported/used in delete.client_delete_app
        self.mock_messagebox = patch('delete.client_delete_app.messagebox').start()
        # Mock the super().__init__ to avoid full GUI initialization
        self.mock_super_init = patch('delete.client_delete_gui.ClientDeleteGUI.__init__', MagicMock(return_value=None)).start()
        # Mock setup_gui_elements as it's called in __init__ and deals with GUI
        self.mock_setup_gui_elements = patch('delete.client_delete_gui.ClientDeleteGUI.setup_gui_elements').start()

        self.app = ClientDeleteApp(self.root)
        # Manually set entry_widgets as setup_gui_elements is mocked
        self.app.entry_widgets = {
            "identifier": MagicMock(get=MagicMock(return_value="12345"), delete=MagicMock())
        }

    def tearDown(self):
        patch.stopall()

    @patch('delete.client_delete_app.delete_client_data') # Patch where it's used
    def test_handle_delete_client_success(self, mock_delete_client_data):
        mock_delete_client_data.return_value = True
        self.app.handle_delete_client() # Call the method directly
        mock_delete_client_data.assert_called_once_with("12345")
        self.mock_messagebox.showinfo.assert_called_once_with("Success", "Client deleted successfully!")
        self.app.entry_widgets["identifier"].delete.assert_called_once_with(0, ctk.END)

    @patch('delete.client_delete_app.delete_client_data') # Patch where it's used
    def test_handle_delete_client_failure(self, mock_delete_client_data):
        mock_delete_client_data.return_value = False
        self.app.handle_delete_client() # Call the method directly
        mock_delete_client_data.assert_called_once_with("12345")
        self.mock_messagebox.showerror.assert_called_once_with("Error", "Failed to delete client. Client not found or an error occurred.")
        self.app.entry_widgets["identifier"].delete.assert_not_called()

    @patch('delete.client_delete_app.delete_client_data') # Patch here to ensure it's not called
    def test_handle_delete_client_empty_identifier(self, mock_delete_client_data):
        self.app.entry_widgets["identifier"].get.return_value = ""
        self.app.handle_delete_client() # Call the method directly
        self.mock_messagebox.showerror.assert_called_once_with("Input Error", "Please enter XCLIENTES, CGC, Name, or Inscrição to delete.")
        mock_delete_client_data.assert_not_called() # Assert it was not called

if __name__ == '__main__':
    unittest.main()
