import click
from cli.auth import auth
from cli.scan import scan

# Define version information here
VERSION = "0.2.1"


# Custom help display with an enhanced ASCII art banner
@click.group(
    invoke_without_command=True,
    help="""
CodeThreat CLI - A Comprehensive Scanner Integration in your local environment!
    """,
    context_settings=dict(help_option_names=['-h', '--help']),
)
@click.version_option(VERSION, '-v', '--version', message="CodeThreat CLI Version: %(version)s")
@click.pass_context
def main(ctx):
    """CodeThreat CLI - A Toolset for SAST (Static Application Security Testing)."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())  # Show help if no command is invoked


# Registering commands
main.add_command(auth)
main.add_command(scan)

if __name__ == '__main__':
    main()
