import argparse
import json

from abc import ABC
from typing import Iterator

from yamler.parser import parse_rulesets
from yamler.validators import validate_yaml
from yamler.utils import load_yaml_file
from yamler.utils import load_yamler_ruleset
from yamler.exceptions import InvalidRulesetFilenameError
from yamler.violations import ViolationJSONEncoder, ViolationType


SUCCESS = 0
ERR = -1


def main() -> int:
    parser = _create_args_parser()
    args = parser.parse_args()
    violations = []

    try:
        violations = validate_yaml_data_from_file(args.file, args.ruleset_schema)
    except FileNotFoundError as ex:
        print(ex)
        return ERR
    except InvalidRulesetFilenameError as ex:
        print(ex)
        return ERR
    except ValueError as ex:
        print(ex)
        return ERR

    return display_violations(violations, args.output)


def _create_args_parser():
    description = 'A YAML validation tool that determines if a YAML file matches a given ruleset schema'  # nopep8

    parser = argparse.ArgumentParser(prog="yamler", description=description)
    parser.add_argument('file', type=str,
                        help='The YAML file to be validated')

    parser.add_argument('-s', '--schema', type=str, required=True, dest='ruleset_schema',
                        help='The schama that will be used to validate the YAML file')

    parser.add_argument('-o', '--output', type=str, required=False, default='table',
                        choices=['table', 'json'],
                        help='Defines the format that will be displayed for the violations')  # nopep8
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
    ruleset_data = load_yamler_ruleset(ruleset_filepath)

    instructions = parse_rulesets(ruleset_data)
    return validate_yaml(yaml_data, instructions)


def display_violations(violations: Iterator[ViolationType], method: str = 'table') -> int:
    """Displays the violations to standard output

    Args:
        violations (Iterator[ViolationType]): A collection of violations
        method                         (str): Defines how the violations will be
        displayed. Supported options are 'table' or 'json'. By default table will be
        used unless method = 'json' is specified.

    Returns:
        The status code if violations were found. 0 = no violations were found
        and -1 = violations were found
    """
    if method.lower() == 'json':
        return JSONOutput.display(violations)
    return TableOutput.display(violations)


class ViolationOutput(ABC):
    """Base class for displaying violations"""

    def display(violations: Iterator[ViolationType]) -> int:
        """Display the violations to the user

        Args:
            violations (Iterator[ViolationType]): A collection of violations

        Returns:
            The status code if violations were found. 0 = no violations were found
            and -1 = violations were found
        """
        pass


class TableOutput(ViolationOutput):
    """Displays violations as a table"""

    def display(violations: Iterator[ViolationType]) -> int:
        """Display the violations to the user as a table

        Args:
            violations (Iterator[ViolationType]): A collection of violations

        Returns:
            The status code if violations were found. 0 = no violations were found
            and -1 = violations were found
        """
        violation_count = len(violations)
        print("\n{:<4} violation(s) found".format(violation_count))

        has_violations = violation_count != 0
        if not has_violations:
            return SUCCESS

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
        return ERR


class JSONOutput(ViolationOutput):
    """Displays violations as JSON"""

    def display(violations: Iterator[ViolationType]) -> int:
        """Display the violations to the user as JSON

        Args:
            violations (Iterator[ViolationType]): A collection of violations

        Returns:
            The status code if violations were found. 0 = no violations were found
            and -1 = violations were found
        """
        violation_count = len(violations)
        data = {'violatons': violations, 'violation_count': violation_count}

        json_data = json.dumps(data, cls=ViolationJSONEncoder, indent=4)
        print(json_data)

        return SUCCESS if violation_count == 0 else ERR
