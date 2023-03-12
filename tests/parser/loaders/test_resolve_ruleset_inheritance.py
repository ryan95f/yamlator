"""Test cases for the `resolve_ruleset_inheritance` function"""

import unittest

from typing import Any
from parameterized import parameterized

from yamlator.types import Rule
from yamlator.types import RuleType
from yamlator.types import SchemaTypes
from yamlator.types import YamlatorRuleset
from yamlator.exceptions import ConstructNotFoundError
from yamlator.parser.loaders import resolve_ruleset_inheritance


class TestResolveRulesetInheritance(unittest.TestCase):
    """Test cases for the `resolve_ruleset_inheritance` function"""

    @parameterized.expand([
        ('with_none_rulesets', None, ValueError),
        ('with_rulesets_as_a_list', [], TypeError),
        ('with_rulesets_as_a_string', 'Foo', TypeError),
        ('with_unknown_ruleset', {
            'Foo': YamlatorRuleset(
                name='Foo',
                rules=[],
                is_strict=False,
                parent=RuleType(SchemaTypes.RULESET, lookup='Bar')
            )
        }, ConstructNotFoundError)
    ])
    def test_resolve_ruleset_raises_error(self, name: str, rulesets: Any,
                                          expected_exception: Exception):
        del name

        with self.assertRaises(expected_exception):
            resolve_ruleset_inheritance(rulesets)

    def test_resolve_ruleset_inheritance(self):
        rulesets = {
            'Foo': YamlatorRuleset(
                name='Foo',
                rules=[
                    Rule('message', RuleType(SchemaTypes.STR), True),
                    Rule('name', RuleType(SchemaTypes.STR), True),
                    Rule('age', RuleType(SchemaTypes.INT), False)
                ],
                is_strict=False,
                parent=RuleType(SchemaTypes.RULESET, lookup='Bar')
            ),
            'Bar': YamlatorRuleset(
                name='Bar',
                rules=[
                    Rule('first_name', RuleType(SchemaTypes.STR), True),
                    Rule('last_name', RuleType(SchemaTypes.STR), True)
                ]
            )
        }
        expected_ruleset_count = 2
        expected_foo_rule_count = 5

        updated_rules = resolve_ruleset_inheritance(rulesets)

        actual_ruleset_count = len(updated_rules)
        actual_foo_rule_count = len(updated_rules['Foo'].rules)
        self.assertEqual(expected_ruleset_count, actual_ruleset_count)
        self.assertEqual(expected_foo_rule_count, actual_foo_rule_count)

    def test_resolve_ruleset_inheritance_parent_same_rule_name(self):
        rulesets = {
            'Foo': YamlatorRuleset(
                name='Foo',
                rules=[
                    Rule('message', RuleType(SchemaTypes.STR), True),
                    Rule('name', RuleType(SchemaTypes.STR), True),
                ],
                is_strict=False,
                parent=RuleType(SchemaTypes.RULESET, lookup='Bar')
            ),
            'Bar': YamlatorRuleset(
                name='Bar',
                rules=[
                    Rule('name', RuleType(SchemaTypes.FLOAT), True),
                ]
            )
        }
        expected_ruleset_count = 2
        expected_foo_rule_count = 2

        updated_rules = resolve_ruleset_inheritance(rulesets)
        foo_rules = updated_rules['Foo'].rules

        actual_ruleset_count = len(updated_rules)
        actual_foo_rule_count = len(foo_rules)
        self.assertEqual(expected_ruleset_count, actual_ruleset_count)
        self.assertEqual(expected_foo_rule_count, actual_foo_rule_count)

        # Extract the rule called name that is common in both rulesets above
        # and check that the type is a SchemaTypes.STR
        overridden_rule = [rule for rule in foo_rules if rule.name == 'name'][0]
        self.assertEqual(SchemaTypes.STR, overridden_rule.rtype.schema_type)

    def test_resolve_ruleset_inheritance_without_any_parents(self):
        rulesets = {
            'Foo': YamlatorRuleset(
                name='Foo',
                rules=[
                    Rule('message', RuleType(SchemaTypes.STR), True),
                    Rule('name', RuleType(SchemaTypes.STR), True),
                    Rule('age', RuleType(SchemaTypes.INT), False)
                ],
            ),
            'Bar': YamlatorRuleset(
                name='Bar',
                rules=[
                    Rule('first_name', RuleType(SchemaTypes.STR), True),
                    Rule('last_name', RuleType(SchemaTypes.STR), True)
                ]
            )
        }
        expected_ruleset_count = 2
        expected_foo_rule_count = 3

        updated_rules = resolve_ruleset_inheritance(rulesets)

        actual_ruleset_count = len(updated_rules)
        actual_foo_rule_count = len(updated_rules['Foo'].rules)
        self.assertEqual(expected_ruleset_count, actual_ruleset_count)
        self.assertEqual(expected_foo_rule_count, actual_foo_rule_count)


if __name__ == '__main__':
    unittest.main()
