import unittest
from typing import Type
from parameterized import parameterized

from src.utils import load_yaml_file
from src.utils import load_schema
from src.exceptions import InvalidSchemaFilenameError


class TestLoadYamlFile(unittest.TestCase):
    @parameterized.expand([
        ('with_empty_str', '', ValueError),
        ('with_none', None, ValueError)
    ])
    def test_yaml_file_invalid_filename(self, name: str, filename: str,
                                        expected_exception: Type[Exception]):
        with self.assertRaises(expected_exception):
            load_yaml_file(filename)

    @parameterized.expand([
        ('yaml_file', 'tests/files/hello.yaml')
    ])
    def test_load_yaml_file(self, name: str, filename: str):
        results = load_yaml_file(filename)
        self.assertIsNotNone(results)


class TestLoadSchema(unittest.TestCase):
    @parameterized.expand([
        ('with_empty_str', '', ValueError),
        ('with_none', None, ValueError),
        ('with_yaml_extension', 'test.yaml', InvalidSchemaFilenameError),
        ('with_txt_extension', 'test/test.txt', InvalidSchemaFilenameError),
    ])
    def test_load_schema_with_invalid_filename(self, name: str, filename: str,
                                               expected_exception: Type[Exception]):
        with self.assertRaises(expected_exception):
            load_schema(filename)

    @parameterized.expand([
        ('with_unix_style_path', 'tests/files/hello.ys'),
        ('with_windows_style_path', 'tests\\files\\hello.ys')
    ])
    def test_successfully_load_schema(self, name, filename):
        results = load_schema(filename)
        self.assertIsNotNone(results)


if __name__ == '__main__':
    unittest.main()
