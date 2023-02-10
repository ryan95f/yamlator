"""Test cases for the RequiredValidator


Test cases:
    * `test_required_validator` tests the required validator with
       different required and optional flags
"""


import unittest

from .base import BaseValidatorTest
from parameterized import parameterized

from yamlator.types import Data
from yamlator.validators import RequiredValidator


class TestRequiredValidator(BaseValidatorTest):
    """Test cases for the Required Validator"""

    @parameterized.expand([
        ('required_data', 'hello world', True, False),
        ('required_none_data', None, True, True),
        ('optional_data', 'hello world', False, False),
        ('optional_none_data', None, False, False)
    ])
    def test_required_validator(self, name: str, data: Data, is_required: bool,
                                expect_violation: bool):
        # Unused by test case, however is required by the parameterized library
        del name

        validator = RequiredValidator(self.violations)
        validator.validate(
            key=self.key,
            data=data,
            parent=self.parent,
            rtype=self.rtype,
            is_required=is_required)

        has_violations = len(self.violations) == 1
        self.assertEqual(expect_violation, has_violations)


if __name__ == '__main__':
    unittest.main()
