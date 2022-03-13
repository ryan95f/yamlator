from collections import deque
import unittest

from typing import Any
from parameterized import parameterized

from yamler.violations import BuiltInTypeViolation
from yamler.violations import RequiredViolation
from yamler.violations import RulesetTypeViolation
from yamler.violations import TypeViolation
from yamler.violations import ViolationJSONEncoder


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
