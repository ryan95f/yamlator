import io
import unittest

from typing import Iterator
from unittest.mock import patch
from parameterized import parameterized

from yamler.cmd import ConsoleOutput
from yamler.violations import RequiredViolation
from yamler.violations import TypeViolation
from yamler.violations import ViolationType


class TestConsoleOutput(unittest.TestCase):

    @parameterized.expand([
        ('with_no_violations', [], 0),
        ('with_violations', [
            RequiredViolation(key="message", parent="-"),
            TypeViolation(key="number", parent="-", message="Invalid number")
        ], -1)
    ])
    def test_displayed_violation_outut(self, name: str,
                                       violations: Iterator[ViolationType],
                                       expected_status_code: int):

        # Supress the print statements
        with patch('sys.stdout', new=io.StringIO()) as std_out:
            status_code = ConsoleOutput.display(violations)
            self.assertEqual(expected_status_code, status_code)


if __name__ == '__main__':
    unittest.main()
