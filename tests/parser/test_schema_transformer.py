"""Test cases for the `SchemaTransformer`

Test Cases:
    * `test_required_rule` tests the transformation of a required rule token
       into a rule object with required set to `true`
    * `test_optional_rule` tests the transformation of a optional rule token
       into a rule object with required set to `false`
    * `test_ruleset` tests that given a set of rule tokens, a ruleset is
       generated that contains all the specified rules
    * `test_start` tests that all the rulesets and enums are sorted into
       the correct container type, which can then be used by the Yamlator
       validation chain
    * `test_str_type` tests transforming a string token into a Yamlator
       string rule type
    * `test_int_type` tests transforming a int token into a Yamlator
       int rule type
    * `test_float_type` tests transforming a float token into a Yamlator
       float rule type
    * `test_list_type` tests transforming a list token into a Yamlator
       list rule type
    * `test_map_type` tests transforming a map token into a Yamlator
       map rule type
    * `test_any_type` tests transforming a any token into a Yamlator
       any rule type
    * `test_bool_type` tests transforming a bool token into a Yamlator
       bool rule type
    * `test_enum_item` tests transforming enum item tokens into a Yamlator
       enum item
    * `test_enum` tests that given a set of enum items a enum container
       type is created
    * `test_container_type` tests transforming a container Type
       (ruleset / enum) type into the relevant rule type
    * `test_container_type_construct_does_not_exist` tests transforming a
       container type when the name of the given container is not found
    * `test_regex_type` tests transforming regex tokens into a Yamlator
       regex type
    * `test_type` tests the type transformer returns the token it was
       passed so the other transformer can successfully transform it
    * `test_schema_entry` tests that given a set of rule tokens within
       a schema block, a schema block is generated that contains all
       the specified rules
    * `test_strict_schema_entry` tests that given a set of rule tokens within
       a schema block, a schema block is generated that contains all
       the specified rules in strict mode
    * `test_int_transform` tests transforming a int into an actual
       integer value
    * `test_float_transform` tests transforming a float into an actual
       float value
    * `test_escaped_string_transform` tests that a string is escaped
       and any speech marks are removed
"""


import re
import unittest

from collections import namedtuple
from parameterized import parameterized
from yamlator.exceptions import ConstructNotFoundError

from yamlator.parser import SchemaTransformer
from yamlator.types import EnumItem, Rule, RuleType
from yamlator.types import YamlatorEnum, YamlatorRuleset, SchemaTypes


Token = namedtuple('Token', ['value'])


class TestSchemaTransformer(unittest.TestCase):
    """Tests the Schema Transformer"""

    def setUp(self):
        self.transformer = SchemaTransformer()
        self.name_token = Token('message')
        self.status_code_token = Token('StatusCode')

        self.str_rtype = RuleType(schema_type=SchemaTypes.STR)
        self.ruleset_rules = [
            Rule('name', RuleType(schema_type=SchemaTypes.STR), True),
            Rule('age', RuleType(schema_type=SchemaTypes.INT), True),
        ]

    def test_required_rule(self):
        tokens = (self.name_token, self.str_rtype)

        required_rule = self.transformer.required_rule(tokens)
        self.assertEqual(self.name_token.value, required_rule.name)
        self.assertTrue(required_rule.is_required)

    def test_optional_rule(self):
        tokens = (self.name_token, self.str_rtype)
        optional_rule = self.transformer.optional_rule(tokens)

        self.assertEqual(self.name_token.value, optional_rule.name)
        self.assertFalse(optional_rule.is_required)

    def test_ruleset(self):
        name = Token('person')
        tokens = (name, *self.ruleset_rules)
        ruleset = self.transformer.ruleset(tokens)

        self.assertEqual(name.value, ruleset.name)
        self.assertEqual(len(self.ruleset_rules), len(ruleset.rules))
        self.assertFalse(ruleset.is_strict)

    def test_strict_ruleset(self):
        name = Token('person')
        tokens = (name, *self.ruleset_rules)
        ruleset = self.transformer.strict_ruleset(tokens)

        self.assertEqual(name.value, ruleset.name)
        self.assertEqual(len(self.ruleset_rules), len(ruleset.rules))
        self.assertTrue(ruleset.is_strict)

    def test_start(self):
        # This will be zero since main is removed from the dict
        # when processed by the start transformer
        expected_ruleset_count = 0
        expected_enum_count = 1

        instructions = [
            YamlatorEnum('StatusCode', {
                'success': EnumItem('SUCCESS', 'success'),
                'error': EnumItem('ERR', 'error')
            }),
            YamlatorRuleset('main', [
                Rule('message', RuleType(schema_type=SchemaTypes.STR), True)
            ])
        ]

        ruleset_items = self.transformer.start(instructions)
        rulesets = ruleset_items.get('rules')
        enums = ruleset_items.get('enums')

        self.assertIsNotNone(ruleset_items.get('main'))
        self.assertEqual(expected_enum_count, len(enums))
        self.assertEqual(expected_ruleset_count, len(rulesets))

    def test_str_type(self):
        str_rule_type = self.transformer.str_type(())
        self.assertEqual(SchemaTypes.STR, str_rule_type.schema_type)

    def test_int_type(self):
        int_rule_type = self.transformer.int_type(())
        self.assertEqual(SchemaTypes.INT, int_rule_type.schema_type)

    def test_float_type(self):
        float_rule_type = self.transformer.float_type(())
        self.assertEqual(SchemaTypes.FLOAT, float_rule_type.schema_type)

    def test_list_type(self):
        tokens = (self.str_rtype, )
        list_type = self.transformer.list_type(tokens)

        self.assertEqual(SchemaTypes.LIST, list_type.schema_type)
        self.assertEqual(tokens[0], list_type.sub_type)

    def test_map_type(self):
        tokens = (self.str_rtype, )
        map_type = self.transformer.map_type(tokens)

        self.assertEqual(SchemaTypes.MAP, map_type.schema_type)
        self.assertEqual(tokens[0], map_type.sub_type)

    def test_any_type(self):
        any_type = self.transformer.any_type(())
        self.assertEqual(SchemaTypes.ANY, any_type.schema_type)

    def test_bool_type(self):
        bool_type = self.transformer.bool_type(())
        self.assertEqual(SchemaTypes.BOOL, bool_type.schema_type)

    def test_enum_item(self):
        enum_name = 'StatusCode'
        enum_value = 'success'

        tokens = (enum_name, enum_value)
        enum_item = self.transformer.enum_item(tokens)

        self.assertEqual(enum_name, enum_item.name)
        self.assertEqual(enum_value, enum_item.value)

    def test_enum(self):
        enum_items = [
            EnumItem('SUCCESS', 'success'),
            EnumItem('ERR', 'error')
        ]

        tokens = (self.status_code_token, *enum_items)
        enum = self.transformer.enum(tokens)

        self.assertEqual(self.status_code_token.value, enum.name)
        self.assertEqual(len(enum_items), len(enum.items))

    def test_container_type(self):
        token = Token('Employee')
        self.transformer.seen_constructs = {'Employee': SchemaTypes.RULESET}
        rule = self.transformer.container_type(token)
        self.assertEqual(rule.schema_type, SchemaTypes.RULESET)

    @parameterized.expand([
        ('with_existing_constructs', {
            'Details': SchemaTypes.RULESET,
            'Status': SchemaTypes.ENUM
        }),
        ('without_existing_constructs', {})
    ])
    def test_container_type_construct_does_not_exist(self, name: str,
                                                     seen_constructs: dict):
        token = Token(name)
        self.transformer.seen_constructs = seen_constructs
        with self.assertRaises(ConstructNotFoundError):
            self.transformer.container_type(token)

    def test_regex_type(self):
        token = 'test{1}'
        expected_regex_str = re.compile('test{1}')

        rule_type = self.transformer.regex_type((token, ))
        self.assertEqual(expected_regex_str, rule_type.regex)
        self.assertEqual(rule_type.schema_type, SchemaTypes.REGEX)

    def test_type(self):
        type_token = self.transformer.type((self.name_token, ))
        self.assertEqual(self.name_token, type_token)

    def test_schema_entry(self):
        expected_ruleset_name = 'main'
        tokens = (*self.ruleset_rules, )
        ruleset = self.transformer.schema_entry(tokens)

        self.assertEqual(expected_ruleset_name, ruleset.name)
        self.assertEqual(len(self.ruleset_rules), len(ruleset.rules))
        self.assertFalse(ruleset.is_strict)

    def test_strict_schema_entry(self):
        expected_ruleset_name = 'main'
        tokens = (*self.ruleset_rules, )
        ruleset = self.transformer.strict_schema_entry(tokens)

        self.assertEqual(expected_ruleset_name, ruleset.name)
        self.assertEqual(len(self.ruleset_rules), len(ruleset.rules))
        self.assertTrue(ruleset.is_strict)

    def test_int_transform(self):
        expected_value = 42
        actual_value = self.transformer.integer('42')
        self.assertEqual(expected_value, actual_value)

    def test_float_transform(self):
        expected_value = 3.142
        actual_value = self.transformer.float('3.142')
        self.assertEqual(expected_value, actual_value)

    @parameterized.expand([
        ('string_with_double_speech_marks', '\'hello\'', 'hello'),
        ('string_with_single_speech_marks', '\'hello\'', 'hello'),
        ('string_without_speech_marks', 'hello', 'hello'),
        ('empty_string', '', '')
    ])
    def test_escaped_string_transform(self, name: str, string_token: str,
                                      expected: str):
        # Unused by test case, however is required by the parameterized library
        del name

        actual = self.transformer.string(string_token)
        self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()
