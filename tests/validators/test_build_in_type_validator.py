import unittest

from .base import BaseValidatorTest
from parameterized import parameterized
from src.validators import BuildInTypeValidator
from src.types import Data, RuleType, SchemaTypes


class TestBuildInTypeValidator(BaseValidatorTest):

    @parameterized.expand([
        ('int_type_match', RuleType(type=SchemaTypes.INT), 1, False),
        ('list_type_match', RuleType(
            type=SchemaTypes.LIST,
            sub_type=RuleType(type=SchemaTypes.INT)
        ), [0, 1, 2], False),
        ('ruleset_type_match', RuleType(type=SchemaTypes.RULESET, lookup='msg'), {
            'message': 'hello'}, False),
        ('float_type_match', RuleType(type=SchemaTypes.FLOAT), 3.14, False),
        ('int_type_mismatch', RuleType(type=SchemaTypes.INT), 'hello', True),
        ('str_type_mismatch', RuleType(type=SchemaTypes.STR), None, True),
        ('float_type_mismatch', RuleType(type=SchemaTypes.FLOAT), 3, True),
        ('regex_type', RuleType(SchemaTypes.REGEX, regex='^test'), "test", False),
        ('regex_mismatch', RuleType(SchemaTypes.REGEX, regex='^test'), 100, False),
    ])
    def test_build_in_type_validator(self, name: str, rtype: RuleType, data: Data,
                                     expect_violations: bool):
        validator = BuildInTypeValidator(self.violations)
        validator.validate(
            key=self.key,
            data=data,
            parent=self.parent,
            rtype=rtype)

        has_violations = len(self.violations) == 1
        self.assertEqual(expect_violations, has_violations)


if __name__ == '__main__':
    unittest.main()
