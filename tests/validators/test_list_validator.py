import unittest

from .base import BaseValidatorTest

from typing import Any
from unittest.mock import MagicMock
from parameterized import parameterized

from yamlator.validators import ListValidator
from yamlator.types import RuleType
from yamlator.types import SchemaTypes


class TestListValidator(BaseValidatorTest):
    def setUp(self):
        super().setUp()
        self.mock_ruleset_validator = MagicMock()
        self.mock_ruleset_validator.validate.return_value = None

    @parameterized.expand([
        ('with_str_type', RuleType(schema_type=SchemaTypes.STR), 'hello', 0, 0),
        ('with_int_type', RuleType(schema_type=SchemaTypes.INT), 42, 0, 0),
        ('with_map_type', RuleType(schema_type=SchemaTypes.MAP), {'value': 42}, 0, 0),
        ('with_regex_type', RuleType(
            schema_type=SchemaTypes.REGEX, regex='value'), "value", 0, 0),
        ('with_str_type_none_data', RuleType(schema_type=SchemaTypes.STR), None, 0, 0),
        ('with_list_type', RuleType(
            schema_type=SchemaTypes.LIST,
            sub_type=RuleType(schema_type=SchemaTypes.INT)), [0, 1, 2, 3], 0, 0),
        ('with_ruleset_list_type', RuleType(
            schema_type=SchemaTypes.LIST, sub_type=RuleType(
                schema_type=SchemaTypes.RULESET, lookup='message'
            )
        ), [{'msg': 'hello'}, {'msg': 'world'}], 2, 0),
        ('with_nested_list', RuleType(
            schema_type=SchemaTypes.LIST, sub_type=RuleType(
                schema_type=SchemaTypes.LIST, sub_type=RuleType(
                    schema_type=SchemaTypes.INT)
                )
        ), [[0, 1, 2], [3, 4, 5]], 0, 0),
        ('with_list_type_none_data', RuleType(
            schema_type=SchemaTypes.LIST,
            sub_type=RuleType(schema_type=SchemaTypes.INT)), None, 0, 1),
        ('with_list_type_str', RuleType(
            schema_type=SchemaTypes.LIST,
            sub_type=RuleType(schema_type=SchemaTypes.INT)), "hello world", 0, 1),
    ])
    def test_list_validator(self, name: str, rtype: RuleType, data: Any,
                            ruleset_validate_call_count: int,
                            expected_violation_count: int):
        validator = ListValidator(self.violations)
        validator.set_ruleset_validator(self.mock_ruleset_validator)

        validator.validate(
            key=self.key,
            data=data,
            parent=self.parent,
            rtype=rtype)

        self.assertEqual(
            ruleset_validate_call_count,
            self.mock_ruleset_validator.validate.call_count
        )

        actual_violation_count = len(self.violations)
        self.assertEqual(expected_violation_count, actual_violation_count)


if __name__ == '__main__':
    unittest.main()
