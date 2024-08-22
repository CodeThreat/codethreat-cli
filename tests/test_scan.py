import tempfile
import unittest
from unittest.mock import patch, MagicMock
import os
from click.testing import CliRunner
from cli import scan

class TestScanCommand(unittest.TestCase):

    @patch('scan.requests.get')
    @patch('scan.requests.post')
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
        result = runner.invoke(scan.scan, ['--target', source_code_path, '--project', 'new_project', '--url', url, '--token', token, '--org', org])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("[CT*] Scan started successfully", result.output)
        mock_make_archive.assert_called_once()
        mock_post.assert_called()

    @patch('scan.requests.get')
    @patch('scan.requests.post')
    def test_scan_project_creation(self, mock_post, mock_get):
        # Mocking project creation and scan initiation
        mock_get.return_value.status_code = 404
        mock_post.side_effect = [
            MagicMock(status_code=200, json=MagicMock(return_value={"result": {"message": "successfull"}, "error": False})),
            MagicMock(status_code=200, json=MagicMock(return_value={"scan_id": "fake_scan_id"}))
        ]

        # Retrieve secrets from environment variables
        org = os.environ.get('CODETHREAT_ORG')
        token = os.environ.get('CODETHREAT_TOKEN')
        url = os.environ.get('CODETHREAT_URL')

        # Use the actual source code directory for testing
        source_code_path = os.path.abspath(os.path.dirname(__file__))

        runner = CliRunner()
        result = runner.invoke(scan.scan, ['--target', source_code_path, '--project', 'new_project', '--url', url, '--token', token, '--org', org])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("[CT*] Project 'new_project' created successfully.", result.output)
        self.assertIn("[CT*] Scan started successfully", result.output)
        mock_post.assert_called()

    @patch('scan.requests.get')
    @patch('scan.requests.post')
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
        result = runner.invoke(scan.scan, ['--target', source_code_path, '--project', 'test_project_123', '--url', url, '--token', token, '--org', org])

        self.assertEqual(result.exit_code, scan.FAILURE_EXIT_CODE)
        self.assertIn("[CT*] Scan initiation failed", result.output)

if __name__ == '__main__':
    unittest.main()
