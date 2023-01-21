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
_UnionViolation = namedtuple('UnionViolation', ['count', 'violations'])


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
                violations = self._handle_list_validation(key, data,
                                                          parent, union_type,
                                                          is_required)
                union_violation = _UnionViolation(len(violations), violations)
                union_violations.append(union_violation)
                continue

            if union_type.schema_type == SchemaTypes.RULESET:
                violations = self._handle_ruleset_validation(key, data,
                                                             parent, union_type,
                                                             is_required)
                union_violation = _UnionViolation(len(violations), violations)
                union_violations.append(union_violation)
                continue

            if union_type.schema_type == SchemaTypes.REGEX:
                violations = self._handle_regex_validation(key, data,
                                                           parent, union_type,
                                                           is_required)
                union_violation = _UnionViolation(len(violations), violations)
                union_violations.append(union_violation)
                continue

            builtin = self._type_lookups[union_type.schema_type]
            if not isinstance(data, builtin.type):
                union_violation = _UnionViolation(1, [])
                union_violations.append(union_violation)
                continue

            union_violations.append(_UnionViolation(0, []))

        union_violations.sort(key=lambda x: x[0])
        if union_violations[0].count == 0:
            return

        occurrence = Counter([uv.count for uv in union_violations])
        if occurrence[union_violations[-1].count] == 1:
            self._violations.extend(union_violations[-1].violations)
            return

        message = 'Expected types in the union do not match'
        violation = TypeViolation(key, parent, message)
        self._violations.append(violation)

    def _handle_list_validation(self, key: str, data: Data, parent: str,
                                rtype: RuleType, is_required: bool) -> list:
        if self._list_validator is None:
            return []

        violation_count = len(self._violations)
        self._list_validator.validate(key, data, parent, rtype, is_required)
        return self._extract_new_violations(violation_count)

    def _extract_new_violations(self, violation_count: int) -> list:
        diff = len(self._violations) - violation_count
        if diff == 0:
            return []

        ripped_violations = []
        for _ in range(0, diff):
            ripped_violations.append(self._violations.pop())
        return ripped_violations

    def _handle_ruleset_validation(self, key: str, data: Data, parent: str,
                                   rtype: RuleType, is_required: bool) -> list:
        if self._ruleset_validator is None:
            return []

        violation_count = len(self._violations)
        self._ruleset_validator.validate(key, data, parent, rtype, is_required)
        return self._extract_new_violations(violation_count)

    def _handle_regex_validation(self, key: str, data: Data, parent: str,
                                 rtype: RuleType, is_required: bool) -> list:
        if self._regex_validator is None:
            return []

        violation_count = len(self._violations)
        self._regex_validator.validate(key, data, parent, rtype, is_required)
        return self._extract_new_violations(violation_count)

    def set_ruleset_validator(self, validator: Validator) -> None:
        self._ruleset_validator = validator

    def set_list_validator(self, validator: Validator) -> None:
        self._list_validator = validator

    def set_regex_validator(self, validator: Validator) -> None:
        self._regex_validator = validator
