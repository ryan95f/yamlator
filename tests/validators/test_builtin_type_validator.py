import unittest

from .base import BaseValidatorTest
from parameterized import parameterized

from yamlator.types import Data, Rule
from yamlator.types import RuleType
from yamlator.types import SchemaTypes
from yamlator.validators import BuiltInTypeValidator


class TestBuiltInTypeValidator(BaseValidatorTest):

    @parameterized.expand([
        ('int_type_match', RuleType(schema_type=SchemaTypes.INT), 1, False),
        ('list_type_match', RuleType(
            schema_type=SchemaTypes.LIST,
            sub_type=RuleType(schema_type=SchemaTypes.INT)
        ), [0, 1, 2], False),
        ('ruleset_type_match', RuleType(schema_type=SchemaTypes.RULESET, lookup='msg'), {
            'message': 'hello'}, False),
        ('float_type_match', RuleType(schema_type=SchemaTypes.FLOAT), 3.14, False),
        ('int_type_mismatch', RuleType(schema_type=SchemaTypes.INT), 'hello', True),
        ('str_type_mismatch', RuleType(schema_type=SchemaTypes.STR), None, True),
        ('float_type_mismatch', RuleType(schema_type=SchemaTypes.FLOAT), 3, True),
        ('bool_type_match_true', RuleType(SchemaTypes.BOOL), True, False),
        ('bool_type_match_false', RuleType(SchemaTypes.BOOL), False, False),
        ('bool_type_mismatch', RuleType(SchemaTypes.BOOL), "true", True),
        ('non_builtin_type', RuleType(SchemaTypes.REGEX, regex='^test'), "test", False),
    ])
    def test_build_in_type_validator(self, name: str, rtype: RuleType, data: Data,
                                     expect_violations: bool):
        validator = BuiltInTypeValidator(self.violations)
        validator.validate(
            key=self.key,
            data=data,
            parent=self.parent,
            rtype=rtype)

        has_violations = len(self.violations) == 1
        self.assertEqual(expect_violations, has_violations)


if __name__ == '__main__':
    unittest.main()
