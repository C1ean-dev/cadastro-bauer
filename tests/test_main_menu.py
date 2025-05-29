import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main_menu import MainMenuApp
import customtkinter as ctk

class TestMainMenuApp(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.root = ctk.CTk()
        cls.root.withdraw() # Hide the main window for testing

    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()

    def setUp(self):
        # Mock the app classes that MainMenuApp opens
        self.mock_client_registration_app = patch('main_menu.ClientRegistrationApp').start()
        self.mock_client_read_app = patch('main_menu.ClientReadApp').start()
        self.mock_client_update_app = patch('main_menu.ClientUpdateApp').start()
        self.mock_client_delete_app = patch('main_menu.ClientDeleteApp').start()

        # Mock root methods
        self.mock_root_withdraw = patch.object(self.root, 'withdraw').start()
        self.mock_root_deiconify = patch.object(self.root, 'deiconify').start()

        # Initialize MainMenuApp
        self.app = MainMenuApp(self.root)
        # Ensure create_widgets is called, as it sets up button commands
        self.app.create_widgets()

    def tearDown(self):
        patch.stopall()

    def test_open_create_client_screen(self):
        # Simulate button click
        self.app.open_create_client_screen()
        
        self.mock_root_withdraw.assert_called_once()
        self.mock_client_registration_app.assert_called_once_with(self.root)
        # Ensure protocol is set for closing
        self.mock_client_registration_app.return_value.protocol.assert_called_once()

    def test_open_read_client_screen(self):
        self.app.open_read_client_screen()
        self.mock_client_read_app.assert_called_once_with(self.root)
        self.mock_client_read_app.return_value.protocol.assert_called_once()

    def test_open_update_client_screen(self):
        self.app.open_update_client_screen()
        self.mock_client_update_app.assert_called_once_with(self.root)
        self.mock_client_update_app.return_value.protocol.assert_called_once()

    def test_open_delete_client_screen(self):
        self.app.open_delete_client_screen()
        self.mock_client_delete_app.assert_called_once_with(self.root)
        self.mock_client_delete_app.return_value.protocol.assert_called_once()

    def test_on_client_app_close(self):
        mock_client_app_instance = MagicMock()
        self.app.on_client_app_close(mock_client_app_instance)
        mock_client_app_instance.destroy.assert_called_once()
        self.mock_root_deiconify.assert_called_once()

if __name__ == '__main__':
    unittest.main()
