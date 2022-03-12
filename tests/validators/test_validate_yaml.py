import unittest

from parameterized import parameterized
from yamler.validators import validate_yaml
from yamler.types import Data, EnumItem, Rule, RuleType
from yamler.types import YamlerEnum, YamlerRuleset, SchemaTypes


def create_flat_ruleset():
    rules = [
        Rule('message', RuleType(type=SchemaTypes.STR), True),
        Rule('number', RuleType(type=SchemaTypes.INT), False),
    ]
    return {
        'main': YamlerRuleset('main', rules),
        'rules': {}
    }


def create_complex_ruleset():
    person_ruleset = YamlerRuleset('ruleset', [
        Rule('name', RuleType(type=SchemaTypes.STR), True),
        Rule('age', RuleType(type=SchemaTypes.INT), False)
    ])

    status_enum = YamlerEnum('Status', {
        'success': EnumItem('SUCCESS', 'success'),
        'error':  EnumItem('ERR', 'error'),
    })

    main_ruleset = YamlerRuleset('main', [
        Rule('num_lists', RuleType(
            type=SchemaTypes.LIST,
            sub_type=RuleType(
                type=SchemaTypes.LIST,
                sub_type=RuleType(type=SchemaTypes.INT))
        ), False),
        Rule('personList', RuleType(
            type=SchemaTypes.LIST,
            sub_type=RuleType(type=SchemaTypes.RULESET, lookup='person')
        ), False),
        Rule('person', RuleType(type=SchemaTypes.RULESET, lookup='person'), False),
        Rule('my_map', RuleType(
            type=SchemaTypes.MAP,
            sub_type=RuleType(type=SchemaTypes.STR)
        ), False),
        Rule('my_any_list', RuleType(
            type=SchemaTypes.LIST,
            sub_type=RuleType(type=SchemaTypes.ANY)
        ), False),
        Rule('status', RuleType(type=SchemaTypes.ENUM, lookup='Status'), False),
    ])

    return {
        'main': main_ruleset,
        'rules': {'person': person_ruleset},
        'enums': {'Status': status_enum}
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
            validate_yaml(data, instructions)

    @parameterized.expand([
        ('empty_data_and_rules', {}, {}, 0),
        ('empty_rules', {}, {'message': 'hello'}, 0),
        ('primitive_data_rules', FLAT_RULESET, {
            'message': 'hello', 'number': 1
        }, 0),
        ('primitive_data_invalid_data', FLAT_RULESET, {
            'message': 12, 'number': []
        }, 2),
        ('primitive_data_missing_required', FLAT_RULESET, {
            'number': 2
        }, 1),
        ('primitive_data_missing_optional', FLAT_RULESET, {
            'message': 'hello'
        }, 0),
        ('int_list', COMPLEX_RULESET, {
            'num_lists': [[0, 1, 2], [3, 4, 5]]
        }, 0),
        ('invalid_list_type', COMPLEX_RULESET, {
            'num_lists': [
                ['hello', 'world']
            ]
        }, 2),
        ('list_ruleset', COMPLEX_RULESET, {
            'personList': [
                {'name': 'hello', 'age': 2},
                {'name': 'world'}
            ]
        }, 0),
        ('list_ruleset_invalid_type', COMPLEX_RULESET, {
            'personList': [
                {'name': 0},
                {'age': 2}
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
        ('invald_ruleset_type', COMPLEX_RULESET, {
            'person': 3
        }, 1),
        ('invalid_list_ruleset_type', COMPLEX_RULESET, {
            'personList': [0, 2, 3]
        }, 3),
        ('valid_dict_type', COMPLEX_RULESET, {
            'my_map': {
                'val1': 'Hello',
                'val2': 'World'
            }
        }, 0),
        ('invalid_subtype_map_type', COMPLEX_RULESET, {
            'my_map': {
                'val1': 1,
                'val2': []
            }
        }, 2),
        ('invalid_map_type', COMPLEX_RULESET, {
            'my_map': []
        }, 1),
        ('valid_empty_map_type', COMPLEX_RULESET, {
            'my_map': {}
        }, 0),
        ('valid_any_type_list', COMPLEX_RULESET, {
            'my_any_list': [1, 2, None, 'hello']
        }, 0),
        ('enum_value_matches_rule', COMPLEX_RULESET, {
            'status': 'error',
        }, 0),
        ('enum_value_does_not_matche_rule', COMPLEX_RULESET, {
            'status': 'not_found',
        }, 1),
        ('enum_value_wrong_type', COMPLEX_RULESET, {
            'status': [],
        }, 1),
    ])
    def test_wrangler(self, name, ruleset, data, expected_violations_count):
        violations = validate_yaml(data, ruleset)
        self.assertEqual(expected_violations_count, len(violations))


if __name__ == '__main__':
    unittest.main()
