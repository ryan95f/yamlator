import unittest

from collections import deque
from typing import Any
from parameterized import parameterized

from src.violations import BuiltInTypeViolation
from src.violations import RequiredViolation
from src.violations import RulesetTypeViolation
from src.violations import TypeViolation
from src.violations import ViolationJSONEncoder


class TestViolationJSONEncoder(unittest.TestCase):
    @parameterized.expand([
        ('encode_deque', deque(['hello', 'world'])),
        ('encode_type_violation', TypeViolation('data', '-', "Should be a string")),
        ('encode_required_violation', RequiredViolation('data', '-')),
        ('encode_ruleset_type_violation', RulesetTypeViolation('data', '-')),
        ('encode_build_in_type_violation', BuiltInTypeViolation('data', '-', int))
    ])
    def test_json_encoding(self, name: str, data: Any):
        encoder = ViolationJSONEncoder()
        encoded_json = encoder.default(data)
        self.assertIsNotNone(encoded_json)


if __name__ == 'main':
    unittest.main()
