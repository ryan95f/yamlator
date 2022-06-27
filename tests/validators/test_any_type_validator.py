import unittest

from .base import BaseValidatorTest

from unittest.mock import Mock
from unittest.mock import patch
from parameterized import parameterized

from yamlator.types import Data
from yamlator.types import RuleType
from yamlator.types import SchemaTypes
from yamlator.validators import AnyTypeValidator


class TestAnyTypeValidator(BaseValidatorTest):

    @parameterized.expand([
        ('is_any_type_with_dict', {'message': 'test'}, RuleType(schema_type=SchemaTypes.ANY), 0),
        ('is_any_type_with_list', [1, 2, 3, 4], RuleType(schema_type=SchemaTypes.ANY), 0),
        ('is_any_type_with_none', None, RuleType(schema_type=SchemaTypes.ANY), 0),
        ('is_any_type_with_str', 100, RuleType(schema_type=SchemaTypes.ANY), 0),
        ('is_list_type', [0, 1, 2, 3, 4], RuleType(
            schema_type=SchemaTypes.LIST, sub_type=RuleType(schema_type=SchemaTypes.INT)), 1),
        ('is_ruleset_type', {'val': 42}, RuleType(
            schema_type=SchemaTypes.RULESET, lookup='value'), 1),
        ('is_int_type', 100, RuleType(schema_type=SchemaTypes.INT), 1)
    ])
    @patch('yamlator.validators.Validator.validate')
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
