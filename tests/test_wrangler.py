import unittest
from yamler.wrangler import YamlerWrangler


class TestYamlerWrangler(unittest.TestCase):
    def setUp(self):
        self.instructions = {
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
            }
        }
        self.wrangler = YamlerWrangler(self.instructions)
        self.data = {'message': 'Hello World', 'number': 42}

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

    def test_wrangle_none_data_dict(self):
        with self.assertRaises(ValueError):
            self.wrangler.wrangle(None)

    def test_wrangle_with_rule_violations(self):
        data = {'name': 'Yamler', 'number': 34}
        expected_violations = 1
        violations = self.wrangler.wrangle(data)
        self._assert_violation_count(expected_violations, violations)

    def test_wrangle_with_no_rule_violations(self):
        data = {'message': 'Hello World', 'number': 42}
        expected_violations = 0
        violations = self.wrangler.wrangle(data)
        self._assert_violation_count(expected_violations, violations)


if __name__ == '__main__':
    unittest.main()
