import unittest
from unittest.mock import patch, mock_open
import os
from click.testing import CliRunner
from cli import auth


class TestAuthCommands(unittest.TestCase):

    @patch('auth.requests.get')
    @patch('builtins.open', new_callable=mock_open)
    def test_login(self, mock_open_file, mock_requests_get):
        # Mocking the requests
        mock_requests_get.return_value.status_code = 200

        # Retrieve secrets from environment variables
        org = os.environ.get('CODETHREAT_ORG')
        token = os.environ.get('CODETHREAT_TOKEN')
        url = os.environ.get('CODETHREAT_URL')

        runner = CliRunner()
        result = runner.invoke(auth.login, ['--key', token, '--url', url, '--org', org])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("[CT*] Authentication successful.", result.output)
        mock_open_file.assert_called_once_with(auth.CONFIG_FILE_PATH, "w")

    @patch('auth.requests.get')
    def test_login_failure(self, mock_requests_get):
        # Mocking a failed login attempt
        mock_requests_get.return_value.status_code = 401

        org = os.environ.get('CODETHREAT_ORG')
        token = os.environ.get('CODETHREAT_TOKEN')
        url = os.environ.get('CODETHREAT_URL')

        runner = CliRunner()
        result = runner.invoke(auth.login, ['--key', token, '--url', url, '--org', org])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("[CT*] Authentication failed:", result.output)

    @patch('os.remove')
    def test_remove_auth_config(self, mock_os_remove):
        runner = CliRunner()

        with patch('os.path.exists', return_value=True):
            result = runner.invoke(auth.remove)

        self.assertEqual(result.exit_code, 0)
        self.assertIn("[CT*] Authentication configuration removed successfully.", result.output)
        mock_os_remove.assert_called_once_with(auth.CONFIG_FILE_PATH)

    @patch('os.path.exists', return_value=False)
    def test_remove_auth_config_not_found(self, mock_os_path_exists):
        runner = CliRunner()
        result = runner.invoke(auth.remove)

        self.assertEqual(result.exit_code, 0)
        self.assertIn("[CT*] No authentication configuration found.", result.output)


if __name__ == '__main__':
    unittest.main()
