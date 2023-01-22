"""Validator for handling the union type"""

from yamlator.types import Data
from yamlator.types import RuleType
from yamlator.types import UnionRuleType
from yamlator.types import SchemaTypes
from yamlator.violations import TypeViolation
from .base_validator import Validator

from collections import Counter
from collections import namedtuple

_SchemaTypeDecoder = namedtuple('SchemaTypeDecoder', ['type', 'friendly_name'])
_UnionViolation = namedtuple('UnionViolation', [
    'count',
    'violations',
    'type_name'
])

_NO_VIOLATION_COUNT = 0
_MIN_INDEX = 0
_MAX_INDEX = -1


class UnionValidator(Validator):
    """Validator for handling the union type"""

    _ruleset_validator: Validator = None
    _list_validator: Validator = None
    _regex_validator: Validator = None

    _type_lookups = {
        SchemaTypes.INT: _SchemaTypeDecoder(int, 'int'),
        SchemaTypes.STR: _SchemaTypeDecoder(str, 'str'),
        SchemaTypes.FLOAT: _SchemaTypeDecoder(float, 'float'),
        SchemaTypes.LIST: _SchemaTypeDecoder(list, 'list'),
        SchemaTypes.MAP: _SchemaTypeDecoder(dict, 'map'),
        SchemaTypes.BOOL: _SchemaTypeDecoder(bool, 'bool'),
        SchemaTypes.REGEX: _SchemaTypeDecoder(str, 'regex'),
        SchemaTypes.RULESET: _SchemaTypeDecoder(dict, 'ruleset')
    }

    def validate(self, key: str, data: Data, parent: str, rtype: UnionRuleType,
                 is_required: bool = False) -> None:

        is_union_type = (rtype.schema_type == SchemaTypes.UNION)
        if not is_union_type:
            super().validate(key, data, parent, rtype, is_required)
            return

        union_violations: 'list[_UnionViolation]' = []
        for union_type in rtype.sub_types:

            if union_type.schema_type == SchemaTypes.LIST:
                union_violation = self._handle_validation(
                    self._list_validator,
                    key,
                    data,
                    parent,
                    union_type,
                    is_required
                )
                union_violations.append(union_violation)
                continue

            if union_type.schema_type == SchemaTypes.RULESET:
                union_violation = self._handle_validation(
                    self._ruleset_validator,
                    key,
                    data,
                    parent,
                    union_type,
                    is_required
                )
                union_violations.append(union_violation)
                continue

            if union_type.schema_type == SchemaTypes.REGEX:
                union_violation = self._handle_validation(
                    self._regex_validator,
                    key,
                    data,
                    parent,
                    union_type,
                    is_required
                )
                union_violations.append(union_violation)
                continue

            builtin = self._type_lookups[union_type.schema_type]
            if not isinstance(data, builtin.type):
                union_violation = _UnionViolation(1, [], builtin.friendly_name)
                union_violations.append(union_violation)
                continue

            union_violation = _UnionViolation(0, [], builtin.friendly_name)
            union_violations.append(union_violation)

        union_violations.sort(key=lambda x: x[0])
        if union_violations[_MIN_INDEX].count == _NO_VIOLATION_COUNT:
            return

        occurrence = Counter([uv.count for uv in union_violations])
        if occurrence[union_violations[_MAX_INDEX].count] == 1:
            self._violations.extend(union_violations[_MAX_INDEX].violations)
            return

        expected_types = ', '.join([uv.type_name for uv in union_violations])
        message = f'{key} did not match union types: {expected_types}'
        violation = TypeViolation(key, parent, message)
        self._violations.append(violation)

    def _handle_validation(self, validator: Validator, key: str, data: Data,
                           parent: str, rtype: RuleType,
                           is_required: bool) -> _UnionViolation:
        if validator is None:
            return []

        violation_count = len(self._violations)
        validator.validate(key, data, parent, rtype, is_required)
        violations = self._extract_new_violations(violation_count)
        name = self._type_lookups[rtype.schema_type].friendly_name
        return _UnionViolation(len(violations), violations, name)

    def _extract_new_violations(self, violation_count: int) -> list:
        diff = len(self._violations) - violation_count
        if diff == 0:
            return []

        ripped_violations = []
        for _ in range(0, diff):
            ripped_violations.append(self._violations.pop())
        return ripped_violations

    def set_ruleset_validator(self, validator: Validator) -> None:
        self._ruleset_validator = validator

    def set_list_validator(self, validator: Validator) -> None:
        self._list_validator = validator

    def set_regex_validator(self, validator: Validator) -> None:
        self._regex_validator = validator
