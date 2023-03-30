"""Test cases for the resolve_unknown_types function"""

import unittest

from parameterized import parameterized

from yamlator.types import RuleType
from yamlator.types import SchemaTypes
from yamlator.types import YamlatorEnum
from yamlator.types import YamlatorRuleset
from yamlator.parser.loaders import resolve_unknown_types
from yamlator.exceptions import ConstructNotFoundError


class TestResolveUnknownTypes(unittest.TestCase):
    """Test cases for the resolve_unknown_types function"""

    @parameterized.expand([
        ('with_unknown_types_is_none', None, {}, {}, ValueError),
        ('with_wrong_type_for_unknown_types', {}, {}, {}, TypeError),
        ('with_ruleset_is_none', [], None, {}, ValueError),
        ('with_enum_is_none', [], {}, None, ValueError),
        ('with_ruleset_and_enum_is_none', [], None, None, ValueError),
        ('with_ruleset_wrong_type', [], [], {}, TypeError),
        ('with_enum_wrong_type', [], {}, [], TypeError),
        ('with_ruleset_and_enum_wrong_type', [], [], [], TypeError),
    ])
    def test_resolve_unknown_types_invalid_parameters(
            self, name: str, unknown_types: list,
            rulesets: dict, enums: dict, expected_exception: Exception):
        # Unused by test case, however is required by the parameterized library
        del name

        with self.assertRaises(expected_exception):
            resolve_unknown_types(unknown_types, rulesets, enums)

    def test_resolve_unknown_types_unknown_construct_type(self):
        unknown_types = [
            RuleType(SchemaTypes.UNKNOWN, lookup='Hello')
        ]

        with self.assertRaises(ConstructNotFoundError):
            resolve_unknown_types(unknown_types, {}, {})

    def test_resolve_unknown_types(self):
        unknown_types = [
            RuleType(SchemaTypes.UNKNOWN, lookup='Hello'),
            RuleType(SchemaTypes.UNKNOWN, lookup='Status'),
            RuleType(SchemaTypes.UNKNOWN, lookup='Users')
        ]

        rulesets = {
            'Hello': YamlatorRuleset('Hello', []),
            'Users': YamlatorRuleset('Users', [])
        }

        enums = {
            'Status': YamlatorEnum('Status', {})
        }

        resolve_unknown_types(unknown_types.copy(), rulesets, enums)

        # Check that the unknown types have been resolved
        self.assertEqual(SchemaTypes.RULESET, unknown_types[0].schema_type)
        self.assertEqual(SchemaTypes.ENUM, unknown_types[1].schema_type)
        self.assertEqual(SchemaTypes.RULESET, unknown_types[2].schema_type)


if __name__ == '__main__':
    unittest.main()
