from click.testing import CliRunner
from cli.scan import scan


def test_scan():
    runner = CliRunner()
    result = runner.invoke(scan, ['--target', '/path/to/code', '--project', 'example_project'])
    assert result.exit_code == 0
    assert 'Scanning target: /path/to/code in project: example_project' in result.output
