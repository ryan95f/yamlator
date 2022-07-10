"""Base Yamlator validator"""

from __future__ import annotations
from collections import deque

from yamlator.types import Data
from yamlator.types import RuleType
from yamlator.violations import TypeViolation


class Validator:
    """Base Validator handler"""

    _next_validator = None

    def __init__(self, violations: deque) -> None:
        """Validator init

        Args:
            violations (deque): Contains violations that have been detected
                whilst processing the data
        """
        self._violations = violations

    def set_next_validator(self, validator: Validator) -> Validator:
        """Set the next validator in the chain

        Args:
            validator (Validator): The next validator in the chain

        Returns:
            Validator: The object that was provided in the `validator` parameter
        """
        self._next_validator = validator
        return validator

    def validate(self, key: str, data: Data, parent: str, rtype: RuleType,
                 is_required: bool = False) -> None:
        """Validate the data against the next validator in the chain

        Args:
            key (str): The key to the data
            data (Data): The data to validate
            parent (str): The parent key of the data
            rtype (RuleType): The type assigned to the rule that will be
                applied to the data
            is_required (bool, optional): Indicates if the rule is required
        """

        if self._next_validator is not None:
            self._next_validator.validate(
                key=key,
                data=data,
                parent=parent,
                rtype=rtype,
                is_required=is_required
            )

    def _add_type_violation(self, key: str, parent: str, message: str) -> None:
        violation = TypeViolation(key, parent, message)
        self._violations.append(violation)
