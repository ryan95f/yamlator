"""Test cases for the `EnumTypeValidator`

Test cases:
    * `test_enum_type_validator` tests the validator with a variety of
       different enum configurations and rule types
"""


import unittest

from .base import BaseValidatorTest
from parameterized import parameterized

from yamlator.types import Data
from yamlator.types import EnumItem
from yamlator.types import RuleType
from yamlator.types import YamlatorEnum
from yamlator.types import SchemaTypes
from yamlator.validators import EnumTypeValidator


string_enum = {
    'message': YamlatorEnum('message', {
        'success': EnumItem('VALID', 'success'),
        'failure': EnumItem('INVALID', 'failure')
    })
}

int_enum = {
    'message': YamlatorEnum('message', {
        0: EnumItem('VALID', 0),
        1: EnumItem('INVALID', 1)
    })
}

float_enum = {
    'digits': YamlatorEnum('digits', {
        3.142: EnumItem('PI', 3.142),
    })
}


class TestEnumTypeValidator(BaseValidatorTest):
    """Test cases for Enum Type Validator"""

    @parameterized.expand([
        ('with_str_enum_valid_value', 'success',
            RuleType(schema_type=SchemaTypes.ENUM, lookup='message'),
            string_enum, 0),
        ('with_str_enum_invalid_value', 'not_found',
            RuleType(schema_type=SchemaTypes.ENUM, lookup='message'),
            string_enum, 1),
        ('with_str_enum_empty_str_value', '',
            RuleType(schema_type=SchemaTypes.ENUM, lookup='message'),
            string_enum, 1),
        ('with_str_rule_type', 'success',
            RuleType(schema_type=SchemaTypes.STR), string_enum, 0),
        ('with_enum_not_found', 'success',
            RuleType(schema_type=SchemaTypes.ENUM, lookup='errors'),
            string_enum, 1),
        ('with_non_str_data_type', [0, 1, 2],
            RuleType(schema_type=SchemaTypes.ENUM, lookup='message'),
            string_enum, 1),
        ('with_none_type', None,
            RuleType(schema_type=SchemaTypes.ENUM, lookup='message'),
            string_enum, 1),
        ('with_int_rule_type', 1, RuleType(SchemaTypes.INT), string_enum, 0),
        ('with_str_rule_type', 'test', RuleType(SchemaTypes.STR),
            string_enum, 0),
        ('with_list_rule_type', [0, 1, 2],
            RuleType(SchemaTypes.LIST, sub_type=RuleType(SchemaTypes.INT)),
            string_enum, 0),
        ('with_int_enum_valid_value', 1,
            RuleType(schema_type=SchemaTypes.ENUM, lookup='message'),
            int_enum, 0),
        ('with_int_enum_invalid_value', 100,
            RuleType(schema_type=SchemaTypes.ENUM, lookup='message'),
            int_enum, 1),
        ('with_int_enum_invalid_str_value', '1',
            RuleType(schema_type=SchemaTypes.ENUM, lookup='message'),
            int_enum, 1),
        ('with_float_enum_valid_value', 3.142,
            RuleType(schema_type=SchemaTypes.ENUM, lookup='digits'),
            float_enum, 0),
        ('with_float_enum_invalid_value', 4.2,
            RuleType(schema_type=SchemaTypes.ENUM, lookup='digits'),
            float_enum, 1),
        ('with_float_enum_invalid_str_value', '3.142',
            RuleType(schema_type=SchemaTypes.ENUM, lookup='digits'),
            float_enum, 1),
    ])
    def test_enum_type_validator(self, name, data: Data, rtype: RuleType,
                                 enum: YamlatorEnum,
                                 expected_violation_count: int):
        # Unused by test case, however is required by the parameterized library
        del name

        validator = EnumTypeValidator(self.violations, enum)
        validator.validate(
            key=self.key,
            data=data,
            parent=self.parent,
            rtype=rtype)

        violation_count = len(self.violations)
        self.assertEqual(expected_violation_count, violation_count)


if __name__ == '__main__':
    unittest.main()
