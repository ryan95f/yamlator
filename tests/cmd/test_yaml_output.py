"""Test cases for the `YAMLOutput` static class

Test Cases:
    * `test_json_output` tests that the expected status code is returned
       when valid arguments are provided
    * `test_json_output_invalid_args` tests that the relevant exception is
       raised when invalid arguments are provided
"""

import io
import unittest

from collections import deque
from unittest.mock import patch
from typing import Iterator, Type
from parameterized import parameterized

from yamlator.cmd import YAMLOutput
from yamlator.cmd import ERR, SUCCESS
from yamlator.violations import RequiredViolation
from yamlator.violations import TypeViolation
from yamlator.violations import Violation


class TestYAMLOutput(unittest.TestCase):
    """Test the YAMLOutput display method"""

    @parameterized.expand([
        ('with_no_violations', deque(), SUCCESS),
        ('with_violations', deque([
            RequiredViolation(key='message', parent='-'),
            TypeViolation(key='number', parent='-', message='Invalid number')
        ]), ERR)
    ])
    def test_json_output(self,
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
