import unittest

from .base import BaseValidatorTest
from parameterized import parameterized
from src.validators import EnumTypeValidator
from src.types import Data, EnumItem, RuleType, YamlatorEnum, SchemaTypes


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
        ('with_str_rule_type', 'success', RuleType(type=SchemaTypes.STR), 0),
        ('with_enum_not_found', 'success', RuleType(
            type=SchemaTypes.ENUM, lookup='errors'), 1),
        ('with_non_str_data_type', [0, 1, 2], RuleType(
            type=SchemaTypes.ENUM, lookup='message'), 1)
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
