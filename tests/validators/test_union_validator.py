"""Test cases for the UnionValidator

Test cases:
    * `test_union_validation` tests the union validation with a dummy
    validator.
    * `test_union_validation_without_sub_validators` to validate
     the validation process is halted when a validator is not provided
"""

import unittest
import typing

from parameterized import parameterized
from .base import BaseValidatorTest

from yamlator.types import Data
from yamlator.types import RuleType
from yamlator.types import UnionRuleType
from yamlator.types import SchemaTypes
from yamlator.violations import TypeViolation
from yamlator.validators import UnionValidator
from yamlator.validators.base_validator import Validator


class DummyValidator(Validator):
    """Dummy Validator to test the union validator

    This validator will always return a Type violation
    """
    def validate(self, key: str, data: Data, parent: str, rtype: RuleType,
                 is_required: bool = False) -> None:
        # Not used by the DummyValidator
        del data
        del is_required
        del rtype

        message = 'Invalid type'
        violation = TypeViolation(key, parent, message)
        self._violations.append(violation)


class TestUnionValidator(BaseValidatorTest):
    """Test cases for the Union Validator"""

    @parameterized.expand([
        ('rule_not_union_type', RuleType(SchemaTypes.FLOAT), 1.23, 0),
        ('union_rule_with_invalid_data', UnionRuleType([
            RuleType(SchemaTypes.LIST, sub_type=RuleType(SchemaTypes.INT)),
            RuleType(SchemaTypes.MAP, sub_type=RuleType(SchemaTypes.INT)),
            RuleType(SchemaTypes.RULESET, lookup='test'),
            RuleType(SchemaTypes.STR)
        ]), 1.23, 1),
        ('union_rule_with_valid_data', UnionRuleType([
            RuleType(SchemaTypes.LIST, sub_type=RuleType(SchemaTypes.INT)),
            RuleType(SchemaTypes.MAP, sub_type=RuleType(SchemaTypes.INT)),
            RuleType(SchemaTypes.RULESET, lookup='test'),
            RuleType(SchemaTypes.FLOAT)
        ]), 1.23, 0),
    ])
    def test_union_validation(self, name: str,
                              rtype: typing.Union[UnionRuleType, RuleType],
                              data: Data,
                              expected_violation_count: int):
        # Unused by test case, however is required by the parameterized library
        del name

        validator = UnionValidator(self.violations)
        self._set_sub_type_validators(validator)
        validator.validate(self.key, data, self.parent, rtype)

        actual_violation_count = len(self.violations)
        self.assertEqual(expected_violation_count, actual_violation_count)

    def _set_sub_type_validators(self, validator: UnionValidator):
        dummy_validator = DummyValidator(self.violations)

        validator.set_enum_validator(dummy_validator)
        validator.set_list_validator(dummy_validator)
        validator.set_map_validator(dummy_validator)
        validator.set_regex_validator(dummy_validator)
        validator.set_ruleset_validator(dummy_validator)

    @parameterized.expand([
        ('rule_not_union_type', RuleType(SchemaTypes.FLOAT), 1.23, 0),
        ('union_rule_with_invalid_data', UnionRuleType([
            RuleType(SchemaTypes.LIST, sub_type=RuleType(SchemaTypes.INT)),
            RuleType(SchemaTypes.MAP, sub_type=RuleType(SchemaTypes.INT)),
            RuleType(SchemaTypes.RULESET, lookup='test'),
            RuleType(SchemaTypes.STR)
        ]), 1.23, 0),
        ('union_rule_with_valid_data', UnionRuleType([
            RuleType(SchemaTypes.LIST, sub_type=RuleType(SchemaTypes.INT)),
            RuleType(SchemaTypes.MAP, sub_type=RuleType(SchemaTypes.INT)),
            RuleType(SchemaTypes.RULESET, lookup='test'),
            RuleType(SchemaTypes.FLOAT)
        ]), 1.23, 0),
    ])
    def test_union_validation_without_sub_validators(self, name: str,
                                                     rtype: typing.Union[
                                                        UnionRuleType,
                                                        RuleType
                                                     ],
                                                     data: Data,
                                                     expected_violation_count: int):  # nopep8 pylint: disable=C0301
        # Unused by test case, however is required by the parameterized library
        del name

        validator = UnionValidator(self.violations)
        validator.validate(self.key, data, self.parent, rtype)

        actual_violation_count = len(self.violations)
        self.assertEqual(expected_violation_count, actual_violation_count)


if __name__ == '__main__':
    unittest.main()
