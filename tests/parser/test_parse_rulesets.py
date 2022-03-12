import unittest

from yamler.parser import parse_rulesets
from yamler.utils import load_yamler_ruleset
from yamler.utils import load_yaml_file
from lark.exceptions import UnexpectedCharacters


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
        with self.assertRaises(UnexpectedCharacters):
            parse_rulesets(str(yaml_content))


if __name__ == '__main__':
    unittest.main()
