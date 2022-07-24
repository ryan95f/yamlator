"""Handles the command line utility functions and entry point"""


import argparse
import json
import yaml

from abc import ABC
from typing import Iterator
from enum import Enum
from collections import deque

from yamlator.utils import load_yaml_file
from yamlator.utils import load_schema
from yamlator.parser import SchemaSyntaxError
from yamlator.parser import parse_schema
from yamlator.validators.core import validate_yaml

from yamlator.exceptions import InvalidSchemaFilenameError
from yamlator.exceptions import SchemaParseError
from yamlator.violations import Violation
from yamlator.violations import RequiredViolation
from yamlator.violations import TypeViolation
from yamlator.violations import BuiltInTypeViolation
from yamlator.violations import RulesetTypeViolation
from yamlator.violations import RegexTypeViolation
from yamlator.violations import ViolationJSONEncoder


SUCCESS = 0
ERR = -1


def main() -> int:
    """Entry point into the Yamler CLI

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
        print(ex)
        return ERR
    except SchemaSyntaxError as ex:
        print(ex)
        return ERR
    except FileNotFoundError as ex:
        print(ex)
        return ERR
    except InvalidSchemaFilenameError as ex:
        print(ex)
        return ERR
    except ValueError as ex:
        print(ex)
        return ERR

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
        A Iterator collection of `Violation` objects that contains
        the violations detected in the YAML data against the schema.

    Raises:
        ValueError: If either argument is `None` or an empty string
        FileNotFoundError: If either argument cannot be found on the file system
        InvalidSchemaFilenameError: If `schema_filepath` does not have
        a valid filename that ends with the `.ys` extension.
    """
    yaml_data = load_yaml_file(yaml_filepath)
    ruleset_data = load_schema(schema_filepath)

    instructions = parse_schema(ruleset_data)
    return validate_yaml(yaml_data, instructions)


class DisplayMethod(Enum):
    """Represents the supported violation display methods"""
    TABLE = 'table'
    JSON = 'json'
    YAML = 'yaml'


def display_violations(violations: Iterator[Violation],
                       method: DisplayMethod = DisplayMethod.TABLE) -> int:
    """Displays the violations to standard output

    Args:
        violations (Iterator[Violation]): A collection of violations

        method               (DisplayMethod): Defines how the violations will be
        displayed. By default table will be used specified

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


class ViolationOutput(ABC):
    """Base class for displaying violations"""

    @staticmethod
    def display(violations: Iterator[Violation]) -> int:
        """Display the violations to the user

        Args:
            violations (Iterator[Violation]): A collection of violations

        Returns:
            The status code if violations were found. 0 = no
            violations were found and -1 = violations were found
        """
        pass


class TableOutput(ViolationOutput):
    """Displays violations as a table"""

    @staticmethod
    def display(violations: Iterator[Violation]) -> int:
        """Display the violations to the user as a table

        Args:
            violations (Iterator[Violation]): A collection of violations

        Returns:
            The status code if violations were found. 0 = no
            violations were found and -1 = violations were found
        """
        if violations is None:
            raise ValueError('violations should not be None')

        violation_count = len(violations)
        print(f'\n{violation_count:<4} violation(s) found')

        has_violations = violation_count != 0
        if not has_violations:
            return SUCCESS

        parent_title = 'Parent Key'
        key_title = 'Key'
        violation_title = 'Violation'
        message_title = 'Message'
        print(f'\n{parent_title:<30} {key_title:<20} {violation_title:<15} {message_title:<20}')  # nopep8 pylint: disable=C0301

        print('---------------------------------------------------------------------------')  # nopep8 pylint: disable=C0301
        for violation in violations:
            print(f'{violation.parent:<30} {violation.key:<20} {violation.violation_type:<15} {violation.message:<20}')  # nopep8 pylint: disable=C0301
        print('---------------------------------------------------------------------------')  # nopep8 pylint: disable=C0301
        return ERR


class JSONOutput(ViolationOutput):
    """Displays violations as JSON"""

    @staticmethod
    def display(violations: Iterator[Violation]) -> int:
        """Display the violations to the user as JSON

        Args:
            violations (Iterator[Violation]): A collection
            of violations

        Returns:
            The status code if violations were found. 0 = no
            violations were found and -1 = violations were found
        """
        if violations is None:
            raise ValueError('violations should not be None')

        violation_count = len(violations)
        pre_json_data = {
            'violations': violations,
            'violations_count': violation_count
        }

        json_data = json.dumps(pre_json_data,
                               cls=ViolationJSONEncoder, indent=4)
        print(json_data)

        return SUCCESS if violation_count == 0 else ERR


class YAMLOutput(ViolationOutput):
    """Display violations as YAML"""

    @staticmethod
    def display(violations: Iterator[Violation]) -> int:
        """Display the violations to the user as YAML

        Args:
            violations (Iterator[Violation]): A collection
            of violations

        Returns:
            The status code if violations were found. 0 = no
            violations were found and -1 = violations were found
        """

        if violations is None:
            raise ValueError('violations should not be None')

        YAMLOutput._set_up_dumper()

        violation_count = len(violations)
        data = {
            'violations': violations,
            'violationCount': violation_count
        }

        yaml_str = yaml.dump(data)
        print(yaml_str)
        return SUCCESS if violation_count == 0 else ERR

    @staticmethod
    def _set_up_dumper() -> None:
        yaml.add_representer(deque, deque_dumper)
        yaml.add_representer(RequiredViolation, violation_dumper)
        yaml.add_representer(TypeViolation, violation_dumper)
        yaml.add_representer(BuiltInTypeViolation, violation_dumper)
        yaml.add_representer(RulesetTypeViolation, violation_dumper)
        yaml.add_representer(RegexTypeViolation, violation_dumper)


def deque_dumper(dumper: yaml.Dumper, data: deque) -> yaml.SequenceNode:
    return dumper.represent_list(data)

def violation_dumper(dumper: yaml.Dumper, data: Violation) -> yaml.SequenceNode:
    data_dict = {
        'key': data.key,
        'parent': data.parent,
        'message': data.message,
        'violationType': data.violation_type
    }
    return dumper.represent_dict(data_dict)
