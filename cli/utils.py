import os

CONFIG_FILE_PATH = os.path.expanduser("~/.codethreat_cli_config")


def get_config_value(key):
    """Fetch configuration value from environment variable or config file."""
    # First, try to get the value from environment variables
    value = os.getenv(key)
    if value:
        return value

    # If not in environment variables, try to get it from the config file
    if os.path.exists(CONFIG_FILE_PATH):
        with open(CONFIG_FILE_PATH, "r") as config_file:
            for line in config_file:
                if line.startswith(key):
                    return line.split("=", 1)[1].strip()

    # If the key is not found in either, return None
    return None
