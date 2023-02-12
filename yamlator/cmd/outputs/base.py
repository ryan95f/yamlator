"""Maintains the basic building blocks used by the output classes"""

import abc
import enum

from typing import Iterator

from yamlator.violations import Violation


class SuccessCode(enum.IntEnum):
    SUCCESS = 0
    ERR = -1


class ViolationOutput(abc.ABC):
    """Base class for displaying violations"""

    @staticmethod
    def display(violations: Iterator[Violation]) -> int:
        """Display the violations to the user

        Args:
            violations (Iterator[yamlator.violations.Violation]): A collection
                of violations

        Returns:
            The status code if violations were found. 0 = no
            violations were found and -1 = violations were found
        """
        pass
