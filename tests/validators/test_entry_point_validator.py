"""Test cases for the `EntryPointValidator`

Test cases:
    * `test_entry_point_validator` tests the validator when the entry
       point ruleset is using strict mode to validate if violations
       are being raised
"""


import unittest

from .base import BaseValidatorTest
from parameterized import parameterized

from yamlator.types import Rule
from yamlator.types import RuleType
from yamlator.types import SchemaTypes
from yamlator.types import YamlatorRuleset
from yamlator.validators import EntryPointValidator


def _create_ruleset(is_strict=False):
    rules = [
        Rule('firstName', RuleType(schema_type=SchemaTypes.STR), True),
        Rule('lastName', RuleType(schema_type=SchemaTypes.STR), True),
        Rule('age', RuleType(schema_type=SchemaTypes.INT), False),
    ]
    return YamlatorRuleset('main', rules, is_strict=is_strict)


class TestEntryPointValidator(BaseValidatorTest):
    """Test case for the Entry Point Validator"""

    def setUp(self):
        super().setUp()

        self.parent = '-'
        self.key = 'SCHEMA'
        self.rtype = None

    @parameterized.expand([
        ('not_in_strict_mode_with_extra_fields', {
            'firstName': 'Test',
            'lastName': 'Tester',
            'fullName': 'Test Tester'
        }, _create_ruleset(), 0),
        ('not_in_strict_mode_with_expected_fields', {
            'firstName': 'Test',
            'lastName': 'Tester',
            'age': 42
        }, _create_ruleset(is_strict=False), 0),
        ('in_strict_mode_without_extra_fields', {
            'firstName': 'Test',
            'lastName': 'Tester',
            'age': 42
        }, _create_ruleset(is_strict=True), 0),
        ('in_strict_mode_with_extra_fields', {
            'firstName': 'Test',
            'lastName': 'Tester',
            'fullName': 'Test Tester',
            'job': 'Tester'
        }, _create_ruleset(is_strict=True), 2)
    ])
    def test_entry_point_validator(self, name: str, data: dict,
                                   ruleset: YamlatorRuleset,
                                   expected_violation_count: int):
        # Unused by test case, however is required by the parameterized library
        del name

        validator = EntryPointValidator(self.violations, ruleset)
        validator.validate(self.key, data, self.parent, self.rtype)

        self.assertEqual(expected_violation_count, len(self.violations))


if __name__ == '__main__':
    unittest.main()
