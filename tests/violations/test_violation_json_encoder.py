import unittest

from typing import Any
from collections import deque
from parameterized import parameterized

from src.violations import BuiltInTypeViolation, RegexTypeViolation
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
        ('encode_build_in_type_violation', BuiltInTypeViolation('data', '-', int)),
        ('encode_regex_type_violation', RegexTypeViolation('data', '-',
                                                           'message', '^roles/')),
        ('encode_int', 42),
        ('encode_bool', True),
        ('encode_string', 'hello world'),
        ('encode_dict', {'message': 'Hello World', 'number': 43}),
        ('encode_list', [0, 1, 2, 3, 4]),
        ('encode_none', None)
    ])
    def test_json_encoding(self, name: str, data: Any):
        encoder = ViolationJSONEncoder()
        encoded_json = encoder.encode(data)
        self.assertIsNotNone(encoded_json)


if __name__ == 'main':
    unittest.main()
