import click
import requests
import os
from colorama import Fore, Style, init
from .utils import get_config_value, CONFIG_FILE_PATH

# Initialize colorama
init(autoreset=True)

@click.group()
def auth():
    """Authentication commands for CodeThreat CLI."""
    pass

@click.command()
@click.option('--key', prompt=False, hide_input=True, confirmation_prompt=True,
              default=lambda: get_config_value("CODETHREAT_SECRET"),
              help='Personal Access Token for authentication')
@click.option('--url', prompt=False,
              default=lambda: get_config_value("CODETHREAT_APP_URL"),
              help='CodeThreat application URL')
@click.option('--org', prompt=False,
              default=lambda: get_config_value("CODETHREAT_ORG"),
              help='Organization name')
def login(key, url, org):
    """Authenticate with your Personal Access Token."""

    if not key:
        key = click.prompt(f"{Fore.CYAN}[CT*] Personal Access Token{Style.RESET_ALL}", hide_input=True, confirmation_prompt=True)

    if not url:
        url = click.prompt(f"{Fore.CYAN}[CT*] CodeThreat application URL{Style.RESET_ALL}")

    if not org:
        org = click.prompt(f"{Fore.CYAN}[CT*] Organization Name{Style.RESET_ALL}")

    headers = {
        "Authorization": f"Bearer {key}",
        "User-Agent": "CodeThreat-CLI",
        "x-ct-organization": org
    }

    click.echo(f"{Fore.CYAN}[CT*] Authenticating...{Style.RESET_ALL}")

    # Validate authentication by making a request
    validate_url = f"{url}/api/organization?key={org}"
    response = requests.get(validate_url, headers=headers)

    if response.status_code == 200:
        click.echo(f"{Fore.GREEN}[CT*] Authentication successful.{Style.RESET_ALL}")

        # Save to config file if not already in env
        with open(CONFIG_FILE_PATH, "w") as config_file:
            config_file.write(f"CODETHREAT_SECRET={key}\n")
            config_file.write(f"CODETHREAT_APP_URL={url}\n")
            config_file.write(f"CODETHREAT_ORG={org}\n")
    else:
        click.echo(f"{Fore.RED}[CT*] Authentication failed: {response.status_code} - {response.text}{Style.RESET_ALL}")

@click.command()
def remove():
    """Remove the existing authentication configuration."""
    if os.path.exists(CONFIG_FILE_PATH):
        os.remove(CONFIG_FILE_PATH)
        click.echo(f"{Fore.YELLOW}[CT*] Authentication configuration removed successfully.{Style.RESET_ALL}")
    else:
        click.echo(f"{Fore.RED}[CT*] No authentication configuration found.{Style.RESET_ALL}")

# Add commands to the auth group
auth.add_command(login)
auth.add_command(remove)

if __name__ == "__main__":
    auth()
