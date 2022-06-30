"""Utility functions to handle loading YAML files and Yamlator schemas"""


import yaml
import re

from yamlator.exceptions import InvalidSchemaFilenameError

_YAMLER_SCHEMA_REGEX = re.compile(r'.ys$')
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

    with open(filename, 'r', encoding='utf-8') as f:
        return yaml.load(f, Loader=yaml.Loader)


def load_schema(filename: str) -> str:
    """Load the contents of a schema file

    Args:
        filename (str): The path to the schema file

    Returns:
        The content of the file as a string

    Raises:
        ValueError: If `filename` is None or an empty string
        InvalidSchemaFilenameError: If the filename does not match
        a file with a `.ys` extension
    """
    if filename is None:
        raise ValueError('filename cannot be None')

    if len(filename) == 0:
        raise ValueError('filename cannot be an empty string')

    if not _YAMLER_SCHEMA_REGEX.search(filename):
        raise InvalidSchemaFilenameError(filename)

    filename = _BACKSLASH_REGEX.sub('/', filename)

    with open(filename, 'r', encoding='utf-8') as f:
        return f.read()
