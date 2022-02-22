import unittest


from .base import BaseWranglerTest
from parameterized import parameterized
from unittest.mock import patch, Mock
from yamler.types import Data, RuleType
from yamler.wranglers import AnyTypeWrangler


class TestAnyTypeWrangler(BaseWranglerTest):

    @parameterized.expand([
        ('is_any_type', {'message': 'test'}, RuleType(type='any'), 0),
        ('is_list_type', [0, 1, 2, 3, 4], RuleType(
            type=list, sub_type=RuleType(type=int)), 1),
    ])
    @patch('yamler.wranglers.Wrangler.wrangle')
    def test_any_type_wrangler(self, name: str, data: Data, rtype: RuleType,
                               expected_wrangler_call_count: int,
                               mock_parent_wrangler: Mock):
        wrangler = AnyTypeWrangler(self.violation_manager)
        wrangler.wrangle(
            key=self.key,
            parent=self.parent,
            data=data,
            rtype=rtype
        )
        self.assertEqual(
            expected_wrangler_call_count,
            mock_parent_wrangler.call_count
        )


if __name__ == '__main__':
    unittest.main()
