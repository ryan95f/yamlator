"""Test cases for the `parse_schema` function

Test cases:
    * `test_parse_with_none_text` tests the parse function when the
       content is `None`
    * `test_parse_with_empty_text` tests the parse function when the
       schema is an empty string
    * `test_parse_with_valid_content` tests the parse function with
       valid content
    * `test_parse_syntax_errors` tests the parse function with a range
       of different syntax errors using multiple test files
"""


import unittest

from typing import Type
from parameterized import parameterized

from yamlator.utils import load_schema
from yamlator.parser import parse_schema
from yamlator.utils import load_yaml_file
from yamlator.parser import MalformedEnumNameError
from yamlator.parser import MalformedRulesetNameError
from yamlator.parser import MissingRulesError
from yamlator.parser import SchemaSyntaxError


class TestParseSchema(unittest.TestCase):
    """Tests the parse schema function"""

    def setUp(self):
        self.valid_schema_file = './tests/files/example/example.ys'
        self.invalid_schema_file = './tests/files/example/example.yaml'

    def test_parse_with_none_text(self):
        with self.assertRaises(ValueError):
            parse_schema(None)

    def test_parse_with_empty_text(self):
        instructions = parse_schema('')
        self.assertIsNotNone(instructions)

    def test_parse_with_valid_content(self):
        schema_content = load_schema(self.valid_schema_file)
        instructions = parse_schema(schema_content)
        main = instructions.get('main')

        self.assertIsNotNone(instructions)
        self.assertIsNotNone(main)
        self.assertEqual('main', main.name)

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
            SchemaSyntaxError
        ),
        (
            'with_invalid_schema_syntax',
            './tests/files/example/example.yaml',
            SchemaSyntaxError
        )
    ])
    def test_parse_syntax_errors(self, name: str, schema_file_path: str,
                                 exception_type: Type[Exception]):
        # Unused by test case, however is required by the parameterized library
        del name

        schema_content = load_yaml_file(schema_file_path)
        with self.assertRaises(exception_type):
            parse_schema(str(schema_content))


if __name__ == '__main__':
    unittest.main()
