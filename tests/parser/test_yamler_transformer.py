import unittest

from collections import namedtuple
from parameterized import parameterized
from yamler.exceptions import ConstructNotFoundError

from yamler.parser import YamlerTransformer
from yamler.types import EnumItem, Rule, RuleType
from yamler.types import YamlerEnum, YamlerRuleset, SchemaTypes


Token = namedtuple('Token', ['value'])


class TestYamlerTransformer(unittest.TestCase):
    def setUp(self):
        self.transformer = YamlerTransformer()
        self.name_token = Token('message')
        self.status_code_token = Token('StatusCode')

        self.str_rtype = RuleType(type=SchemaTypes.STR)
        self.ruleset_rules = [
            Rule('name', RuleType(type=SchemaTypes.STR), True),
            Rule('age', RuleType(type=SchemaTypes.INT), True),
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

    def test_start(self):
        # This will be zero since main is removed from the dict
        # when processed by the start transformer
        expected_ruleset_count = 0
        expected_enum_count = 1

        instructions = [
            YamlerEnum('StatusCode', {
                'success': EnumItem('SUCCESS', 'success'),
                'error': EnumItem('ERR', 'error')
            }),
            YamlerRuleset('main', [
                Rule('message', RuleType(type=SchemaTypes.STR), True)
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
        self.assertEqual(SchemaTypes.STR, str_rule_type.type)

    def test_int_type(self):
        int_rule_type = self.transformer.int_type(())
        self.assertEqual(SchemaTypes.INT, int_rule_type.type)

    def test_float_type(self):
        float_rule_type = self.transformer.float_type(())
        self.assertEqual(SchemaTypes.FLOAT, float_rule_type.type)

    def test_list_type(self):
        tokens = (self.str_rtype, )
        list_type = self.transformer.list_type(tokens)

        self.assertEqual(SchemaTypes.LIST, list_type.type)
        self.assertEqual(tokens[0], list_type.sub_type)

    def test_map_type(self):
        tokens = (self.str_rtype, )
        map_type = self.transformer.map_type(tokens)

        self.assertEqual(SchemaTypes.MAP, map_type.type)
        self.assertEqual(tokens[0], map_type.sub_type)

    def test_any_type(self):
        any_type = self.transformer.any_type(())
        self.assertEqual(SchemaTypes.ANY, any_type.type)

    def test_enum_item(self):
        enum_name = Token('StatusCode')
        enum_value = Token('success')

        tokens = (enum_name, enum_value)
        enum_item = self.transformer.enum_item(tokens)

        self.assertEqual(enum_name.value, enum_item.name)
        self.assertEqual(enum_value.value, enum_item.value)

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
        token = Token("Employee")
        self.transformer.seen_constructs = {'Employee': SchemaTypes.RULESET}
        rule = self.transformer.container_type(token)
        self.assertEqual(rule.type, SchemaTypes.RULESET)

    @parameterized.expand([
        ('with_existing_constructs', 'Employee', {
            'Details': SchemaTypes.RULESET,
            'Status': SchemaTypes.ENUM
        }),
        ('without_existing_constructs', 'Employee', {})
    ])
    def test_container_type_construct_does_not_exist(self, name: str, construct_name: str,
                                                     seen_constructs: dict):
        token = Token(name)
        self.transformer.seen_constructs = seen_constructs
        with self.assertRaises(ConstructNotFoundError):
            self.transformer.container_type(token)

    def test_type(self):
        type_token = self.transformer.type((self.name_token, ))
        self.assertEqual(self.name_token, type_token)

    def test_schema_entry(self):
        expected_ruleset_name = 'main'
        tokens = (*self.ruleset_rules, )
        ruleset = self.transformer.schema_entry(tokens)

        self.assertEqual(expected_ruleset_name, ruleset.name)
        self.assertEqual(len(self.ruleset_rules), len(ruleset.rules))


if __name__ == '__main__':
    unittest.main()
