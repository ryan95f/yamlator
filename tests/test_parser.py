import unittest
from lark.exceptions import UnexpectedCharacters
from yamler.parser import YamlerParser
from yamler.utils import load_yamler_ruleset
from yamler.utils import load_yaml_file


class TestYamlerParser(unittest.TestCase):
    def setUp(self):
        self.valid_yamler_file = "./tests/files/hello.yamler"
        self.invalid_yamler_file = "./tests/files/hello.yaml"
        self.parser = YamlerParser()

    def test_parse_with_none_text(self):
        with self.assertRaises(ValueError):
            self.parser.parse(None)

    def test_parse_with_empty_text(self):
        instructions = self.parser.parse("")
        self.assertIsNotNone(instructions)

    def test_parse_with_valid_content(self):
        yamler_content = load_yamler_ruleset(self.valid_yamler_file)
        instructions = self.parser.parse(yamler_content)
        main = instructions.get('name')

        self.assertIsNotNone(instructions)
        self.assertIsNotNone(main)
        self.assertEqual("main", main)

    def test_parse_with_invalid_content(self):
        yaml_content = load_yaml_file(self.invalid_yamler_file)
        with self.assertRaises(UnexpectedCharacters):
            self.parser.parse(str(yaml_content))


if __name__ == '__main__':
    unittest.main()
