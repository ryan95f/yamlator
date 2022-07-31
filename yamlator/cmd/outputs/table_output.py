"""Display output class for generating a table"""
from typing import Iterator

from yamlator.violations import Violation
from yamlator.cmd.outputs.base import SuccessCode
from yamlator.cmd.outputs.base import ViolationOutput


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

        Raises:
            ValueError: If the violations list is None
        """
        if violations is None:
            raise ValueError('violations should not be None')

        violation_count = len(violations)
        print(f'\n{violation_count:<4} violation(s) found')

        has_violations = violation_count != 0
        if not has_violations:
            return SuccessCode.SUCCESS

        parent_title = 'Parent Key'
        key_title = 'Key'
        violation_title = 'Violation'
        message_title = 'Message'
        print(f'\n{parent_title:<30} {key_title:<20} {violation_title:<15} {message_title:<20}')  # nopep8 pylint: disable=C0301

        print('---------------------------------------------------------------------------')  # nopep8 pylint: disable=C0301
        for violation in violations:
            print(f'{violation.parent:<30} {violation.key:<20} {violation.violation_type:<15} {violation.message:<20}')  # nopep8 pylint: disable=C0301
        print('---------------------------------------------------------------------------')  # nopep8 pylint: disable=C0301
        return SuccessCode.ERR
