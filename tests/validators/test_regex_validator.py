import unittest

from .base import BaseValidatorTest
from parameterized import parameterized

from yamlator.types import Data
from yamlator.types import RuleType
from yamlator.types import SchemaTypes
from yamlator.validators import RegexValidator


class TestRegexValidator(BaseValidatorTest):
    @parameterized.expand([
        ('with_int_type', 12, RuleType(schema_type=SchemaTypes.INT), 0),
        ('with_str_type', "roles/user", RuleType(schema_type=SchemaTypes.STR), 0),
        ('with_list_type', ["val1", "val2"],
            RuleType(schema_type=SchemaTypes.LIST, sub_type=RuleType(schema_type=SchemaTypes.STR)), 0),
        ('with_ruleset_type', {'val1': 'value'},
            RuleType(schema_type=SchemaTypes.RULESET, lookup='value'), 0),
        ('with_expected_regex_type_no_violations', "roles/myrole",
            RuleType(schema_type=SchemaTypes.REGEX, regex="roles/[a-z]+"), 0),
        ('with_expected_regex_type_violations', "roles/user",
            RuleType(schema_type=SchemaTypes.REGEX, regex="^role/"), 1),
        ('with_regex_type_list_data', ["roles/admin"],
            RuleType(schema_type=SchemaTypes.REGEX, regex="roles/[a-z]+"), 1),
        ('with_regex_type_int_data', 42,
            RuleType(schema_type=SchemaTypes.REGEX, regex="roles/[a-z]+"), 1),
        ('with_regex_type_dict_data', {"val": 100},
            RuleType(schema_type=SchemaTypes.REGEX, regex="roles/[a-z]+"), 1),
        ('with_regex_type_none_data', None,
            RuleType(schema_type=SchemaTypes.REGEX, regex="roles/[a-z]+"), 1)
    ])
    def test_regex_validator(self, name: str, data: Data, rtype: RuleType,
                             expected_violation_count: int):

        validator = RegexValidator(self.violations)
        validator.validate(
            key=self.key,
            data=data,
            parent=self.parent,
            rtype=rtype,
            is_required=True)

        violation_count = len(self.violations)
        self.assertEqual(expected_violation_count, violation_count)


if __name__ == '__main__':
    unittest.main()
