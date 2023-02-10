"""Test cases for the display_violations function

Test cases:
    * `test_display_violations` tests that the function will display the
       results when provided a valid display method
    * `test_display_violations_invalid_params` tests that a ValueError
       exception is raised when invalid parameters are provided
"""


import io
import unittest

from typing import Iterator
from unittest.mock import patch
from parameterized import parameterized

from yamlator.cmd import display_violations
from yamlator.cmd import DisplayMethod
from yamlator.cmd.outputs import SuccessCode
from yamlator.violations import RequiredViolation
from yamlator.violations import TypeViolation
from yamlator.violations import BuiltInTypeViolation
from yamlator.violations import RulesetTypeViolation
from yamlator.violations import RegexTypeViolation
from yamlator.violations import Violation


EMPTY_VIOLATION_LIST = []
VIOLATION_LIST = [
    RequiredViolation(key='message', parent='-'),
    TypeViolation(key='number', parent='-', message='Invalid number'),
    BuiltInTypeViolation(key='name',
                         parent='-',
                         expected_type=str),
    RulesetTypeViolation(key='address', parent='-'),
    RegexTypeViolation(key='data',
                       parent='-',
                       data='1st January 2022',
                       regex_str=r'([0-3][0-9]\/){2}2022')
]


class TestDisplayViolations(unittest.TestCase):
    """Test that the display violation function"""

    @parameterized.expand([
        ('display_table_with_violations',
            VIOLATION_LIST,
            DisplayMethod.TABLE,
            SuccessCode.ERR),
        ('display_table_without_violations',
            EMPTY_VIOLATION_LIST,
            DisplayMethod.TABLE,
            SuccessCode.SUCCESS),
        ('display_json_with_violations',
            VIOLATION_LIST,
            DisplayMethod.JSON,
            SuccessCode.ERR),
        ('display_json_without_violations',
            EMPTY_VIOLATION_LIST,
            DisplayMethod.JSON,
            SuccessCode.SUCCESS),
        ('display_yaml_with_violations',
            VIOLATION_LIST,
            DisplayMethod.YAML,
            SuccessCode.ERR),
        ('display_yaml_without_violations',
            EMPTY_VIOLATION_LIST,
            DisplayMethod.YAML,
            SuccessCode.SUCCESS),
    ])
    def test_display_violations(self, name, violations: Iterator[Violation],
                                display_method: str, expected_status_code: int):
        # Unused by test case, however is required by the parameterized library
        del name

        # Suppress the print statements
        with patch('sys.stdout', new=io.StringIO()):
            status_code = display_violations(violations, display_method)
            self.assertEqual(expected_status_code, status_code)

    @parameterized.expand([
        ('with_none_violations', None, DisplayMethod.JSON),
        ('with_none_display_method', [RequiredViolation('data', '-')], None),
        ('with_violations_and_display_method_none', None, None)
    ])
    def test_display_violations_invalid_params(self, name: str,
                                               violations: Iterator[Violation],
                                               display_method: str):
        # Unused by test case, however is required by the parameterized library
        del name

        with self.assertRaises(ValueError):
            display_violations(violations, display_method)


if __name__ == '__main__':
    unittest.main()
