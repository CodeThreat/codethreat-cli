from click.testing import CliRunner
from cli.auth import auth


def test_auth():
    runner = CliRunner()
    result = runner.invoke(auth, ['--key', 'fake_token'])
    assert result.exit_code == 0
    assert 'Authenticated with token: fake_token' in result.output
