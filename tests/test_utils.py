import unittest
from parameterized import parameterized

from yamler.utils import load_yaml_file
from yamler.utils import load_yamler_ruleset
from yamler.exceptions import InvalidYamlerFilenameError


class TestLoadYamlFile(unittest.TestCase):
    @parameterized.expand([
        ('with_empty_str', ''),
        ('with_none', None)
    ])
    def test_yaml_file_invalid_filename(self, name, filename):
        with self.assertRaises(ValueError):
            load_yaml_file(filename)

    def test_successfully_load_yaml_file(self):
        yaml_file_path = 'tests/files/hello.yaml'
        results = load_yaml_file(yaml_file_path)
        self.assertIsNotNone(results)


class TestLoadYamlerRuleset(unittest.TestCase):
    @parameterized.expand([
        ('with_empty_str', ''),
        ('with_none', None)
    ])
    def test_load_yamler_ruleset_invalid_filename(self, name, filename):
        with self.assertRaises(ValueError):
            load_yamler_ruleset(filename)

    @parameterized.expand([
        ('with_yaml_extension', 'test.yaml'),
        ('with_txt_extension', 'test/test.txt')
    ])
    def test_load_yamler_ruleset_malfromed_filename(self, name, filename):
        with self.assertRaises(InvalidYamlerFilenameError):
            load_yamler_ruleset(filename)

    def test_successfully_load_yamler_file(self):
        yamler_file_path = 'tests/files/hello.yamler'
        results = load_yamler_ruleset(yamler_file_path)
        self.assertIsNotNone(results)


if __name__ == '__main__':
    unittest.main()
