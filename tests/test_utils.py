"""Test cases for the Yamlator utilities. This contains tests
for the `load_yaml_file` and `load_schema` functions

Test cases:
    * `test_yaml_file_invalid_filename` tests loading the YAML file with a range
       of invalid arguments
    * `test_load_yaml_file` tests loading a valid YAML file
    * `test_load_schema_with_invalid_filename` tests loading a Yamlator
       schema with a range of invalid arguments
    * `test_successfully_load_schema` tests loading a valid Yamlator schema
"""


import unittest

from typing import Type
from parameterized import parameterized

from yamlator.utils import load_yaml_file
from yamlator.utils import load_schema
from yamlator.exceptions import InvalidSchemaFilenameError


class TestLoadYamlFile(unittest.TestCase):
    """Test cases for the Load Yaml File function"""

    @parameterized.expand([
        ('with_empty_str', '', ValueError),
        ('with_none', None, ValueError)
    ])
    def test_yaml_file_invalid_filename(self, name: str, filename: str,
                                        expected_exception: Type[Exception]):
        # Unused by test case, however is required by the parameterized library
        del name

        with self.assertRaises(expected_exception):
            load_yaml_file(filename)

    @parameterized.expand([
        ('yaml_file', 'tests/files/example/example.yaml')
    ])
    def test_load_yaml_file(self, name: str, filename: str):
        # Unused by test case, however is required by the parameterized library
        del name

        results = load_yaml_file(filename)
        self.assertIsNotNone(results)


class TestLoadSchema(unittest.TestCase):
    """Test cases for the Load Schema function"""

    @parameterized.expand([
        ('with_empty_str', '', ValueError),
        ('with_none', None, ValueError),
        ('with_yaml_extension', 'test.yaml', InvalidSchemaFilenameError),
        ('with_txt_extension', 'test/test.txt', InvalidSchemaFilenameError),
    ])
    def test_load_schema_with_invalid_filename(self, name: str, filename: str,
                                               expected_exception: Type[Exception]):  # nopep8 pylint: disable=C0301
        # Unused by test case, however is required by the parameterized library
        del name

        with self.assertRaises(expected_exception):
            load_schema(filename)

    @parameterized.expand([
        ('with_unix_style_path', 'tests/files/example/example.ys'),
        ('with_windows_style_path', 'tests\\files\\example\\example.ys')
    ])
    def test_successfully_load_schema(self, name, filename):
        # Unused by test case, however is required by the parameterized library
        del name

        results = load_schema(filename)
        self.assertIsNotNone(results)


if __name__ == '__main__':
    unittest.main()
