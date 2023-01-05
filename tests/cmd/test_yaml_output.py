"""Test cases for the `YAMLOutput` static class

Test Cases:
    * `test_yaml_output` tests that the expected status code is returned
       when valid arguments are provided
    * `test_yaml_output_invalid_args` tests that the relevant exception is
       raised when invalid arguments are provided
"""

import io
import unittest

from collections import deque
from unittest.mock import patch
from typing import Type
from typing import Iterator
from parameterized import parameterized

from yamlator.cmd.outputs import YAMLOutput
from yamlator.cmd.outputs import SuccessCode
from yamlator.violations import BuiltInTypeViolation
from yamlator.violations import RegexTypeViolation
from yamlator.violations import RulesetTypeViolation
from yamlator.violations import RequiredViolation
from yamlator.violations import TypeViolation
from yamlator.violations import Violation
from yamlator.violations import StrictRulesetViolation


class TestYAMLOutput(unittest.TestCase):
    """Test the YAMLOutput display method"""

    @parameterized.expand([
        ('with_no_violations', deque(), SuccessCode.SUCCESS),
        ('with_violations', deque([
            RequiredViolation(key='message', parent='-'),
            TypeViolation(key='number', parent='-', message='Invalid number'),
            BuiltInTypeViolation(key='name',
                                 parent='-',
                                 expected_type=str),
            RulesetTypeViolation(key='address', parent='-'),
            StrictRulesetViolation(key='data',
                                   parent='-',
                                   field='message',
                                   ruleset_name='details'),
            RegexTypeViolation(key='data',
                               parent='-',
                               data='1st January 2022',
                               regex_str=r'([0-3][0-9]\/){2}2022')
        ]), SuccessCode.ERR)
    ])
    def test_yaml_output(self,
                         name: str,
                         violations: Iterator[Violation],
                         expected_status_code: str):
        # Unused by test case, however is required by the parameterized library
        del name

        # Suppress the print statements
        with patch('sys.stdout', new=io.StringIO()):
            status_code = YAMLOutput.display(violations)
            self.assertEqual(expected_status_code, status_code)

    @parameterized.expand([
        ('with_none_violations', None, ValueError)
    ])
    def test_yaml_output_invalid_args(self,
                                      name: str,
                                      violations: Iterator[Violation],
                                      expected_exception: Type[Exception]):
        # Unused by test case, however is required by the parameterized library
        del name

        with self.assertRaises(expected_exception):
            YAMLOutput.display(violations)


if __name__ == '__main__':
    unittest.main()
