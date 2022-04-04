from __future__ import annotations
import json

from collections import deque
from enum import Enum
from typing import Any


class ViolationType(Enum):
    REQUIRED = 'required'
    TYPE = 'type'


class ViolationJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle the Violation classes"""

    def default(self, o: Any) -> Any:
        if isinstance(o, deque):
            return list(o)

        if issubclass(type(o), Violation):
            return {
                'key': o.key,
                'parent': o.parent,
                'message': o.message,
                'violation_type': o.violation_type
            }
        return super().default(o)


class Violation:
    def __init__(self, key: str, parent: str, message: str, v_type: ViolationType):
        """Violation init

        Args:
            key     (str):              The key name in the YAML file
            parent  (str):              The parent key in the YAML file
            message (str):              The message with information regarding
            the violation

            v_type  (ViolationType):    The violation type. Either `REQUIRED` or `TYPE`
        """
        self.key = key
        self.message = message
        self.parent = parent
        self._violation_type = v_type

    @property
    def violation_type(self) -> str:
        return self._violation_type.value

    def __repr__(self) -> str:
        message_template = '{}(parent={}, key={}, message={}'
        return message_template.format(__class__.__name__,
                                       self.parent, self.key, self.message)


class RequiredViolation(Violation):
    """Violation for when a required field is missing"""

    def __init__(self, key: str, parent: str):
        """RequiredViolation constructor

        Args:
            key     (str):  The key name in the YAML file
            parent  (str):  The parent key in the YAML file
        """
        message = f'{key} is missing'
        super().__init__(key, parent, message, ViolationType.REQUIRED)


class TypeViolation(Violation):
    """Violation when a value in the YAML file has an incorrect type"""

    def __init__(self, key: str, parent: str, message: str):
        """TypeViolation constructor

        Args:
            key     (str):  The key name in the YAML file
            parent  (str):  The parent key in the YAML file
            message (str):  The message with information regarding the type violation
        """
        super().__init__(key, parent, message, ViolationType.TYPE)


class BuiltInTypeViolation(TypeViolation):
    """Type violation when a field is not using the required
    built in type e.g (float, int, str, list)
    """

    def __init__(self, key: str, parent: str, expected_type: type):
        """BuiltInTypeViolation constructor

        Args:
            key             (str):  The key name in the YAML file
            parent          (str):  The parent key in the YAML file
            expected_type   (type): The expected build in type for the field
        """
        message = f"{key} is expected to be an {expected_type.__name__}"
        super().__init__(key, parent, message)


class RulesetTypeViolation(TypeViolation):
    """Type violation when a field is not a ruleset (dict) in the file"""

    def __init__(self, key: str, parent: str):
        """RulesetTypeViolation constructor

        Args:
            key     (str):  The key name in the YAML file
            parent  (str):  The parent key in the YAML file
        """
        message = f'{key} should be a ruleset'
        super().__init__(key, parent, message)
