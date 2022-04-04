import unittest

from .base import BaseValidatorTest

from unittest.mock import Mock, patch
from parameterized import parameterized
from src.types import Data
from src.validators import OptionalValidator


class TestOptionalValidator(BaseValidatorTest):

    @parameterized.expand([
        ('with_optional_data', False, 'hello world', 1),
        ('with_required_data', True, 'Hello World', 1),
        ('with_optional_and_none_data', False, None, 0),
        ('with_required_and_none_data', True, None, 1),
    ])
    @patch('yamler.validators.Validator.validate')
    def test_optional_validator(self, name: str, is_required: bool, data: Data,
                                next_validator_call_count: int,
                                mock_parent_validator: Mock):
        validator = OptionalValidator(self.violations)
        validator.validate(
            key=self.key,
            data=data,
            parent=self.parent,
            rtype=self.rtype,
            is_required=is_required)

        self.assertEqual(next_validator_call_count, mock_parent_validator.call_count)


if __name__ == '__main__':
    unittest.main()
