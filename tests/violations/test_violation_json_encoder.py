"""Test cases for the `ViolationJSONEncoder`

Test Cases:
    * `test_violation_json_encoder` tests the encoder using a variety
       of different data structures and types to validate the JSON
       is successfully generated
    * `test_violation_json_encoder_raises_type_error` tests the JSON
       encoder with objects that are not support
"""


import unittest

from typing import Any
from collections import deque
from parameterized import parameterized
from dataclasses import dataclass

from yamlator.violations import BuiltInTypeViolation
from yamlator.violations import RegexTypeViolation
from yamlator.violations import RequiredViolation
from yamlator.violations import RulesetTypeViolation
from yamlator.violations import TypeViolation
from yamlator.violations import ViolationJSONEncoder
from yamlator.violations import StrictRulesetViolation
from yamlator.violations import StrictEntryPointViolation


@dataclass
class FakeViolation:
    msg: str


class TestViolationJSONEncoder(unittest.TestCase):
    """Test cases for the ViolationJSONEncoder"""

    @parameterized.expand([
        ('encode_deque', deque(['hello', 'world'])),
        ('encode_type_violation',
            TypeViolation('data', '-', 'Should be a string')),
        ('encode_required_violation', RequiredViolation('data', '-')),
        ('encode_ruleset_type_violation', RulesetTypeViolation('data', '-')),
        ('encode_build_in_type_violation',
            BuiltInTypeViolation('data', '-', int)),
        ('encode_regex_type_violation',
            RegexTypeViolation('data', '-', 'message', '^roles/')),
        ('encode_int', 42),
        ('encode_bool', True),
        ('encode_string', 'hello world'),
        ('encode_dict', {'message': 'Hello World', 'number': 43}),
        ('encode_list', [0, 1, 2, 3, 4]),
        ('encode_none', None),
        ('encode_strict_ruleset_violation',
            StrictRulesetViolation('data', '-', 'message', 'details')),
        ('encode_strict_entry_point_violation',
            StrictEntryPointViolation('-', 'SCHEMA', 'name'))
    ])
    def test_violation_json_encoder(self, name: str, data: Any):
        # Unused by test case, however is required by the parameterized library
        del name

        encoder = ViolationJSONEncoder()
        encoded_json = encoder.encode(data)
        self.assertIsNotNone(encoded_json)

    @parameterized.expand([
        ('encode_base_object', object()),
        ('encode_custom_unsupported_object', FakeViolation('A fake error'))
    ])
    def test_violation_json_encoder_raises_type_error(self, name, data: Any):
        # Unused by test case, however is required by the parameterized library
        del name

        encoder = ViolationJSONEncoder()
        with self.assertRaises(TypeError):
            encoder.encode(data)


if __name__ == 'main':
    unittest.main()
