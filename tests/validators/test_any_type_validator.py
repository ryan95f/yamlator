import unittest

from .base import BaseValidatorTest
from parameterized import parameterized
from unittest.mock import patch, Mock
from src.types import Data, RuleType, SchemaTypes
from src.validators import AnyTypeValidator


class TestAnyTypeValidator(BaseValidatorTest):

    @parameterized.expand([
        ('is_any_type', {'message': 'test'}, RuleType(type=SchemaTypes.ANY), 0),
        ('is_list_type', [0, 1, 2, 3, 4], RuleType(
            type=list, sub_type=RuleType(type=SchemaTypes.INT)), 1),
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
