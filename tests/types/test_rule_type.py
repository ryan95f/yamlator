"""Test case for the RuleType object

Test cases:
    * `test_rule_type_string_representation` tests the string output
      when different RuleTypes are configured
"""

import unittest

from parameterized import parameterized

from yamlator.types import RuleType
from yamlator.types import UnionRuleType
from yamlator.types import SchemaTypes


class TestRuleType(unittest.TestCase):
    """Test cases for the RuleType objects"""

    @parameterized.expand([
        ('str_type', RuleType(SchemaTypes.STR), 'str'),
        ('int_type', RuleType(SchemaTypes.INT), 'int'),
        ('float_type', RuleType(SchemaTypes.FLOAT), 'float'),
        ('int_map', RuleType(
            SchemaTypes.MAP,
            sub_type=RuleType(SchemaTypes.INT)), 'map(int)'),
        ('map_of_int_maps', RuleType(
            SchemaTypes.MAP,
            sub_type=RuleType(
                    SchemaTypes.MAP,
                    sub_type=RuleType(SchemaTypes.INT)
                )
            ),
            'map(map(int))'),
        ('str_list', RuleType(
            SchemaTypes.LIST,
            sub_type=RuleType(SchemaTypes.INT)), 'list(int)'),
        ('list_of_str_lists', RuleType(
            SchemaTypes.LIST,
            sub_type=RuleType(
                SchemaTypes.LIST,
                sub_type=RuleType(SchemaTypes.STR))
            ),
            'list(list(str))'),
        ('enum_type', RuleType(
            SchemaTypes.ENUM, lookup='Numbers'),
            'Numbers'),
        ('ruleset_type',
            RuleType(SchemaTypes.RULESET, lookup='Details'),
            'Details'),
        ('any_type', RuleType(SchemaTypes.ANY), 'any'),
        ('regex_type',
            RuleType(SchemaTypes.REGEX, regex='^role'),
            'Regex(^role)'),
        ('bool_type', RuleType(SchemaTypes.BOOL), 'bool'),
        ('union_type', UnionRuleType([
            RuleType(SchemaTypes.INT),
            RuleType(
                SchemaTypes.LIST,
                sub_type=RuleType(
                    SchemaTypes.LIST,
                    sub_type=RuleType(SchemaTypes.STR)
                )
            )
        ]), 'union(int, list(list(str)))')
    ])
    def test_rule_type_string_representation(self, name: str, rtype: RuleType,
                                             expected_string: str):
        del name

        actual_string = str(rtype)
        self.assertEqual(expected_string, actual_string)


if __name__ == '__main__':
    unittest.main()
