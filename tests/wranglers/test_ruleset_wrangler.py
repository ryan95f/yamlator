import unittest

from .base import BaseWranglerTest
from parameterized import parameterized
from yamler.wranglers import RuleSetWrangler
from yamler.types import Data, Rule, RuleType


class TestRuleSetWrangler(BaseWranglerTest):
    def setUp(self):
        super().setUp()
        self.instructions = self._create_flat_ruleset()

    def _create_flat_ruleset(self):
        return {
            'rules': {
                'message': {
                    'rules': [
                        Rule('message', RuleType(type=str), True),
                        Rule('number', RuleType(type=int), False)
                    ]
                },
            }
        }

    @parameterized.expand([
        ('str_type_data', RuleType(type=str), 'hello world', False),
        ('ruleset_type_with_invalid_data', RuleType(type='ruleset'), 'hello world', True),
        ('valid_ruleset', RuleType(type='ruleset', lookup='message'), {
            'msg': {'message': 'hello', 'number': 1}
        }, False),
        ('ruleset_with_no_rules', RuleType(type='ruleset', lookup='not_real'), {
            'msg': {'message': 'hello', 'number': 1}
        }, False)
    ])
    def test_rule_set_wrangler(self, name: str, rtype: RuleType, data: Data,
                               expect_violations: bool):
        wrangler = RuleSetWrangler(self.violation_manager, self.instructions)
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
