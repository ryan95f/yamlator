"""Validator for handling Enum types"""

from collections import deque

from yamlator.types import Data
from yamlator.types import RuleType
from yamlator.types import SchemaTypes
from yamlator.validators.base_validator import Validator


class EnumTypeValidator(Validator):
    """Validator to handle enum types"""

    def __init__(self, violations: deque, enums: dict):
        """EnumTypeValidator init

        Args:
            violations (deque): Contains violations that have been detected
                whilst processing the data
            enums (dict): A dict that contains references to enum values.
        """
        super().__init__(violations)
        self._enums = enums

    def validate(self, key: str, data: Data, parent: str, rtype: RuleType,
                 is_required: bool = False) -> None:
        """Validate enum data. If the data does not align to a known value
        in the enum, then a `TypeViolation` is added to the violation list

        Args:
            key (str): The key to the data
            data (Data): The data to validate
            parent (str): The parent key of the data
            rtype (RuleType): The type assigned to the rule that will be
                applied to the data
            is_required (bool, optional): Indicates if the rule is required
        """
        is_enum_type = (rtype.schema_type == SchemaTypes.ENUM)
        if not is_enum_type:
            super().validate(key, data, parent, rtype, is_required)
            return

        is_enum_data = isinstance(data, (str, float, int))
        if not is_enum_data:
            self._add_enum_violation(key, parent, rtype.lookup)
            return

        if self._matches_enum_data(data, rtype.lookup):
            return

        self._add_enum_violation(key, parent, rtype.lookup)

    def _matches_enum_data(self, data: Data, enum_name: str) -> bool:
        target_enum = self._enums.get(enum_name)
        if target_enum is None:
            return False

        enum_value = target_enum.items.get(data)
        return enum_value is not None

    def _add_enum_violation(self, key: str, parent: str, enum_name: str):
        message = f'{key} does not match any value in enum {enum_name}'
        self._add_type_violation(key, parent, message)
