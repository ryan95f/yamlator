from collections import Counter

from yamlator.types import Data
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
            print(union_type)
            v = self._type_lookups.get(union_type.schema_type, _SchemaTypeDecoder(int, 'int'))

            if not isinstance(data, v.type):
                flags.append(1)
                ripped_violations.append([])
                expected_types.append(v.friendly_name)

            violation_count = len(self._violations)
            if isinstance(data, list) and union_type.schema_type == SchemaTypes.LIST:
                self._list_validator.validate(key, data, parent, union_type, is_required)
                diff = len(self._violations) - violation_count
                flags.append(diff)
                s = []
                if diff > 0:
                    while diff > 0:
                        s.append(self._violations.pop())
                        diff -= 1
                    ripped_violations.append(s)
                continue
            
            violation_count = len(self._violations)
            if isinstance(data, dict) and union_type.schema_type == SchemaTypes.RULESET:
                self._ruleset_validator.validate(key, data, parent, union_type, is_required)
                diff = len(self._violations) - violation_count
                flags.append(diff)
                s = []
                if diff > 0:
                    while diff > 0:
                        s.append(self._violations.pop())
                        diff -= 1
                    ripped_violations.append(s)
                continue
            
            violation_count = len(self._violations)
            if isinstance(data, str) and union_type.schema_type == SchemaTypes.REGEX:
                self._regex_validator.validate(key, data, parent, union_type, is_required)
                diff = len(self._violations) - violation_count
                flags.append(diff)
                s = []
                if diff > 0:
                    while diff > 0:
                        s.append(self._violations.pop())
                        diff -= 1
                    ripped_violations.append(s)
                continue
        
        print(ripped_violations)
        _, val = min(enumerate(flags), key=lambda x: x[1])
        if val == 0:
            return

        x = Counter(flags)
        print(x)
        idx, val = max(enumerate(flags), key=lambda x: x[1])
        if x[val] == 1:
            self._violations.extend(ripped_violations[idx])
            return

        e = ", ".join(expected_types)
        message = f"Expect types {e} defined in the Union"
        violation = TypeViolation(key, parent, message)
        self._violations.append(violation)

    def set_ruleset_validator(self, validator: Validator) -> None:
        self._ruleset_validator = validator

    def set_list_validator(self, validator: Validator) -> None:
        self._list_validator = validator

    def set_regex_validator(self, validator: Validator) -> None:
        self._regex_validator = validator
