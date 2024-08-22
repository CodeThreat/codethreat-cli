import click


@click.command()
@click.option('--key', prompt=True, hide_input=True, confirmation_prompt=True,
              help='Personal Access Token for authentication')
def auth(key):
    """Authenticate with your Personal Access Token."""
    click.echo(f'Authenticated with token: {key}')
    # Logic to store the token securely
