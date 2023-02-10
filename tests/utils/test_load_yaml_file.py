"""Test case for the load_yaml_file function

Test cases:
    * `test_yaml_file_invalid_filename` tests loading the YAML file with a range
       of invalid arguments
    * `test_load_yaml_file` tests loading a valid YAML file
"""

import unittest

from typing import Type
from parameterized import parameterized

from yamlator.utils import load_yaml_file


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
        ('yaml_file', 'tests/files/valid/valid.yaml')
    ])
    def test_load_yaml_file(self, name: str, filename: str):
        # Unused by test case, however is required by the parameterized library
        del name

        results = load_yaml_file(filename)
        self.assertIsNotNone(results)


if __name__ == '__main__':
    unittest.main()
