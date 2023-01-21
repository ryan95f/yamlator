from collections import Counter

from yamlator.types import Data
from yamlator.types import RuleType
from yamlator.types import UnionRuleType
from yamlator.types import SchemaTypes
from yamlator.violations import TypeViolation
from .base_validator import Validator

from collections import namedtuple

_SchemaTypeDecoder = namedtuple('SchemaTypeDecoder', ['type', 'friendly_name'])


class UnionValidator(Validator):
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

        expected_types = []
        ripped_violations = []
        flags = []

        for union_type in rtype.sub_types:
            
            if union_type.schema_type == SchemaTypes.LIST:
                violations = self._handle_list_validation(key, data, parent, union_type, is_required)
                flags.append(len(violations))
                ripped_violations.append(violations)
                continue

            if union_type.schema_type == SchemaTypes.RULESET:
                violations = self._handle_ruleset_validation(key, data, parent, union_type, is_required)
                flags.append(len(violations))
                ripped_violations.append(violations)
                continue
            
            if union_type.schema_type == SchemaTypes.REGEX:
                violations = self._handle_regex_validation(key, data, parent, union_type, is_required)
                flags.append(len(violations))
                ripped_violations.append(violations)
                continue
            
            builtin = self._type_lookups[union_type.schema_type]
            if not isinstance(data, builtin.type):
                flags.append(1)
                ripped_violations.append([])
                expected_types.append(builtin.friendly_name)
                continue

            flags.append(0)

        flags.sort()
        if flags[0] == 0:
            return

        occurrence = Counter(flags)
        if occurrence[flags[-1]] == 1:
            self._violations.extend(ripped_violations[-1])
            return

        e = ", ".join(expected_types)
        message = f"Expect types {e} defined in the Union"
        violation = TypeViolation(key, parent, message)
        self._violations.append(violation)

    def _handle_list_validation(self, key: str, data: Data, parent: str,
                                rtype: RuleType, is_required: bool) -> list:
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
        violation_count = len(self._violations)
        self._ruleset_validator.validate(key, data, parent, rtype, is_required)
        return self._extract_new_violations(violation_count)

    def _handle_regex_validation(self, key: str, data: Data, parent: str,
                                 rtype: RuleType, is_required: bool) -> list:
        if rtype.schema_type != SchemaTypes.REGEX:
            return

        violation_count = len(self._violations)
        self._regex_validator.validate(key, data, parent, rtype, is_required)
        return self._extract_new_violations(violation_count)

    def set_ruleset_validator(self, validator: Validator) -> None:
        self._ruleset_validator = validator

    def set_list_validator(self, validator: Validator) -> None:
        self._list_validator = validator

    def set_regex_validator(self, validator: Validator) -> None:
        self._regex_validator = validator
