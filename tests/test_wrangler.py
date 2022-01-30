import unittest

from parameterized import parameterized
from yamler.wrangler import YamlerWrangler


def create_flat_ruleset():
    return {
        'main': {
            'rules': [
                {
                    'name': 'message',
                    'rtype': {'type': str},
                    'required': True
                },
                {
                    'name': 'number',
                    'rtype': {'type': int},
                    'required': False
                }
            ]
        },
    }


def create_complex_ruleset():
    return {
        'main': {
            'rules': [
                {
                    'name': "num_lists",
                    'rtype': {'type': list, 'sub_type': {
                        'type': list, 'sub_type': {
                            'type': int
                            }
                        }
                    },
                    'required': False
                },
                {
                    'name': 'personList',
                    'rtype': {'type': list,  'sub_type': {
                        'type': 'ruleset',
                        'lookup': 'person'
                    }},
                    'required': False
                }
            ]
        },
        "rules": {
            "person": {
                "rules": [
                    {
                        'name': 'name',
                        'rtype': {'type': str},
                        'required': True
                    },
                    {
                        'name': 'age',
                        'rtype': {'type': int},
                        'required': False
                    }
                ]
            }
        }
    }


FLAT_RULESET = create_flat_ruleset()
COMPLEX_RULESET = create_complex_ruleset()


class TestYamlerWranglerNew(unittest.TestCase):
    """
    Constructor Tests:
        1. Empty Dict
        2. None Dict - Done
        3. Valid Instructions

    Wrangler Tests
        1. Empty Data
        2. None Data
        3. Optional Data
        4. Roleset (with optional / required fields)
        5. Incorrect type
        6. list
        7. nested lists
    """

    @parameterized.expand([
        ("empty_instructions", {}),
        ("valid_instructions", FLAT_RULESET)
    ])
    def test_constructor(self, name, rulesets):
        wrangler = YamlerWrangler(rulesets)
        self.assertIsNotNone(wrangler)

    def test_constructor_none_instructions(self):
        with self.assertRaises(ValueError):
            YamlerWrangler(None)

    @parameterized.expand([
        ("empty_data_and_rules", {}, {}, 0),
        ("empty_rules", {}, {"message": "hello"}, 0),
        ("valid_flat_rules", FLAT_RULESET, {"message": "hello", "number": 1}, 0),
        ("flat_rules_invalid_data", FLAT_RULESET, {"message": 12, "number": []}, 2),
        ("flat_rules_missing_required", FLAT_RULESET, {"number": 2}, 1),
        ("flat_rules_missing_optional", FLAT_RULESET, {"message": "hello"}, 0),
        ("complex_valid_ruleset", COMPLEX_RULESET, {
            "num_lists": [[0, 1, 2], [3, 4, 5]]
        }, 0),
        ("complex_rules_invalid_list_type", COMPLEX_RULESET, {
            "num_lists": [
                ["hello", "world"]
            ]
        }, 2),
        ("complex_rules_valid_ruleset", COMPLEX_RULESET, {
            "personList": [
                {"name": "hello", "age": 2},
                {"name": "world"}
            ]
        }, 0),
        ("complex_rules_invalid_ruleset", COMPLEX_RULESET, {
            "personList": [
                {"name": 0},
                {"age": 2}
            ]
        }, 2)
    ])
    def test_wrangler(self, name, ruleset, data, expected_violations_count):
        wrangler = YamlerWrangler(ruleset)
        violations = wrangler.wrangle(data)
        self.assertEqual(expected_violations_count, len(violations))


if __name__ == '__main__':
    unittest.main()
