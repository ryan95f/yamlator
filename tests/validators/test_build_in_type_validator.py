import unittest

from .base import BaseWranglerTest
from parameterized import parameterized
from yamler.validators import BuildInTypeValidator
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
    def test_build_in_type_validator(self, name: str, rtype: RuleType, data: Data,
                                     expect_violations: bool):
        wrangler = BuildInTypeValidator(self.violations)
        wrangler.validate(
            key=self.key,
            data=data,
            parent=self.parent,
            rtype=rtype)

        has_violations = len(self.violations) == 1
        self.assertEqual(expect_violations, has_violations)


if __name__ == '__main__':
    unittest.main()
