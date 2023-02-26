"""Test cases for the fetch_schema_path function"""


import unittest

from typing import Any
from parameterized import parameterized

from yamlator.parser.loaders import fetch_schema_path


class TestFetchSchemaPath(unittest.TestCase):
    """Test cases for the fetch_schema_path function"""

    @parameterized.expand([
        ('with_none_str', None, ValueError),
        ('with_empty_str', '', ValueError),
        ('with_none_str_path', ['./path/file.ys'], TypeError),
    ])
    def test_fetch_path_with_invalid_paths(self, name: str, schema_path: Any,
                                           expected_exception: Exception):
        # Unused by test case, however is required by the parameterized library
        del name

        with self.assertRaises(expected_exception):
            fetch_schema_path(schema_path)

    @parameterized.expand([
        ('with_backslash_path', '\\awesome\\path\\test.ys', 'awesome/path'),
        ('with_forward_slash_path', '/awesome/path/test.ys', 'awesome/path'),
        ('with_schema_only', 'test.ys', '.'),
        ('with_parent_directory', '../test.ys', '..'),
        ('with_parent_directory_mixed_in_path', 'awesome/test/../wow.ys',
            'awesome/test/..')
    ])
    def test_fetch_path_with_valid_paths(self, name: str, schema_path: str,
                                         expected_path: str):
        # Unused by test case, however is required by the parameterized library
        del name

        actual_path = fetch_schema_path(schema_path)
        self.assertEqual(expected_path, actual_path)


if __name__ == '__main__':
    unittest.main()
