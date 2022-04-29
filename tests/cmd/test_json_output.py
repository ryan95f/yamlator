import io
import unittest

from typing import Iterator, Type
from unittest.mock import patch
from parameterized import parameterized

from src.cmd import ERR, SUCCESS, JSONOutput
from src.violations import RequiredViolation
from src.violations import TypeViolation
from src.violations import Violation


class TestJSONOutput(unittest.TestCase):
    @parameterized.expand([
        ('with_no_violations', [], SUCCESS),
        ('with_violations', [
            RequiredViolation(key='message', parent='-'),
            TypeViolation(key='number', parent='-', message='Invalid number')
        ], ERR)
    ])
    def test_json_output(self, name: str,
                         violations: Iterator[Violation],
                         expected_status_code: str):
        # Suppress the print statements
        with patch('sys.stdout', new=io.StringIO()):
            status_code = JSONOutput.display(violations)
            self.assertEqual(expected_status_code, status_code)

    @parameterized.expand([
        ('with_non_violations', None, ValueError)
    ])
    def test_json_output_invalid_args(self, name: str,
                                      violations: Iterator[Violation],
                                      expected_exception: Type[Exception]):
        with self.assertRaises(expected_exception):
            JSONOutput.display(violations)


if __name__ == '__main__':
    unittest.main()
