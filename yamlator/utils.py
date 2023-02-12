"""Utility functions to handle loading YAML files and Yamlator schemas"""


import yaml
import re

from typing import Any
from yamlator.types import Rule
from yamlator.exceptions import InvalidSchemaFilenameError

_YAMLER_SCHEMA_REGEX = re.compile(r'.ys$')
_BACKSLASH_REGEX = re.compile(r'[\\]{1,2}')

KEYLESS_RULE_DIRECTIVE = '!!yamlator'


def is_keyless_rule(rule: Rule) -> bool:
    """Checks if a rule has a name that matches a keyless
    rule directive. For example, given the following YAML data:

    {
        "value1": 1,
        "value2: 2,
    }

    This object does not have a parent key. In order to denote
    this in the schema block, !!yamlator directive is defined
    as the rule name. For example:

    schema {
        !!yamlator map(int)
    }

    Args:
        rule (yamlator.types.Rule): A Yamlator rule

    Returns:
        True if the name matches the `KEYLESS_RULE_DIRECTIVE`
        otherwise False

    Raises:
        ValueError: If the rule type is `None`
    """
    if rule is None:
        raise ValueError('The rule argument should not be None')
    return rule.name == KEYLESS_RULE_DIRECTIVE


def load_yaml_file(filename: str) -> Any:
    """Load a YAML file from the file system and convert it
    into a data structure Python can process

    Args:
        filename (str): The path to the YAML file

    Returns:
        The YAML file in a data structure that Python can process

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

        yamlator.exceptions.InvalidSchemaFilenameError: If the filename
            does not match a file with a `.ys` extension
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
