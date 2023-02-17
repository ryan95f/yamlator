"""Handles the command line utility functions and entry point"""
import os
import enum
import argparse

from typing import Iterator

from yamlator.utils import load_yaml_file
from yamlator.utils import load_schema
from yamlator.parser import SchemaSyntaxError
from yamlator.parser import parse_schema
from yamlator.validators.core import validate_yaml

from yamlator.exceptions import SchemaParseError
from yamlator.exceptions import InvalidSchemaFilenameError
from yamlator.violations import Violation

from yamlator.cmd.outputs import SuccessCode
from yamlator.cmd.outputs import JSONOutput
from yamlator.cmd.outputs import TableOutput
from yamlator.cmd.outputs import YAMLOutput


def main() -> int:
    """Entry point into the Yamlator CLI

    Returns:
        A status code where 0 = success and -1 = error
    """
    parser = _create_args_parser()
    args = parser.parse_args()
    violations = []

    try:
        violations = validate_yaml_data_from_file(
            yaml_filepath=args.file,
            schema_filepath=args.ruleset_schema
        )
    except SchemaParseError as ex:
        print(f'Error when parsing schema: {ex}')
        return SuccessCode.ERR
    except SchemaSyntaxError as ex:
        print(ex)
        return SuccessCode.ERR
    except InvalidSchemaFilenameError as ex:
        print(ex)
        return SuccessCode.ERR
    except FileNotFoundError as ex:
        print(ex)
        return SuccessCode.ERR
    except ValueError as ex:
        print(ex)
        return SuccessCode.ERR

    display_method = DisplayMethod[args.output.upper()]
    return display_violations(violations, display_method)


def _create_args_parser():
    description = 'Yamlator is a CLI tool that allows a YAML file to be \
                  validated using a lightweight schema language'

    parser = argparse.ArgumentParser(prog='yamlator', description=description)
    parser.add_argument('file', type=str,
                        help='The YAML file to be validated')

    parser.add_argument('-s', '--schema', type=str, required=True,
                        dest='ruleset_schema',
                        help='The schama that will be used to \
                        validate the YAML file')

    parser.add_argument('-o', '--output', type=str, required=False,
                        default='table', choices=['table', 'json', 'yaml'],
                        help='Defines the format that will be displayed \
                        for the violations')
    return parser


def validate_yaml_data_from_file(yaml_filepath: str,
                                 schema_filepath: str) -> Iterator[Violation]:
    """Validate a YAML file with a schema file

    Args:
        yaml_filepath   (str): The path to the YAML data file
        schema_filepath (str): The path to the schema file

    Returns:
        A Iterator collection of `yamlator.violations.Violation` objects
        that contains the violations detected in the YAML data against
        the schema

    Raises:
        ValueError: If either argument is `None` or an empty string
        FileNotFoundError: If either argument cannot be found on the file system
        InvalidSchemaFilenameError: If `schema_filepath` does not have
        a valid filename that ends with the `.ys` extension.
    """
    yaml_data = load_yaml_file(yaml_filepath)
    schema_data = load_schema(schema_filepath)

    context = load_schema_path_context(schema_filepath)

    instructions = parse_schema(schema_data)
    load_child_resources(instructions, context)
    # return validate_yaml(yaml_data, instructions)
    return []


class DisplayMethod(enum.Enum):
    """Represents the supported violation display methods"""
    TABLE = 'table'
    JSON = 'json'
    YAML = 'yaml'


def display_violations(violations: Iterator[Violation],
                       method: DisplayMethod = DisplayMethod.TABLE) -> int:
    """Displays the violations to standard output

    Args:
        violations (Iterator[yamlator.violations.Violation]): A collection
            of violations

        method (yamlator.core.DisplayMethod, optional): Defines how the
            violations will be displayed. By default `DisplayMethod.TABLE`
            will be used

    Returns:
        The status code if violations were found. 0 = no violations were found
        and -1 = violations were found

    Raises:
        ValueError: If `violations` or `method` is None
    """
    if violations is None:
        raise ValueError('violations should not be None')

    if method is None:
        raise ValueError('method should not be None')

    strategies = {
        DisplayMethod.JSON: JSONOutput,
        DisplayMethod.TABLE: TableOutput,
        DisplayMethod.YAML: YAMLOutput,
    }

    display_option = strategies.get(method, TableOutput)
    return display_option.display(violations)


def load_schema_path_context(schema_path):
    context = schema_path.split('\\')[:-1]
    return os.path.join(*context)


def load_child_resources(root_schema, context):
    import_statements = root_schema.imports
    for path, items in import_statements.items():
        full_path = os.path.join(context, path)
        schema = load_schema(full_path)
        parsed_schema = parse_schema(schema)
        rulesets = parsed_schema.rulesets

        for item in items:
            item = rulesets.get(item)
            root_schema.rulesets[item.name] = item
    print(root_schema)
