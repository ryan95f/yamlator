"""Test cases for the `JSONOutput` static class

Test Cases:
    * `test_json_output` tests that the expected status code is returned
       when valid arguments are provided
    * `test_json_output_invalid_args` tests that the relevant exception is
       raised when invalid arguments are provided
"""


import io
import unittest

from typing import Iterator, Type
from unittest.mock import patch
from parameterized import parameterized

from yamlator.cmd.outputs import SuccessCode
from yamlator.cmd.outputs import JSONOutput
from yamlator.violations import RequiredViolation
from yamlator.violations import TypeViolation
from yamlator.violations import Violation


class TestJSONOutput(unittest.TestCase):
    """Test the JSONOutput display method"""

    @parameterized.expand([
        ('with_no_violations', [], SuccessCode.SUCCESS),
        ('with_violations', [
            RequiredViolation(key='message', parent='-'),
            TypeViolation(key='number', parent='-', message='Invalid number')
        ], SuccessCode.ERR)
    ])
    def test_json_output(self, name: str,
                         violations: Iterator[Violation],
                         expected_status_code: str):
        # Unused by test case, however is required by the parameterized library
        del name

        # Suppress the print statements
        with patch('sys.stdout', new=io.StringIO()):
            status_code = JSONOutput.display(violations)
            self.assertEqual(expected_status_code, status_code)

    @parameterized.expand([
        ('with_none_violations', None, ValueError)
    ])
    def test_json_output_invalid_args(self, name: str,
                                      violations: Iterator[Violation],
                                      expected_exception: Type[Exception]):
        # Unused by test case, however is required by the parameterized library
        del name

        with self.assertRaises(expected_exception):
            JSONOutput.display(violations)


if __name__ == '__main__':
    unittest.main()
