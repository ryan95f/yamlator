import unittest

from .base import BaseValidatorTest
from parameterized import parameterized
from src.validators import RulesetValidator
from src.types import Data, Rule, RuleType, YamlerRuleset, SchemaTypes


class TestRuleSetValidator(BaseValidatorTest):
    def setUp(self):
        super().setUp()
        self.instructions = self._create_flat_ruleset()

    def _create_flat_ruleset(self):
        message_ruleset = YamlerRuleset('message', [
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
        validator = RulesetValidator(self.violations, self.instructions)
        validator.validate(
            key=self.key,
            data=data,
            parent=self.parent,
            rtype=rtype)

        has_violations = len(self.violations) == 1
        self.assertEqual(expect_violations, has_violations)


if __name__ == '__main__':
    unittest.main()
