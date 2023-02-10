"""Test cases for the is_keyless_rule function

Test cases:
    * `test_is_keyless_rule` tests that given a different rules it identifies
       the specific keyless rule `KEYLESS_RULE_DIRECTIVE`
"""


import unittest

from parameterized import parameterized

from yamlator.types import Rule
from yamlator.types import RuleType
from yamlator.types import SchemaTypes
from yamlator.utils import is_keyless_rule
from yamlator.utils import KEYLESS_RULE_DIRECTIVE


class TestIsKeylessRule(unittest.TestCase):
    """Test case for the `is_keyless_rule` function"""

    @parameterized.expand([
        ('with_expected_directive',
            Rule(KEYLESS_RULE_DIRECTIVE,
                 RuleType(SchemaTypes.INT), False), True),
        ('with_malformed_directive',
            Rule('!yamlator',
                 RuleType(SchemaTypes.INT), False), False),
        ('without_directive',
            Rule('hello',
                 RuleType(SchemaTypes.INT), False), False)
    ])
    def test_is_keyless_rule(self, name, rule, expected):
        # Unused by test case, however is required by the parameterized library
        del name

        actual = is_keyless_rule(rule)
        self.assertEqual(expected, actual)

    def test_is_keyless_rule_with_none_rule(self):
        with self.assertRaises(ValueError):
            is_keyless_rule(None)


if __name__ == '__main__':
    unittest.main()
