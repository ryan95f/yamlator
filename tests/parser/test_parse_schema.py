"""Test cases for the parse_schema function

Test cases:
    * `test_parse_with_none_text` tests the parse function when the
       content is `None` raises a ValueError
    * `test_parse_with_empty_text` tests the parse function when the
       schema is an empty string still returns an object
    * `test_parse_with_valid_content` tests the parse function with
       valid content returns the expected rule count
    * `test_parse_syntax_errors` tests the parse function with a range
       of different syntax errors using multiple test files
"""


import unittest

from typing import Type
from parameterized import parameterized

from yamlator.utils import load_schema
from yamlator.parser import parse_schema
from yamlator.parser import MalformedEnumNameError
from yamlator.parser import MalformedRulesetNameError
from yamlator.parser import MissingRulesError
from yamlator.parser import SchemaParseError
from yamlator.parser import SchemaSyntaxError


class TestParseSchema(unittest.TestCase):
    """Tests the parse schema function"""

    def test_parse_with_none_text(self):
        with self.assertRaises(ValueError):
            parse_schema(None)

    def test_parse_with_empty_text(self):
        instructions = parse_schema('')
        self.assertIsNotNone(instructions)

    @parameterized.expand([
        ('with_root_key_schema', './tests/files/valid/valid.ys', 4),
        ('with_keyless_schema', './tests/files/valid/keyless_directive.ys', 1),
        ('with_keyless_schema',
         './tests/files/valid/keyless_and_standard_rules.ys', 2),
    ])
    def test_parse_with_valid_content(self, name: str, schema_path: str,
                                      expected_schema_rule_count: int):
        # Unused by test case, however is required by the parameterized library
        del name

        schema_content = load_schema(schema_path)
        instructions = parse_schema(schema_content)
        main = instructions.get('main')

        self.assertIsNotNone(instructions)
        self.assertIsNotNone(main)
        self.assertEqual('main', main.name)
        self.assertEqual(expected_schema_rule_count, len(main.rules))

    @parameterized.expand([
        (
            'with_schema_missing_rules',
            './tests/files/invalid_files/schema_missing_rules.ys',
            MissingRulesError
        ),
        (
            'with_ruleset_missing_rules',
            './tests/files/invalid_files/schema_missing_rules.ys',
            MissingRulesError
        ),
        (
            'with_invalid_enum_name',
            './tests/files/invalid_files/invalid_enum_name.ys',
            MalformedEnumNameError
        ),
        (
            'with_invalid_ruleset_name',
            './tests/files/invalid_files/invalid_ruleset_name.ys',
            MalformedRulesetNameError
        ),
        (
            'with_ruleset_not_defined',
            './tests/files/invalid_files/missing_defined_ruleset.ys',
            SchemaParseError
        ),
        (
            'union_with_nested_union',
            './tests/files/invalid_files/nested_union.ys',
            SchemaParseError
        ),
        (
            'with_invalid_rule_syntax',
            './tests/files/invalid_files/invalid_syntax.ys',
            SchemaSyntaxError
        )
    ])
    def test_parse_syntax_errors(self, name: str, schema_file_path: str,
                                 exception_type: Type[Exception]):
        # Unused by test case, however is required by the parameterized library
        del name

        schema_content = load_schema(schema_file_path)
        with self.assertRaises(exception_type):
            parse_schema(schema_content)


if __name__ == '__main__':
    unittest.main()
