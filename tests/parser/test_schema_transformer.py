"""Test cases for the `SchemaTransformer` class"""


import re
import unittest
import lark

from parameterized import parameterized
from yamlator.exceptions import NestedUnionError

from yamlator.parser import SchemaTransformer
from yamlator.types import EnumItem
from yamlator.types import Rule
from yamlator.types import RuleType
from yamlator.types import YamlatorEnum
from yamlator.types import YamlatorRuleset
from yamlator.types import SchemaTypes
from yamlator.parser.core import GrammarKeywords


class TestSchemaTransformer(unittest.TestCase):
    """Tests the SchemaTransformer class"""

    def setUp(self):
        self.transformer = SchemaTransformer()
        self.name_token = lark.Token(type_='NAME', value='message')
        self.status_code_token = lark.Token(type_='STATUS', value='StatusCode')

        self.str_rtype = RuleType(schema_type=SchemaTypes.STR)
        self.ruleset_rules = [
            Rule('name', RuleType(schema_type=SchemaTypes.STR), True),
            Rule('age', RuleType(schema_type=SchemaTypes.INT), True),
        ]

    @parameterized.expand([
        ('without_quotes', 'ruleName', 'ruleName'),
        ('with_double_quotes', '\"ruleName\"', 'ruleName'),
        ('with_single_quotes', '\'ruleName\'', 'ruleName'),
        ('with_spaces', 'rule name', 'rule name'),
        ('with_padding_spaces', '    rule name    ', 'rule name'),
    ])
    def test_rule_name(self, name: str, rule_name: str, expected: str):
        # Unused by test case, however is required by the parameterized library
        del name

        token = lark.Token('TOKEN', value=rule_name)
        processed_token = self.transformer.rule_name([token])
        self.assertEqual(expected, processed_token.value)

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
        name = lark.Token(type_='TOKEN', value='person')
        tokens = (name, *self.ruleset_rules)
        ruleset = self.transformer.ruleset(tokens)

        self.assertEqual(name.value, ruleset.name)
        self.assertEqual(len(self.ruleset_rules), len(ruleset.rules))
        self.assertFalse(ruleset.is_strict)
        self.assertIsNone(ruleset.parent)

    def test_ruleset_with_strict_token(self):
        strict_token = lark.Token(type_=GrammarKeywords.STRICT, value='')
        name = lark.Token(type_='TOKEN', value='person')
        tokens = (strict_token, name, *self.ruleset_rules)
        ruleset = self.transformer.ruleset(tokens)

        self.assertEqual(name.value, ruleset.name)
        self.assertEqual(len(self.ruleset_rules), len(ruleset.rules))
        self.assertTrue(ruleset.is_strict)
        self.assertIsNone(ruleset.parent)

    def test_ruleset_with_parent(self):
        strict_token = lark.Token(type_=GrammarKeywords.STRICT, value='')
        name = lark.Token(type_='TOKEN', value='person')
        parent = RuleType(SchemaTypes.RULESET, lookup='Foo')
        tokens = (strict_token, name, parent, *self.ruleset_rules)
        ruleset = self.transformer.ruleset(tokens)

        self.assertEqual(name.value, ruleset.name)
        self.assertEqual(len(self.ruleset_rules), len(ruleset.rules))
        self.assertTrue(ruleset.is_strict)
        self.assertIsNotNone(ruleset.parent)

    def test_ruleset_parent(self):
        parent_rule_type = RuleType(SchemaTypes.RULESET, lookup='Foo')
        result = self.transformer.ruleset_parent([parent_rule_type])
        self.assertEqual(parent_rule_type, result)

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

        schema = self.transformer.start(instructions)
        rulesets = schema.rulesets
        enums = schema.enums

        self.assertIsNotNone(schema.root)
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
        token = lark.Token(type_='TOKEN', value='Employee')
        self.transformer.seen_constructs = {'Employee': SchemaTypes.RULESET}
        rule = self.transformer.container_type([token])
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
        # Unused by test case, however is required by the parameterized library
        del name

        token = lark.Token(type_='TOKEN', value='Foo')
        self.transformer.seen_constructs = seen_constructs
        rule = self.transformer.container_type(token)
        self.assertEqual(SchemaTypes.UNKNOWN, rule.schema_type)

    def test_regex_type(self):
        token = 'test{1}'
        expected_regex_str = re.compile('test{1}')

        rule_type = self.transformer.regex_type((token, ))
        self.assertEqual(expected_regex_str, rule_type.regex)
        self.assertEqual(rule_type.schema_type, SchemaTypes.REGEX)

    def test_union_type(self):
        tokens = [
            RuleType(SchemaTypes.INT),
            RuleType(SchemaTypes.STR),
            RuleType(SchemaTypes.LIST, sub_type=RuleType(SchemaTypes.INT))
        ]

        union_type = self.transformer.union_type(tokens)
        self.assertIsNotNone(union_type)
        self.assertEqual(SchemaTypes.UNION, union_type.schema_type)

    def test_union_type_with_nested_union(self):
        tokens = [
            RuleType(SchemaTypes.INT),
            RuleType(SchemaTypes.STR),
            RuleType(SchemaTypes.LIST, sub_type=RuleType(SchemaTypes.INT)),
            RuleType(SchemaTypes.UNION)
        ]
        with self.assertRaises(NestedUnionError):
            self.transformer.union_type(tokens)

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

    def test_schema_entry_with_strict_token(self):
        expected_ruleset_name = 'main'
        strict_token = lark.Token(type_=GrammarKeywords.STRICT, value='')
        tokens = (strict_token, *self.ruleset_rules, )
        ruleset = self.transformer.schema_entry(tokens)

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
