import unittest

from .base import BaseValidatorTest
from parameterized import parameterized
from src.validators import RulesetValidator
from src.types import Data, Rule, RuleType, YamlatorRuleset, SchemaTypes


class TestRuleSetValidator(BaseValidatorTest):
    def setUp(self):
        super().setUp()
        self.instructions = self._create_flat_ruleset()

    def _create_flat_ruleset(self):
        message_ruleset = YamlatorRuleset('message', [
            Rule('message', RuleType(type=SchemaTypes.STR), True),
            Rule('number', RuleType(type=SchemaTypes.INT), False)
        ])
        return {
            'rules': {
                'message': message_ruleset
            }
        }

    @parameterized.expand([
        ('str_type_data', RuleType(type=SchemaTypes.STR), 'hello world', 0),
        ('ruleset_type_with_invalid_data', RuleType(
            type=SchemaTypes.RULESET
        ), 'hello world', 1),
        ('valid_ruleset', RuleType(type=SchemaTypes.RULESET, lookup='message'), {
            'msg': {'message': 'hello', 'number': 1}
        }, 0),
        ('ruleset_with_no_rules', RuleType(type=SchemaTypes.RULESET, lookup='not_real'), {
            'msg': {'message': 'hello', 'number': 1}
        }, 0),
        ('ruleset_with_none_data', RuleType(type=SchemaTypes.RULESET, lookup='not_real'),
            None, 1),
        ('ruleset_with_list_data', RuleType(type=SchemaTypes.RULESET, lookup='not_real'),
            [0, 1, 2], 1),
        ('ruleset_with_str_data', RuleType(type=SchemaTypes.RULESET, lookup='not_real'),
            "hello world", 1),
    ])
    def test_ruleset_validator(self, name: str, rtype: RuleType, data: Data,
                               expected_violation_count: int):
        validator = RulesetValidator(self.violations, self.instructions)
        validator.validate(
            key=self.key,
            data=data,
            parent=self.parent,
            rtype=rtype)

        actual_violation_count = len(self.violations)
        self.assertEqual(expected_violation_count, actual_violation_count)


if __name__ == '__main__':
    unittest.main()
