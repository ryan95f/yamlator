import unittest

from .base import BaseValidatorTest
from parameterized import parameterized
from unittest.mock import patch, Mock
from src.types import Data, RuleType, SchemaTypes
from src.validators import AnyTypeValidator


class TestAnyTypeValidator(BaseValidatorTest):

    @parameterized.expand([
        ('is_any_type_with_dict', {'message': 'test'}, RuleType(type=SchemaTypes.ANY), 0),
        ('is_any_type_with_list', [1, 2, 3, 4], RuleType(type=SchemaTypes.ANY), 0),
        ('is_any_type_with_none', None, RuleType(type=SchemaTypes.ANY), 0),
        ('is_any_type_with_str', 100, RuleType(type=SchemaTypes.ANY), 0),
        ('is_list_type', [0, 1, 2, 3, 4], RuleType(
            type=SchemaTypes.LIST, sub_type=RuleType(type=SchemaTypes.INT)), 1),
        ('is_ruleset_type', {'val': 42}, RuleType(
            type=SchemaTypes.RULESET, lookup='value'), 1),
        ('is_int_type', 100, RuleType(type=SchemaTypes.INT), 1)
    ])
    @patch('src.validators.Validator.validate')
    def test_any_type_validator(self, name: str, data: Data, rtype: RuleType,
                                expected_validator_call_count: int,
                                mock_parent_validator: Mock):
        validator = AnyTypeValidator(self.violations)
        validator.validate(
            key=self.key,
            parent=self.parent,
            data=data,
            rtype=rtype
        )
        self.assertEqual(
            expected_validator_call_count,
            mock_parent_validator.call_count
        )


if __name__ == '__main__':
    unittest.main()
