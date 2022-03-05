import unittest

from collections import namedtuple
from yamler.parser import YamlerTransformer
from yamler.types import EnumItem, Rule, RuleType, YamlerEnum, YamlerRuleSet


Token = namedtuple('Token', ['value'])


class TestYamlerTransformer(unittest.TestCase):
    def setUp(self):
        self.transformer = YamlerTransformer()

    def test_required_rule(self):
        rtype = RuleType(type=str)
        name = Token('message')
        tokens = (name, rtype)

        required_rule = self.transformer.required_rule(tokens)
        self.assertEqual(name.value, required_rule.name)
        self.assertTrue(required_rule.is_required)

    def test_optional_rule(self):
        rtype = RuleType(type=str)
        name = Token('message')
        tokens = (name, rtype)

        optional_rule = self.transformer.optional_rule(tokens)
        self.assertEqual(name.value, optional_rule.name)
        self.assertFalse(optional_rule.is_required)

    def test_ruleset(self):
        name = Token('person')
        rules = [
            Rule('name', RuleType(type=str), True),
            Rule('age', RuleType(type=int), True),
        ]
        tokens = (name, *rules)

        ruleset = self.transformer.ruleset(tokens)
        self.assertEqual(name.value, ruleset.name)
        self.assertEqual(len(rules), len(ruleset.rules))

    def test_main_ruleset(self):
        expected_ruleset_name = 'main'
        rules = [
            Rule('name', RuleType(type=str), True),
            Rule('age', RuleType(type=int), True),
        ]
        tokens = (*rules, )
        ruleset = self.transformer.main_ruleset(tokens)
        self.assertEqual(expected_ruleset_name, ruleset.name)
        self.assertEqual(len(rules), len(ruleset.rules))

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
            YamlerRuleSet('main', [
                Rule('message', RuleType(type=str), True)
            ])
        ]

        ruleset_items = self.transformer.start(instructions)
        rulesets = ruleset_items.get('rules')
        enums = ruleset_items.get('enums')
        self.assertIsNotNone(ruleset_items.get('main'))
        self.assertIsNotNone(rulesets)
        self.assertIsNotNone(enums)

        self.assertEqual(expected_enum_count, len(enums))
        self.assertEqual(expected_ruleset_count, len(rulesets))

    def test_str_type(self):
        str_rule_type = self.transformer.str_type(())
        self.assertEqual(str, str_rule_type.type)

    def test_int_type(self):
        int_rule_type = self.transformer.int_type(())
        self.assertEqual(int, int_rule_type.type)

    def test_ruleset_type(self):
        name = Token('message')
        ruleset_type = self.transformer.ruleset_type((name, ))
        self.assertEqual('ruleset', ruleset_type.type)
        self.assertEqual(name.value, ruleset_type.lookup)

    def test_enum(self):
        enum_items = [
            EnumItem('SUCCESS', 'success'),
            EnumItem('ERR', 'error')
        ]
        tokens = (Token('StatusCode'), *enum_items)
        enum = self.transformer.enum(tokens)
        self.assertIsNotNone(enum)
        self.assertEqual('StatusCode', enum.name)
        self.assertEqual(len(enum_items), len(enum.items))


if __name__ == '__main__':
    unittest.main()
