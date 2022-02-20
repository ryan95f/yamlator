from turtle import rt
import unittest

from unittest.mock import patch, Mock
from parameterized import parameterized
from yamler.types import Data, RuleType

from .base import BaseWranglerTest
from yamler.wranglers import MapWrangler


class TestMapWrangler(BaseWranglerTest):
    @parameterized.expand([
        ('with_str_rule_type', 'hello', RuleType(type=str), 1),
        ('with_ruleset_rule_type', {'message': 'hello'}, RuleType(
            type='ruleset', lookup='message'), 1),
        ('with_map_rule_type', {'message1': 'wow', 'message2': 'wow'}, RuleType(
            type=dict, sub_type=RuleType(type=str)
        ), 2),
        ('with_nested_map_rule_type', {'hello': {'message1': 'test'}}, RuleType(
            type=dict, sub_type=RuleType(type=dict, sub_type=RuleType(type=str))
        ), 1)
    ])
    @patch('yamler.wranglers.Wrangler.wrangle')
    def test_map_wrangler(self, name: str, data: Data, rtype: RuleType,
                          expected_parent_call_count: int, mock_parent_wrangler: Mock):
        wrangler = MapWrangler(self.violation_manager)
        wrangler.wrangle(
            key=self.key,
            data=data,
            parent=self.parent,
            rtype=rtype
        )
        self.assertEqual(expected_parent_call_count, mock_parent_wrangler.call_count)


if __name__ == '__main__':
    unittest.main()
