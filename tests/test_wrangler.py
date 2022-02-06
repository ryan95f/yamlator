import unittest

from parameterized import parameterized
from yamler.wrangler import ImprovedWrangler as YamlerWrangler
from yamler.types import Rule


def create_flat_ruleset():
    return {
        'main': {
            'rules': [
                Rule('message', {'type': str}, True),
                Rule('number', {'type': int}, False)
            ]
        },
    }


def create_complex_ruleset():
    return {
        'main': {
            'rules': [
                Rule("num_lists", {
                    'type': list, 'sub_type': {
                        'type': list, 'sub_type': {
                            'type': int
                        }
                    }
                }, False),
                Rule('personList', {
                    'type': list,  'sub_type': {
                        'type': 'ruleset',
                        'lookup': 'person'
                    }
                }, False),
                Rule('person', {
                    'type': "ruleset",
                    'lookup': 'person'
                }, False)
            ]
        },
        "rules": {
            "person": {
                "rules": [
                    Rule('name', {'type': str}, True),
                    Rule('age', {'type': int}, False)
                ]
            }
        }
    }


FLAT_RULESET = create_flat_ruleset()
COMPLEX_RULESET = create_complex_ruleset()


class TestYamlerWranglerNew(unittest.TestCase):
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

    def test_wrangler_none_data(self):
        wrangler = YamlerWrangler(FLAT_RULESET)
        with self.assertRaises(ValueError):
            wrangler.wrangle(None)

    @parameterized.expand([
        ("empty_data_and_rules", {}, {}, 0),
        ("empty_rules", {}, {"message": "hello"}, 0),
        ("primitive_data_rules", FLAT_RULESET, {
            "message": "hello", "number": 1
        }, 0),
        ("primitive_data_invalid_data", FLAT_RULESET, {
            "message": 12, "number": []
        }, 2),
        ("primitive_data_missing_required", FLAT_RULESET, {
            "number": 2
        }, 1),
        ("primitive_data_missing_optional", FLAT_RULESET, {
            "message": "hello"
        }, 0),
        ("int_list", COMPLEX_RULESET, {
            "num_lists": [[0, 1, 2], [3, 4, 5]]
        }, 0),
        ("invalid_list_type", COMPLEX_RULESET, {
            "num_lists": [
                ["hello", "world"]
            ]
        }, 2),
        ("list_ruleset", COMPLEX_RULESET, {
            "personList": [
                {"name": "hello", "age": 2},
                {"name": "world"}
            ]
        }, 0),
        ("list_ruleset_invalid_type", COMPLEX_RULESET, {
            "personList": [
                {"name": 0},
                {"age": 2}
            ]
        }, 2),
        ('valid_ruleset_type', COMPLEX_RULESET, {
            'person': {
                'name': 'Test',
                'age': 100
            }
        }, 0),
        ('valid_ruleset_missing_optional', COMPLEX_RULESET, {
            'person': {
                'name': 'Test'
            }
        }, 0),
        ("invald_ruleset_type", COMPLEX_RULESET, {
            'person': 3
        }, 1),
        ("invalid_list_ruleset_type", COMPLEX_RULESET, {
            "personList": [0, 2, 3]
        }, 3)
    ])
    def test_wrangler(self, name, ruleset, data, expected_violations_count):
        wrangler = YamlerWrangler(ruleset)
        violations = wrangler.wrangle(data)
        self.assertEqual(expected_violations_count, len(violations))


if __name__ == '__main__':
    unittest.main()
