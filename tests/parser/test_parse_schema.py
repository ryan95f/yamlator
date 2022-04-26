import unittest

from parameterized import parameterized

from src.utils import load_schema
from src.parser import parse_schema
from src.utils import load_yaml_file
from src.exceptions import SchemaParseError
from src.parser import MalformedEnumNameError
from src.parser import MalformedRulesetNameError
from src.parser import MissingRulesError
from src.parser import SchemaSyntaxError


class TestParseSchema(unittest.TestCase):
    def setUp(self):
        self.valid_schema_file = './tests/files/hello.ys'
        self.invalid_schema_file = './tests/files/hello.yaml'

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
            SchemaParseError
        ),
        (
            'with_invalid_schema_syntax',
            './tests/files/hello.yaml',
            SchemaSyntaxError
        )
    ])
    def test_parse_syntax_errors(self, name: str, schema_file_path: str, exception_type):
        schema_content = load_yaml_file(schema_file_path)
        with self.assertRaises(exception_type):
            parse_schema(str(schema_content))


if __name__ == '__main__':
    unittest.main()
