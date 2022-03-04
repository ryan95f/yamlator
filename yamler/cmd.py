import argparse

from abc import ABC
from typing import Iterator
from yamler.violations import ViolationType

from .parser import YamlerParser
from .wranglers import wrangle_data
from .utils import load_yaml_file, load_yamler_ruleset


class ViolationOutput(ABC):
    def display(violations: Iterator[ViolationType]) -> int:
        pass


class ConsoleOutput(ViolationOutput):
    def display(violations: Iterator[ViolationType]) -> int:
        violation_count = len(violations)
        print("\n{:<4} violation(s) found".format(violation_count))

        if violation_count == 0:
            return 0

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
        return -1


def display_violations(violations: Iterator[ViolationType],
                       method: str = "console") -> int:
    return ConsoleOutput.display(violations)


def validate_yaml_data_from_file(yaml_filepath: str,
                                 ruleset_filepath: str) -> Iterator[ViolationType]:
    yaml_data = load_yaml_file(yaml_filepath)
    ruleset = load_yamler_ruleset(ruleset_filepath)

    parser = YamlerParser()
    tokens = parser.parse(ruleset)

    return wrangle_data(yaml_data, tokens)


def _create_args_parser():
    description = 'A YAML validation tool that determines if a YAML file matches a given ruleset schema'  # nopep8

    parser = argparse.ArgumentParser(prog="yamler", description=description)
    parser.add_argument('file', type=str,
                        help='The file to be validated')

    parser.add_argument("-schema", type=str, required=True, dest='ruleset_schema',
                        help="The schama that will be used to validate the file")
    return parser


def main() -> int:
    parser = _create_args_parser()
    args = parser.parse_args()

    violations = validate_yaml_data_from_file(args.file, args.ruleset_schema)
    return display_violations(violations)
