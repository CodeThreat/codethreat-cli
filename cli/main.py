import click
from cli.auth import auth
from cli.scan import scan


@click.group()
def main():
    """CodeThreat CLI - A toolset for SAST."""
    pass


main.add_command(auth)
main.add_command(scan)

if __name__ == '__main__':
    main()
