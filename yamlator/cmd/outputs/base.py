"""Maintains the base class for defining an output option and
the SuccessCode Enum
"""

from abc import ABC
from typing import Iterator
from enum import IntEnum

from yamlator.violations import Violation


class SuccessCode(IntEnum):
    SUCCESS = 0
    ERR = -1


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
