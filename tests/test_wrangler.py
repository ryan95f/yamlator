import unittest

from yamler.wrangler import Violation
from yamler.wrangler import YamlerWrangler
from yamler.wrangler import RequiredViolation
from yamler.wrangler import TypeViolation


class TestYamlerWrangler(unittest.TestCase):
    def setUp(self):
        self.flat_instructions = {
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
                        'required': True
                    }
                ]
            },
        }

        self.nested_instructions = {
            'main': {
                'rules': [
                    {
                        'name': 'message',
                        'rtype': {'type': str},
                        'required': False
                    },
                    {
                        'name': 'person',
                        'rtype': {
                            'type': 'ruleset',
                            'lookup': 'person'
                        },
                        'required': True
                    },
                    {
                        'name': 'otherPerson',
                        'rtype': {
                            'type': 'ruleset',
                            'lookup': 'person'
                        },
                        'required': False
                    }
                ]
            },
            "rules": {
                "person": {
                    "rules": [
                        {
                            'name': 'first_name',
                            'rtype': {'type': str},
                            'required': True
                        },
                        {
                            'name': 'surname',
                            'rtype': {'type': str},
                            'required': False
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
        self.wrangler = YamlerWrangler(self.flat_instructions)
        self.data = {'message': 'Hello World', 'number': 42}

        self.nested_wrangle = YamlerWrangler(self.nested_instructions)

    def test_create_wrangler_empty_instructions(self):
        expected_violations = 0
        wrangler = YamlerWrangler({})
        violations = wrangler.wrangle(self.data)

        self._assert_violation_count(expected_violations, violations)

    def _assert_violation_count(self, expected, violations):
        self.assertEqual(expected, len(violations))

    def test_create_wrangler_none_instructions(self):
        with self.assertRaises(ValueError):
            YamlerWrangler(None)

    def test_wrangle_empty_data_dict(self):
        expected_violations = 2
        violations = self.wrangler.wrangle({})

        self._assert_violation_count(expected_violations, violations)
        self._assert_key_name_violations("", "message",
                                         violations,
                                         RequiredViolation)

        self._assert_key_name_violations("", "number",
                                         violations,
                                         RequiredViolation)

    def _assert_key_name_violations(self, parent: str, key: str,
                                    violations: dict,
                                    violation_type: type):
        violation_key = f"{parent}#{key}"
        key_violation = violations.get(violation_key, None)
        msg = f"{violation_key} was not found in the violations"
        self.assertIsNotNone(key_violation, msg)

        is_type = type(key_violation) == violation_type
        msg = f"{key} was not a {violation_type.__name__}"
        self.assertTrue(is_type, msg)

    def test_wrangle_none_data_dict(self):
        with self.assertRaises(ValueError):
            self.wrangler.wrangle(None)

    def test_wrangle_with_rule_violations(self):
        data = {'name': 'Yamler', 'number': 34}
        expected_violations = 1
        violations = self.wrangler.wrangle(data)

        self._assert_violation_count(expected_violations, violations)
        self._assert_key_name_violations("", "message",
                                         violations,
                                         RequiredViolation)

    def test_wrangle_with_no_rule_violations(self):
        data = {'message': 'Hello World', 'number': 42}
        expected_violations = 0
        violations = self.wrangler.wrangle(data)

        self._assert_violation_count(expected_violations, violations)

    def test_wrangle_with_invalid_type_violations(self):
        data = {'message': 'Hello World', 'number': "42"}
        expected_violations = 1
        violations = self.wrangler.wrangle(data)

        self._assert_violation_count(expected_violations, violations)
        self._assert_key_name_violations("", "number", violations, TypeViolation)

    def test_wrangle_with_nested_ruleset_valid_data(self):
        data = {
            'message': 'Hello World',
            'person': {
                'first_name': 'Hello',
                'surname': 'World',
                'age': 100
            },
            'otherPerson': {
                'first_name': 'Hello',
                'surname': 'World',
                'age': 100
            }
        }
        expected_violations = 0
        violations = self.nested_wrangle.wrangle(data)

        self._assert_violation_count(expected_violations, violations)

    def test_wrangler_with_optionals_removed_from_data(self):
        data = {
            'message': 'Hello World',
            'person': {
                'first_name': 'Hello',
                'surname': 'World',
                'age': 100
            }
        }
        expected_violations = 0
        violations = self.nested_wrangle.wrangle(data)

        self._assert_violation_count(expected_violations, violations)

    def test_wrangler_with_ruleset_type_violation(self):
        data = {
            'message': 'Hello World',
            'person': {
                'first_name': 'Hello',
                'surname': 'World',
                'age': 100
            },
            'otherPerson': 43
        }
        expected_violations = 1
        violations = self.nested_wrangle.wrangle(data)

        self._assert_violation_count(expected_violations, violations)
        self._assert_key_name_violations("", "otherPerson",
                                         violations,
                                         TypeViolation)

    def test_wrangler_with_required_ruleset_violation(self):
        data = {
            'message': 'Hello World'
        }
        expected_violations = 1
        violations = self.nested_wrangle.wrangle(data)

        self._assert_violation_count(expected_violations, violations)
        self._assert_key_name_violations("", "person",
                                         violations,
                                         RequiredViolation)


if __name__ == '__main__':
    unittest.main()
