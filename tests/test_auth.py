import unittest
from unittest.mock import patch, MagicMock
import os
from click.testing import CliRunner
from cli.auth import auth, login, remove

class TestAuthCommands(unittest.TestCase):

    @patch('cli.auth.requests.get')
    def test_login(self, mock_get):
        # Mock the authentication response
        mock_get.return_value.status_code = 200

        # Retrieve secrets from environment variables
        org = os.environ.get('CODETHREAT_ORG')
        token = os.environ.get('CODETHREAT_TOKEN')
        url = os.environ.get('CODETHREAT_URL')

        runner = CliRunner()
        result = runner.invoke(login, ['--key', token, '--url', url, '--org', org])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("[CT*] Authentication successful.", result.output)

    @patch('cli.auth.requests.get')
    def test_login_failure(self, mock_get):
        # Mock the authentication failure response
        mock_get.return_value.status_code = 401

        # Retrieve secrets from environment variables
        org = os.environ.get('CODETHREAT_ORG')
        token = os.environ.get('CODETHREAT_TOKEN')
        url = os.environ.get('CODETHREAT_URL')

        runner = CliRunner()
        result = runner.invoke(login, ['--key', token, '--url', url, '--org', org])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("[CT*] Authentication failed", result.output)

    def test_remove_auth(self):
        # Mock the config file path
        with patch('cli.auth.CONFIG_FILE_PATH', new='/mock/path/to/config') as mock_config_path:
            runner = CliRunner()
            result = runner.invoke(remove)

            # Assert the output message
            self.assertIn("[CT*] No authentication configuration found.", result.output)
            self.assertEqual(result.exit_code, 0)

if __name__ == '__main__':
    unittest.main()
