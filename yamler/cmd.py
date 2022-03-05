import argparse

from abc import ABC
from enum import Enum
from typing import Iterator
from yamler.exceptions import InvalidRulesetFilenameError
from yamler.violations import ViolationType

from .parser import YamlerParser
from .wranglers import wrangle_data
from .utils import load_yaml_file, load_yamler_ruleset


def main() -> int:
    parser = _create_args_parser()
    args = parser.parse_args()
    violations = []

    try:
        violations = validate_yaml_data_from_file(args.file, args.ruleset_schema)
    except FileNotFoundError as ex:
        print(ex)
        return StatusCode.ERR.value
    except InvalidRulesetFilenameError as ex:
        print(ex)
        return StatusCode.ERR.value
    except ValueError as ex:
        print(ex)
        return StatusCode.ERR.value

    return display_violations(violations)


def _create_args_parser():
    description = 'A YAML validation tool that determines if a YAML file matches a given ruleset schema'  # nopep8

    parser = argparse.ArgumentParser(prog="yamler", description=description)
    parser.add_argument('file', type=str,
                        help='The file to be validated')

    parser.add_argument("-schema", type=str, required=True, dest='ruleset_schema',
                        help="The schama that will be used to validate the file")
    return parser


def validate_yaml_data_from_file(yaml_filepath: str,
                                 ruleset_filepath: str) -> Iterator[ViolationType]:
    """Validate a YAML file with a ruleset

    Args:
        yaml_filepath    (str): The path to the YAML data file
        ruleset_filepath (str): The path to the ruleset file

    Returns:
        A Iterator collection of ViolationType objects that contains
        the violations detected in the YAML data against the rulesets.

    Raises:
        ValueError: If either argument is `None` or an empty string
        FileNotFoundError: If either argument cannot be found on the file system
        InvalidRulesetFilenameError: If `ruleset_filepath` does not have a valid filename
        that ends with the `.yamler` extension.
    """
    yaml_data = load_yaml_file(yaml_filepath)
    ruleset = load_yamler_ruleset(ruleset_filepath)

    parser = YamlerParser()
    tokens = parser.parse(ruleset)

    return wrangle_data(yaml_data, tokens)


def display_violations(violations: Iterator[ViolationType]) -> int:
    return ConsoleOutput.display(violations)


class StatusCode(Enum):
    """Status code for the output of running the validaton process"""
    SUCCESS = 0
    ERR = -1


class ViolationOutput(ABC):
    """Base class for displaying violations"""

    def display(violations: Iterator[ViolationType]) -> int:
        """Display the violations to the user

        Args:
            violations Iterator[ViolationType]: A collection of violations

        Returns:
            The status code if violations were found. 0 = no violations were found
            and -1 = violations were found
        """
        pass


class ConsoleOutput(ViolationOutput):
    """Displays violations as a table"""

    def display(violations: Iterator[ViolationType]) -> int:
        """Display the violations to the user as a table

        Args:
            violations Iterator[ViolationType]: A collection of violations

        Returns:
            The status code if violations were found. 0 = no violations were found
            and -1 = violations were found
        """
        violation_count = len(violations)
        print("\n{:<4} violation(s) found".format(violation_count))

        if violation_count == 0:
            return StatusCode.SUCCESS.value

        print('\n{:<30} {:<20} {:<15} {:20}'.format(
                'Parent Key', 'Key', 'Violation', 'Message'))
        print('---------------------------------------------------------------------------')  # nopep8
        for violation in violations:
            print('{:<30} {:<20} {:<15} {:20}'.format(
                violation.parent,
                violation.key,
                violation.violation_type,
                violation.message))
        print('---------------------------------------------------------------------------')  # nopep8
        return StatusCode.ERR.value
