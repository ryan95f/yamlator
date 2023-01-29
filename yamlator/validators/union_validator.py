"""Validator for handling the union type"""

from yamlator.types import Data
from yamlator.types import RuleType
from yamlator.types import UnionRuleType
from yamlator.types import SchemaTypes
from yamlator.violations import TypeViolation
from .base_validator import Validator

from collections import namedtuple

_SchemaTypeDecoder = namedtuple('SchemaTypeDecoder', ['type', 'friendly_name'])
_UnionViolation = namedtuple('UnionViolation', ['count', 'type_name'])

_NO_VIOLATION_COUNT = 0
_MIN_INDEX = 0


class UnionValidator(Validator):
    """Validator for handling the union type"""

    _type_lookups = {
        SchemaTypes.INT: _SchemaTypeDecoder(int, 'int'),
        SchemaTypes.STR: _SchemaTypeDecoder(str, 'str'),
        SchemaTypes.FLOAT: _SchemaTypeDecoder(float, 'float'),
        SchemaTypes.LIST: _SchemaTypeDecoder(list, 'list'),
        SchemaTypes.MAP: _SchemaTypeDecoder(dict, 'map'),
        SchemaTypes.BOOL: _SchemaTypeDecoder(bool, 'bool'),
    }

    _sub_type_validators = {}

    def set_ruleset_validator(self, validator: Validator) -> None:
        self._sub_type_validators[SchemaTypes.RULESET] = validator

    def set_list_validator(self, validator: Validator) -> None:
        self._sub_type_validators[SchemaTypes.LIST] = validator

    def set_regex_validator(self, validator: Validator) -> None:
        self._sub_type_validators[SchemaTypes.REGEX] = validator

    def set_enum_validator(self, validator: Validator) -> None:
        self._sub_type_validators[SchemaTypes.ENUM] = validator

    def set_map_validator(self, validator: Validator) -> None:
        self._sub_type_validators[SchemaTypes.MAP] = validator

    def validate(self, key: str, data: Data, parent: str, rtype: UnionRuleType,
                 is_required: bool = False) -> None:
        """Validate the data against all types defined in the union. If one
        or more types do not match the union, a single `TypeViolation`
        is raised

        __Note__: Any sub violations raised during the processing of
        the union type are removed from the final list

        Args:
            key (str): The key to the data
            data (Data): The data to validate
            parent (str): The parent key of the data
            rtype (RuleType): The type assigned to the rule that will be
                applied to the data
            is_required (bool, optional): Indicates if the rule is required
        """

        is_union_type = (rtype.schema_type == SchemaTypes.UNION)
        if not is_union_type:
            super().validate(key, data, parent, rtype, is_required)
            return

        union_violations = []
        for sub_rule_type in rtype.sub_types:

            validator = self._sub_type_validators.get(sub_rule_type.schema_type)
            if validator is not None:
                union_violation = self._handle_sub_type_validation(
                    validator,
                    key,
                    data,
                    parent,
                    sub_rule_type,
                    is_required
                )
                union_violations.append(union_violation)
                continue

            builtin = self._type_lookups[sub_rule_type.schema_type]
            if not isinstance(data, builtin.type):
                union_violation = _UnionViolation(1, builtin.friendly_name)
                union_violations.append(union_violation)
                continue

            union_violation = _UnionViolation(0, builtin.friendly_name)
            union_violations.append(union_violation)

        union_violations.sort(key=lambda x: x[0])
        if union_violations[_MIN_INDEX].count == _NO_VIOLATION_COUNT:
            return

        expected_types = ', '.join([uv.type_name for uv in union_violations])
        message = f'{key} did not match union types: {expected_types}'
        violation = TypeViolation(key, parent, message)
        self._violations.append(violation)

    def _handle_sub_type_validation(self, validator: Validator, key: str,
                                    data: Data, parent: str, rtype: RuleType,
                                    is_required: bool) -> _UnionViolation:
        if validator is None:
            return _UnionViolation(0, str(rtype))

        violation_count = len(self._violations)
        validator.validate(key, data, parent, rtype, is_required)

        # Remove the violations from the sub validation process
        # to not pollute the output with all the different violations
        # from every type defined in the union
        removed_violations = self._remove_nested_violations(violation_count)
        return _UnionViolation(removed_violations, str(rtype))

    def _remove_nested_violations(self, initial_count) -> int:
        diff = len(self._violations) - initial_count
        for _ in range(0, diff):
            self._violations.pop()
        return diff
