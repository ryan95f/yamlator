"""Test cases for the ImportStatement class"""

import unittest

from parameterized import parameterized
from yamlator.types import ImportStatement


class TestImportStatement(unittest.TestCase):
    """Test cases for the ImportStatement class"""

    @parameterized.expand([
        ('with_none_item', None, './test', ValueError),
        ('with_item_as_an_empty_string', '', './test', ValueError),
        ('with_item_wrong_type', ['Test'], './test.ys', TypeError),
        ('with_none_path', 'Test', None, ValueError),
        ('with_path_as_an_empty_string', 'Test', '', ValueError),
        ('with_item_wrong_type', 'Test', ['./test.ys'], TypeError),
    ])
    def test_import_statements_invalid_params(self, name: str, item: str,
                                              path: str,
                                              expected_exception: Exception):
        # Unused by test case, however is required by the parameterized library
        del name

        with self.assertRaises(expected_exception):
            ImportStatement(item, path)


if __name__ == '__main__':
    unittest.main()
