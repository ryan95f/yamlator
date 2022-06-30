"""Test cases for the `validate_yaml` function

Test cases:
    * `test_validator_invalid_parameters` tests the validate yaml function
       with a range of invalid arguments
    * `test_validator` tests the validate yaml function with a variety of
       different schemas and data to verify the validation process
"""


import unittest

from parameterized import parameterized

from yamlator.types import Data
from yamlator.types import Rule
from yamlator.types import RuleType
from yamlator.types import EnumItem
from yamlator.types import YamlatorEnum
from yamlator.types import YamlatorRuleset
from yamlator.types import SchemaTypes
from yamlator.validators.core import validate_yaml


def create_flat_schema():
    rules = [
        Rule('message', RuleType(schema_type=SchemaTypes.STR), True),
        Rule('number', RuleType(schema_type=SchemaTypes.INT), False),
    ]
    return {
        'main': YamlatorRuleset('main', rules),
        'rules': {}
    }


def create_complex_schema():
    person_ruleset = YamlatorRuleset('ruleset', [
        Rule('name', RuleType(schema_type=SchemaTypes.STR), True),
        Rule('age', RuleType(schema_type=SchemaTypes.INT), False)
    ])

    status_enum = YamlatorEnum('Status', {
        'success': EnumItem('SUCCESS', 'success'),
        'error':  EnumItem('ERR', 'error'),
    })

    main_ruleset = YamlatorRuleset('main', [
        Rule('num_lists', RuleType(
            schema_type=SchemaTypes.LIST,
            sub_type=RuleType(
                schema_type=SchemaTypes.LIST,
                sub_type=RuleType(schema_type=SchemaTypes.INT))), False),
        Rule('personList',
             RuleType(schema_type=SchemaTypes.LIST,
                      sub_type=RuleType(schema_type=SchemaTypes.RULESET,
                                        lookup='person')), False),
        Rule('person',
             RuleType(schema_type=SchemaTypes.RULESET, lookup='person'), False),
        Rule('my_map',
             RuleType(schema_type=SchemaTypes.MAP,
                      sub_type=RuleType(schema_type=SchemaTypes.STR)), False),
        Rule('my_any_list',
             RuleType(schema_type=SchemaTypes.LIST,
                      sub_type=RuleType(schema_type=SchemaTypes.ANY)), False),
        Rule('status',
             RuleType(schema_type=SchemaTypes.ENUM, lookup='Status'), False),
    ])

    return {
        'main': main_ruleset,
        'rules': {'person': person_ruleset},
        'enums': {'Status': status_enum}
    }


FLAT_RULESET = create_flat_schema()
COMPLEX_RULESET = create_complex_schema()


class TestWrangleData(unittest.TestCase):
    """Test cases for the validate_yaml function"""

    @parameterized.expand([
        ('none_data', None, FLAT_RULESET),
        ('none_instructions', {'message': 'hello'}, None),
        ('none_data_and_instructions', None, None),
    ])
    def test_validator_invalid_parameters(self, name: str, data: Data,
                                          instructions: dict):
        # Unused by test case, however is required by the parameterized library
        del name

        with self.assertRaises(ValueError):
            validate_yaml(data, instructions)

    @parameterized.expand([
        ('empty_data_and_schema', {}, {}, 0),
        ('empty_schema', {}, {'message': 'hello'}, 0),
        ('primitive_data_schema', FLAT_RULESET, {
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
    def test_validator(self, name, ruleset, data, expected_violations_count):
        # Unused by test case, however is required by the parameterized library
        del name

        violations = validate_yaml(data, ruleset)
        self.assertEqual(expected_violations_count, len(violations))


if __name__ == '__main__':
    unittest.main()
