"""Validator for handling the builtin types"""


from collections import deque
from collections import namedtuple

from yamlator.types import Data
from yamlator.types import RuleType
from yamlator.types import SchemaTypes
from yamlator.validators.base_validator import Validator

_SchemaTypeDecoder = namedtuple('SchemaTypeDecoder', ['type', 'friendly_name'])


class BuiltInTypeValidator(Validator):
    """Validator to handle the builtin types. e.g `int`, `list` & `str`"""

    def __init__(self, violations: deque) -> None:
        """BuiltInTypeValidator init

        Args:
            violations (deque): Contains violations that have been detected
                whilst processing the data
        """
        super().__init__(violations)
        self._built_in_lookups = {
            SchemaTypes.INT: _SchemaTypeDecoder(int, 'int'),
            SchemaTypes.STR: _SchemaTypeDecoder(str, 'str'),
            SchemaTypes.FLOAT: _SchemaTypeDecoder(float, 'float'),
            SchemaTypes.LIST: _SchemaTypeDecoder(list, 'list'),
            SchemaTypes.MAP: _SchemaTypeDecoder(dict, 'map'),
            SchemaTypes.BOOL: _SchemaTypeDecoder(bool, 'bool'),
        }

    def validate(self, key: str, data: Data, parent: str, rtype: RuleType,
                 is_required: bool = False) -> None:
        """Validate the data against the core base types. If the data
        does not match the expected type, then a `TypeViolation` is added
        to the list of violations

        Args:
            key (str): The key to the data
            data (Data): The data to validate
            parent (str): The parent key of the data
            rtype (RuleType): The type assigned to the rule that will be
                applied to the data
            is_required (bool, optional): Indicates if the rule is required
        """
        buildin_type = self._built_in_lookups.get(rtype.schema_type)
        is_not_build_in_type = (buildin_type is None)

        if is_not_build_in_type:
            super().validate(key, data, parent, rtype, is_required)
            return

        if not isinstance(data, buildin_type.type):
            message = f'{key} should be of type {buildin_type.friendly_name}'
            self._add_type_violation(key, parent, message)
            return

        super().validate(key, data, parent, rtype, is_required)
