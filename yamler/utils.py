import yaml
import re

_YAMLER_SCHEMA_REGEX = re.compile(r'^[a-zA-Z0-9_-]+\.yamler$')


def load_yaml_file(filename: str) -> dict:
    """Load a YAML file from a the file system and
    convert it into a dict

    Args:
        filename (str): The path to the YAML file

    Returns:
        The YAML file contents as a dict

    Raises:
        ValueError: If the filename parameter is None or an empty string
        FileNotFoundError: If the file specified in filename does not exist
    """
    if filename is None:
        raise ValueError("filename cannot be None")

    if len(filename) == 0:
        raise ValueError("filename cannot be an empty string")

    with open(filename, 'r') as f:
        return yaml.load(f, Loader=yaml.Loader)


def load_yamler_ruleset(filename: str) -> str:
    """Load the contents of a Yamler file as a string

    Args:
        filename (str): The path to the Yamler file

    Returns:
        The content of the file as a string
    """
    if filename is None:
        raise ValueError("filename cannot be None")

    if len(filename) == 0:
        raise ValueError("filename cannot be an empty string")

    if not _YAMLER_SCHEMA_REGEX.match(filename):
        # TODO raise a custom exception
        pass

    with open(filename) as f:
        return f.read()
