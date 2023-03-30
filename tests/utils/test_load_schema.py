"""Test case for the load_schema function

Test cases:
    * `test_load_schema_with_invalid_filename` tests loading a Yamlator
       schema with a range of invalid arguments
    * `test_successfully_load_schema` tests loading a valid Yamlator schema
"""

import unittest

from typing import Type
from parameterized import parameterized

from yamlator.utils import load_schema
from yamlator.exceptions import InvalidSchemaFilenameError

from tests.cmd import constants


class TestLoadSchema(unittest.TestCase):
    """Test cases for the Load Schema function"""

    @parameterized.expand([
        ('with_empty_str', constants.EMPTY_PATH, ValueError),
        ('with_none', constants.NONE_PATH, ValueError),
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
        ('with_unix_style_path', 'tests/files/valid/valid.ys'),
        ('with_windows_style_path', 'tests\\files\\valid\\valid.ys')
    ])
    def test_successfully_load_schema(self, name, filename):
        # Unused by test case, however is required by the parameterized library
        del name

        results = load_schema(filename)
        self.assertIsNotNone(results)


if __name__ == '__main__':
    unittest.main()
