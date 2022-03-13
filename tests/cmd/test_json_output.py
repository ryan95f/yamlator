import io
import unittest

from typing import Iterator
from unittest.mock import patch
from parameterized import parameterized

from yamler.cmd import ERR, SUCCESS, JSONOutput
from yamler.violations import RequiredViolation, TypeViolation, Violation


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


if __name__ == '__main__':
    unittest.main()
