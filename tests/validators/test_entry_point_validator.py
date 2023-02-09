"""Test cases for the `EntryPointValidator`

Test cases:
    * `test_entry_point_validator` tests the validator when the entry
       point ruleset is using strict mode to validate if violations
       are being raised
"""


import unittest

from .base import BaseValidatorTest
from unittest.mock import Mock
from unittest.mock import patch
from parameterized import parameterized

from yamlator.types import Rule
from yamlator.types import Data
from yamlator.types import RuleType
from yamlator.utils import KEYLESS_RULE_DIRECTIVE
from yamlator.types import SchemaTypes
from yamlator.types import YamlatorRuleset
from yamlator.validators import EntryPointValidator


def create_person_ruleset(is_strict=False):
    rules = [
        Rule('firstName', RuleType(schema_type=SchemaTypes.STR), True),
        Rule('lastName', RuleType(schema_type=SchemaTypes.STR), True),
        Rule('age', RuleType(schema_type=SchemaTypes.INT), False),
    ]
    return YamlatorRuleset('main', rules, is_strict=is_strict)


def create_ruleset(rules: 'list[Rule]', is_strict=False):
    return YamlatorRuleset('main', rules, is_strict)


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
        }, create_person_ruleset(), 0, 3),
        ('not_in_strict_mode_with_expected_fields', {
            'firstName': 'Test',
            'lastName': 'Tester',
            'age': 42
        }, create_person_ruleset(is_strict=False), 0, 3),
        ('in_strict_mode_without_extra_fields', {
            'firstName': 'Test',
            'lastName': 'Tester',
            'age': 42
        }, create_person_ruleset(is_strict=True), 0, 3),
        ('in_strict_mode_with_extra_fields', {
            'firstName': 'Test',
            'lastName': 'Tester',
            'fullName': 'Test Tester',
            'job': 'Tester'
        }, create_person_ruleset(is_strict=True), 2, 3),
        ('with_no_rules', {'hello': 0}, create_ruleset([]), 0, 0),
        ('with_keyless_directive_rule', [1, 2, 3], create_ruleset([
            Rule(KEYLESS_RULE_DIRECTIVE, RuleType(schema_type=SchemaTypes.LIST,
                 sub_type=RuleType(SchemaTypes.INT)), True),
        ]), 0, 1),
        ('with_single_rule', {'hello': 23}, create_ruleset([
            Rule('hello', RuleType(schema_type=SchemaTypes.INT), True),
        ]), 0, 1),
        ('with_no_rules_or_data', {}, create_ruleset([]), 0, 0)
    ])
    @patch('yamlator.validators.base_validator.Validator.validate')
    def test_entry_point_validator(self, name: str, data: Data,
                                   ruleset: YamlatorRuleset,
                                   expected_violation_count: int,
                                   expected_parent_call_count: int,
                                   mock_parent_validator: Mock):
        # Unused by test case, however is required by the parameterized library
        del name

        validator = EntryPointValidator(self.violations, ruleset)
        validator.validate(self.key, data, self.parent, self.rtype)

        self.assertEqual(expected_violation_count, len(self.violations))
        self.assertEqual(expected_parent_call_count,
                         mock_parent_validator.call_count)


if __name__ == '__main__':
    unittest.main()
