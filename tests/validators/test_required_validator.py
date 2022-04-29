import unittest

from .base import BaseValidatorTest
from parameterized import parameterized

from src.types import Data
from src.validators import RequiredValidator


class TestRequiredValidator(BaseValidatorTest):

    @parameterized.expand([
        ('required_data', 'hello world', True, False),
        ('required_none_data', None, True, True),
        ('optional_data', 'hello world', False, False),
        ('optional_none_data', None, False, False)
    ])
    def test_required_validator(self, name: str, data: Data, is_required: bool,
                                expect_violation: bool):
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
