import unittest

from .base import BaseValidatorTest
from parameterized import parameterized

from src.types import Data
from src.types import EnumItem
from src.types import RuleType
from src.types import YamlatorEnum
from src.types import SchemaTypes
from src.validators import EnumTypeValidator


class TestEnumTypeValidator(BaseValidatorTest):
    def setUp(self):
        super().setUp()
        self.enums = {
            'message': YamlatorEnum('message', {
                'success': EnumItem('VALID', 'success'),
                'failure': EnumItem('INVALID', 'failure')
            })
        }

    @parameterized.expand([
        ('with_valid_enum_value', 'success', RuleType(
            type=SchemaTypes.ENUM, lookup='message'), 0),
        ('with_invalid_enum_value', 'not_found',
            RuleType(type=SchemaTypes.ENUM, lookup='message'), 1),
        ('with_empty_str_enum_value', '',
            RuleType(type=SchemaTypes.ENUM, lookup='message'), 1),
        ('with_str_rule_type', 'success', RuleType(type=SchemaTypes.STR), 0),
        ('with_enum_not_found', 'success', RuleType(
            type=SchemaTypes.ENUM, lookup='errors'), 1),
        ('with_non_str_data_type', [0, 1, 2], RuleType(
            type=SchemaTypes.ENUM, lookup='message'), 1),
        ('with_none_type', None, RuleType(
            type=SchemaTypes.ENUM, lookup='message'), 1),
        ('with_int_rule_type', 1, RuleType(SchemaTypes.INT), 0),
        ('with_str_rule_type', 'test', RuleType(SchemaTypes.STR), 0),
        ('with_list_rule_type', [0, 1, 2], RuleType(
            SchemaTypes.LIST, sub_type=RuleType(SchemaTypes.INT)), 0),
    ])
    def test_enum_type_validator(self, name, data: Data, rtype: RuleType,
                                 expected_violation_count: int):
        validator = EnumTypeValidator(self.violations, self.enums)
        validator.validate(
            key=self.key,
            data=data,
            parent=self.parent,
            rtype=rtype)

        violation_count = len(self.violations)
        self.assertEqual(expected_violation_count, violation_count)


if __name__ == '__main__':
    unittest.main()
