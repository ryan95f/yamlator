"""Test cases for the `MapValidator`

Test cases:
    * `test_map_validator` tests validating maps with a variety
       of different types of maps, including nested maps and
       different rule types
"""


import unittest

from .base import BaseValidatorTest

from unittest.mock import patch
from unittest.mock import Mock
from parameterized import parameterized

from yamlator.types import Data
from yamlator.types import RuleType
from yamlator.types import SchemaTypes
from yamlator.validators import MapValidator


class TestMapValidator(BaseValidatorTest):
    """Test cases for the Map Validator"""

    @parameterized.expand([
        ('with_str_rule_type', 'hello',
            RuleType(schema_type=SchemaTypes.STR), 1, 0),
        ('with_ruleset_rule_type', {'message': 'hello'},
            RuleType(schema_type=SchemaTypes.RULESET, lookup='message'),
            1, 0),
        ('with_map_rule_type', {'message1': 'wow', 'message2': 'wow'},
            RuleType(schema_type=SchemaTypes.MAP,
                     sub_type=RuleType(schema_type=SchemaTypes.STR)),
            2, 0),
        ('with_nested_map_rule_type', {'hello': {'message1': 'test'}},
            RuleType(schema_type=SchemaTypes.MAP,
                     sub_type=RuleType(
                            schema_type=SchemaTypes.MAP,
                            sub_type=RuleType(schema_type=SchemaTypes.STR))),
            1, 0),
        ('with_map_rule_none_data', None,
            RuleType(schema_type=SchemaTypes.MAP,
                     sub_type=RuleType(schema_type=SchemaTypes.STR)),
            0, 1),
        ('with_map_rule_str_data', 'hello world',
            RuleType(schema_type=SchemaTypes.MAP,
                     sub_type=RuleType(schema_type=SchemaTypes.STR)),
            0, 1),
        ('with_map_rule_list_data', [0, 1, 2],
            RuleType(schema_type=SchemaTypes.MAP,
                     sub_type=RuleType(schema_type=SchemaTypes.STR)),
            0, 1),
    ])
    @patch('yamlator.validators.base_validator.Validator.validate')
    def test_map_validator(self, name: str, data: Data, rtype: RuleType,
                           expected_parent_call_count: int,
                           expected_violation_count: int,
                           mock_parent_validator: Mock):
        # Unused by test case, however is required by the parameterized library
        del name

        validator = MapValidator(self.violations)
        validator.validate(
            key=self.key,
            data=data,
            parent=self.parent,
            rtype=rtype
        )
        self.assertEqual(expected_parent_call_count,
                         mock_parent_validator.call_count)

        actual_violation_count = len(self.violations)
        self.assertEqual(expected_violation_count, actual_violation_count)


if __name__ == '__main__':
    unittest.main()
