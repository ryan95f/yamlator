import unittest
from yamler.utils import load_yaml_file
from yamler.utils import load_yamler_ruleset


class TestLoadYamlFile(unittest.TestCase):
    def test_yaml_file_invalid_filename(self):
        filenames = [None, '']

        for filename in filenames:
            with self.assertRaises(ValueError):
                load_yaml_file(filename)

    def test_successfully_load_yaml_file(self):
        yaml_file_path = 'tests/files/hello.yaml'
        results = load_yaml_file(yaml_file_path)
        self.assertIsNotNone(results)


class TestLoadYamlerRuleset(unittest.TestCase):
    def test_load_yamler_ruleset_invalid_filename(self):
        filenames = [None, '']

        for filename in filenames:
            with self.assertRaises(ValueError):
                load_yamler_ruleset(filename)

    def test_successfully_load_yamler_file(self):
        yamler_file_path = 'tests/files/hello.yamler'
        results = load_yamler_ruleset(yamler_file_path)
        self.assertIsNotNone(results)


if __name__ == '__main__':
    unittest.main()
