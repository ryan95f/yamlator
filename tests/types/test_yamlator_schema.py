"""Test cases for the YamlatorSchema class"""

import unittest

from yamlator.types import YamlatorSchema


class TestYamlatorSchema(unittest.TestCase):
    """Test cases for the YamlatorSchema class"""

    def test_schema_with_none_parameters(self):
        expected_rule_count = 0
        expected_rulesets = {}
        expected_enums = {}

        schema = YamlatorSchema(root=None, rulesets=None, enums=None)

        root = schema.root
        self.assertIsNotNone(root)
        self.assertEqual(expected_rule_count, len(root.rules))

        self.assertIsNotNone(expected_rulesets, schema.rulesets)
        self.assertIsNotNone(expected_enums, schema.enums)


if __name__ == '__main__':
    unittest.main()
