import unittest

from parameterized import parameterized
from yamler.wranglers import wrangle_data
from yamler.types import Data, Rule, RuleType, YamlerRuleSet


def create_flat_ruleset():
    rules = [
        Rule('message', RuleType(type=str), True),
        Rule('number', RuleType(type=int), False),
    ]
    return {
        "main": YamlerRuleSet('main', rules),
        "rules": {}
    }


def create_complex_ruleset():
    person_ruleset = YamlerRuleSet("ruleset", [
        Rule('name', RuleType(type=str), True),
        Rule('age', RuleType(type=int), False)
    ])

    main_ruleset = YamlerRuleSet("main", [
        Rule("num_lists", RuleType(type=list, sub_type=RuleType(type=list, sub_type=RuleType(type=int))), False),  # nopep8
        Rule('personList', RuleType(type=list, sub_type=RuleType(type="ruleset", lookup="person")), False),  # nopep8
        Rule('person', RuleType(type="ruleset", lookup="person"), False),
        Rule('my_map', RuleType(type=dict, sub_type=RuleType(type=str)), False),
        Rule('my_any_list', RuleType(type=list, sub_type=RuleType(type='any')), False)
    ])

    return {
        'main': main_ruleset,
        "rules": {"person": person_ruleset}
    }


FLAT_RULESET = create_flat_ruleset()
COMPLEX_RULESET = create_complex_ruleset()


class TestWrangleData(unittest.TestCase):

    @parameterized.expand([
        ('none_data', None, FLAT_RULESET),
        ('none_instructions', {'message': 'hello'}, None),
        ('none_data_and_instructions', None, None),
    ])
    def test_wrangler_invalid_parameters(self, name: str, data: Data, instructions: dict):
        with self.assertRaises(ValueError):
            wrangle_data(data, instructions)

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
        }, 3),
        ('valid_dict_type', COMPLEX_RULESET, {
            "my_map": {
                "val1": "Hello",
                "val2": "World"
            }
        }, 0),
        ('invalid_subtype_map_type', COMPLEX_RULESET, {
            "my_map": {
                "val1": 1,
                "val2": []
            }
        }, 2),
        ('invalid_map_type', COMPLEX_RULESET, {
            "my_map": []
        }, 1),
        ('valid_empty_map_type', COMPLEX_RULESET, {
            'my_map': {}
        }, 0),
        ('valid_any_type_list', COMPLEX_RULESET, {
            'my_any_list': [1, 2, None, 'hello']
        }, 0)
    ])
    def test_wrangler(self, name, ruleset, data, expected_violations_count):
        violations = wrangle_data(data, ruleset)
        self.assertEqual(expected_violations_count, len(violations))


if __name__ == '__main__':
    unittest.main()
