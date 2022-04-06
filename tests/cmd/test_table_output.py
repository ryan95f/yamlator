import io
import unittest

from typing import Iterator
from unittest.mock import patch
from parameterized import parameterized

from src.cmd import ERR, SUCCESS, TableOutput
from src.violations import RequiredViolation
from src.violations import TypeViolation
from src.violations import ViolationType


class TestTableOutput(unittest.TestCase):

    @parameterized.expand([
        ('with_no_violations', [], SUCCESS),
        ('with_violations', [
            RequiredViolation(key='message', parent='-'),
            TypeViolation(key='number', parent='-', message='Invalid number')
        ], ERR)
    ])
    def test_displayed_violation_output(self, name: str,
                                        violations: Iterator[ViolationType],
                                        expected_status_code: int):

        # Suppress the print statements
        with patch('sys.stdout', new=io.StringIO()):
            status_code = TableOutput.display(violations)
            self.assertEqual(expected_status_code, status_code)


if __name__ == '__main__':
    unittest.main()
