import unittest

from .base import BaseWranglerTest
from parameterized import parameterized
from yamler.wranglers import BuildInTypeWrangler
from yamler.types import Data, RuleType, SchemaTypes


class TestBuildInTypeWrangler(BaseWranglerTest):

    @parameterized.expand([
        ('int_type_match', RuleType(type=SchemaTypes.INT), 1, False),
        ('list_type_match', RuleType(
            type=SchemaTypes.LIST,
            sub_type=RuleType(type=SchemaTypes.INT)
        ), [0, 1, 2], False),
        ('ruleset_type_match', RuleType(type=SchemaTypes.RULESET, lookup='msg'), {
            'message': 'hello'}, False),
        ('int_type_mismatch', RuleType(type=SchemaTypes.INT), 'hello', True),
        ('str_type_mismatch', RuleType(type=SchemaTypes.STR), None, True)
    ])
    def test_build_in_type_wrangler(self, name: str, rtype: RuleType, data: Data,
                                    expect_violations: bool):
        wrangler = BuildInTypeWrangler(self.violation_manager)
        wrangler.wrangle(
            key=self.key,
            data=data,
            parent=self.parent,
            rtype=rtype)

        violations = self.violation_manager.violations
        has_violations = len(violations) == 1
        self.assertEqual(expect_violations, has_violations)


if __name__ == '__main__':
    unittest.main()
