import unittest

from unittest.mock import Mock, patch
from parameterized import parameterized
from yamler.types import Data, RuleType
from yamler.wranglers import OptionalWrangler
from yamler.violations import ViolationManager


class TestOptionalWrangler(unittest.TestCase):
    def setUp(self):
        self.parent = '-'
        self.key = 'msg'
        self.rtype = RuleType(type=str)
        self.violation_manager = ViolationManager

    @parameterized.expand([
        ('with_optional_data', False, 'hello world', 1),
        ('with_required_data', True, 'Hello World', 1),
        ('with_optional_and_none_data', False, None, 0),
        ('with_required_and_none_data', True, None, 1),
    ])
    @patch('yamler.wranglers.Wrangler.wrangle')
    def test_optional_wrangler(self, name: str, is_required: bool, data: Data,
                               next_wrangler_call_count: int, mock_parent_wrangler: Mock):
        wrangler = OptionalWrangler(self.violation_manager)
        wrangler.wrangle(
            key=self.key,
            data=data,
            parent=self.parent,
            rtype=self.rtype,
            is_required=is_required)
        self.assertEqual(next_wrangler_call_count, mock_parent_wrangler.call_count)


if __name__ == '__main__':
    unittest.main()
