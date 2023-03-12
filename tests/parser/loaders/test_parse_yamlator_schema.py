"""Test cases for the parse_yamlator_schema function"""

import unittest
import typing

from parameterized import parameterized
from yamlator.exceptions import InvalidSchemaFilenameError
from yamlator.exceptions import SchemaParseError
from yamlator.parser import SchemaSyntaxError
from yamlator.parser import parse_yamlator_schema


class TestParseYamlatorSchema(unittest.TestCase):
    """Test cases for the parse_yamlator_schema function"""

    @parameterized.expand([
        ('with_none_path', None, ValueError),
        ('with_empty_string_path', '', ValueError),
        ('with_non_string_path', ['./path'], ValueError),
        ('with_none_ys_extension', 'schema.yaml', InvalidSchemaFilenameError),
        ('with_syntax_error',
            './tests/files/invalid_files/invalid_ruleset_name.ys',
            SchemaSyntaxError),
        ('with_schema_nested_union',
            './tests/files/invalid_files/nested_union.ys',
            SchemaParseError),
    ])
    def test_with_invalid_schema_paths(self, name: str,
                                       schema_path: typing.Any,
                                       expected_exception: Exception):
        # Unused by test case, however is required by the parameterized library
        del name

        with self.assertRaises(expected_exception):
            parse_yamlator_schema(schema_path)

    @parameterized.expand([
        ('without_any_imports', './tests/files/valid/valid.ys'),
        ('with_imports', './tests/files/valid/with_imports.ys'),
        ('with_namespace_imports',
            './tests/files/valid/with_import_and_namespaces.ys'),
        ('with_inheritance',
            './tests/files/valid/inheritance.ys'),
    ])
    def test_with_valid_schema_paths(self, name, schema_path):
        # Unused by test case, however is required by the parameterized library
        del name

        schema = parse_yamlator_schema(schema_path)
        self.assertIsNotNone(schema)


if __name__ == '__main__':
    unittest.main()
