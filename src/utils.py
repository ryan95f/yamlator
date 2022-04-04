import yaml
import re

from src.exceptions import InvalidSchemaFilenameError

_YAMLER_SCHEMA_REGEX = re.compile(r'^[.\/\\]?[a-zA-Z0-9_\-\/\\]+.yamler')
_BACKSLASH_REGEX = re.compile(r'[\\]{1,2}')


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
        raise ValueError('filename cannot be None')

    if len(filename) == 0:
        raise ValueError('filename cannot be an empty string')

    with open(filename, 'r') as f:
        return yaml.load(f, Loader=yaml.Loader)


def load_yamler_ruleset(filename: str) -> str:
    """Load the contents of a Yamler file as a string

    Args:
        filename (str): The path to the Yamler file

    Returns:
        The content of the file as a string

    Raises:
        ValueError: If `filename` is None or an empty string
        InvalidYamlerFilenameError: If the filename does not match
        a file with a `.yamler` extention
    """
    if filename is None:
        raise ValueError('filename cannot be None')

    if len(filename) == 0:
        raise ValueError('filename cannot be an empty string')

    if not _YAMLER_SCHEMA_REGEX.match(filename):
        raise InvalidSchemaFilenameError(filename)

    filename = _BACKSLASH_REGEX.sub('/', filename)

    with open(filename) as f:
        return f.read()
