import unittest

from parameterized import parameterized

from src.utils import load_yamler_ruleset
from src.parser import parse_rulesets
from src.utils import load_yaml_file
from src.exceptions import SchemaParseError
from src.parser import MalformedEnumNameError
from src.parser import MalformedRulesetNameError
from src.parser import MissingRulesError
from src.parser import SchemaSyntaxError


class TestParseRulesets(unittest.TestCase):
    def setUp(self):
        self.valid_yamler_file = './tests/files/hello.yamler'
        self.invalid_yamler_file = './tests/files/hello.yaml'

    def test_parse_with_none_text(self):
        with self.assertRaises(ValueError):
            parse_rulesets(None)

    def test_parse_with_empty_text(self):
        instructions = parse_rulesets('')
        self.assertIsNotNone(instructions)

    def test_parse_with_valid_content(self):
        yamler_content = load_yamler_ruleset(self.valid_yamler_file)
        instructions = parse_rulesets(yamler_content)
        main = instructions.get('main')

        self.assertIsNotNone(instructions)
        self.assertIsNotNone(main)
        self.assertEqual('main', main.name)

    def test_parse_with_invalid_content(self):
        yaml_content = load_yaml_file(self.invalid_yamler_file)
        with self.assertRaises(SchemaSyntaxError):
            parse_rulesets(str(yaml_content))

    @parameterized.expand([
        (
            'with_schema_missing_rules',
            './tests/files/invalid_files/schema_missing_rules.yamler',
            MissingRulesError
        ),
        (
            'with_ruleset_missing_rules',
            './tests/files/invalid_files/schema_missing_rules.yamler',
            MissingRulesError
        ),
        (
            'with_invalid_enum_name',
            './tests/files/invalid_files/invalid_enum_name.yamler',
            MalformedEnumNameError
        ),
        (
            'with_invalid_ruleset_name',
            './tests/files/invalid_files/invalid_ruleset_name.yamler',
            MalformedRulesetNameError
        ),
        (
            'with_ruleset_not_defined',
            './tests/files/invalid_files/missing_defined_ruleset.yamler',
            SchemaParseError
        )
    ])
    def test_parse_syntax_errors(self, name: str, yamler_file_path: str, exception_type):
        yaml_content = load_yaml_file(yamler_file_path)
        with self.assertRaises(exception_type):
            parse_rulesets(str(yaml_content))


if __name__ == '__main__':
    unittest.main()
