import unittest

from .base import BaseWranglerTest
from parameterized import parameterized
from yamler.validators import RuleSetValidator
from yamler.types import Data, Rule, RuleType, YamlerRuleSet, SchemaTypes


class TestRuleSetWrangler(BaseWranglerTest):
    def setUp(self):
        super().setUp()
        self.instructions = self._create_flat_ruleset()

    def _create_flat_ruleset(self):
        message_ruleset = YamlerRuleSet('message', [
            Rule('message', RuleType(type=SchemaTypes.STR), True),
            Rule('number', RuleType(type=SchemaTypes.INT), False)
        ])
        return {
            'rules': {
                'message': message_ruleset
            }
        }

    @parameterized.expand([
        ('str_type_data', RuleType(type=SchemaTypes.STR), 'hello world', False),
        ('ruleset_type_with_invalid_data', RuleType(
            type=SchemaTypes.RULESET
        ), 'hello world', True),
        ('valid_ruleset', RuleType(type=SchemaTypes.RULESET, lookup='message'), {
            'msg': {'message': 'hello', 'number': 1}
        }, False),
        ('ruleset_with_no_rules', RuleType(type=SchemaTypes.RULESET, lookup='not_real'), {
            'msg': {'message': 'hello', 'number': 1}
        }, False)
    ])
    def test_ruleset_validator(self, name: str, rtype: RuleType, data: Data,
                               expect_violations: bool):
        wrangler = RuleSetValidator(self.violations, self.instructions)
        wrangler.validate(
            key=self.key,
            data=data,
            parent=self.parent,
            rtype=rtype)

        has_violations = len(self.violations) == 1
        self.assertEqual(expect_violations, has_violations)


if __name__ == '__main__':
    unittest.main()
