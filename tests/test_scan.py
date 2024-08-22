import tempfile
import unittest
from unittest.mock import patch, MagicMock
import os
import random
import string
from click.testing import CliRunner
from cli.scan import scan, FAILURE_EXIT_CODE, SUCCESS_EXIT_CODE


def generate_random_project_name(prefix="test_project_", length=6):
    """Generates a random project name."""
    return prefix + ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))


class TestScanCommand(unittest.TestCase):

    @patch('cli.scan.requests.get')
    @patch('cli.scan.requests.post')
    @patch('shutil.make_archive')
    @patch('tempfile.TemporaryDirectory')
    def test_scan(self, mock_tempdir, mock_make_archive, mock_post, mock_get):
        # Mocking environment variables and requests
        mock_tempdir.return_value.__enter__.return_value = tempfile.gettempdir()
        mock_make_archive.return_value = os.path.join(tempfile.gettempdir(), 'test.zip')
        mock_get.return_value.status_code = 200
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"scan_id": "fake_scan_id"}

        # Retrieve secrets from environment variables
        org = os.environ.get('CODETHREAT_ORG')
        token = os.environ.get('CODETHREAT_TOKEN')
        url = os.environ.get('CODETHREAT_URL')

        # Use the actual source code directory for testing
        source_code_path = os.path.abspath(os.path.dirname(__file__))

        runner = CliRunner()
        result = runner.invoke(scan, ['--target', source_code_path, '--project', generate_random_project_name(),
                                      '--url', url, '--token', token, '--org', org])

        print(result.output)  # For debugging purposes
        print(mock_post.return_value.json.return_value)  # For debugging the mock's json response
        self.assertEqual(result.exit_code, SUCCESS_EXIT_CODE)
        self.assertIn("[CT*] Scan started successfully", result.output)
        mock_make_archive.assert_called_once()
        mock_post.assert_called()

    @patch('cli.scan.requests.get')
    @patch('cli.scan.requests.post')
    def test_scan_project_creation(self, mock_post, mock_get):
        # Mocking project creation and scan initiation
        mock_get.return_value.status_code = 404
        mock_post.side_effect = [
            MagicMock(status_code=200,
                      json=MagicMock(return_value={"result": {"message": "successfull"}, "error": False})),
            MagicMock(status_code=200, json=MagicMock(return_value={"scan_id": "fake_scan_id"}))
        ]

        # Retrieve secrets from environment variables
        org = os.environ.get('CODETHREAT_ORG')
        token = os.environ.get('CODETHREAT_TOKEN')
        url = os.environ.get('CODETHREAT_URL')

        # Use the actual source code directory for testing
        source_code_path = os.path.abspath(os.path.dirname(__file__))

        runner = CliRunner()
        result = runner.invoke(scan, ['--target', source_code_path, '--project', generate_random_project_name(),
                                      '--url', url, '--token', token, '--org', org])

        print(result.output)  # For debugging purposes
        print(mock_post.return_value.json.return_value)  # For debugging the mock's json response
        self.assertEqual(result.exit_code, SUCCESS_EXIT_CODE)
        self.assertIn("[CT*] Project 'new_project' created successfully.", result.output)
        self.assertIn("[CT*] Scan started successfully", result.output)
        mock_post.assert_called()

    @patch('cli.scan.requests.get')
    @patch('cli.scan.requests.post')
    def test_scan_failure(self, mock_post, mock_get):
        # Mocking a failed scan initiation
        mock_get.return_value.status_code = 200
        mock_post.return_value.status_code = 500

        # Retrieve secrets from environment variables
        org = os.environ.get('CODETHREAT_ORG')
        token = os.environ.get('CODETHREAT_TOKEN')
        url = os.environ.get('CODETHREAT_URL')

        # Use the actual source code directory for testing
        source_code_path = os.path.abspath(os.path.dirname(__file__))

        runner = CliRunner()
        result = runner.invoke(scan,
                               ['--target', source_code_path, '--project', generate_random_project_name(),
                                '--url', url, '--token', token, '--org', org])

        print(result.output)  # For debugging purposes
        self.assertEqual(result.exit_code, FAILURE_EXIT_CODE)
        self.assertIn("[CT*] Scan initiation failed", result.output)


if __name__ == '__main__':
    unittest.main()
