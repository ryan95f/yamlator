"""Test cases for the load_schema_imports function"""

import unittest

from parameterized import parameterized

from yamlator.types import Rule
from yamlator.types import RuleType
from yamlator.types import SchemaTypes
from yamlator.types import ImportedType
from yamlator.types import YamlatorRuleset
from yamlator.types import PartiallyLoadedYamlatorSchema
from yamlator.parser.loaders import load_schema_imports


def create_basic_loaded_schema():
    root = YamlatorRuleset('main', [])
    return PartiallyLoadedYamlatorSchema(
        root=root,
        rulesets={},
        enums={},
        imports=[],
        unknowns=[]
    )


BASIC_SCHEMA = create_basic_loaded_schema()


class TestLoadSchemaImports(unittest.TestCase):
    """Test cases for the load_schema_imports function"""

    @parameterized.expand([
        ('with_none_schema', None, './path/test.ys', ValueError),
        ('with_wrong_schema_type', YamlatorRuleset('main', []),
            './path/test.ys', TypeError),
        ('with_none_schema_path', BASIC_SCHEMA, None, ValueError),
        ('with_wrong_schema_path_type_', BASIC_SCHEMA, ['test.ys'], TypeError),
        ('with_empty_schema_path_string', BASIC_SCHEMA, '', ValueError)
    ])
    def test_load_schema_imports_with_invalid_params(
            self, name: str,
            loaded_schema: PartiallyLoadedYamlatorSchema,
            schema_path: str, expected_exception: Exception):

        # Unused by test case, however is required by the parameterized library
        del name

        with self.assertRaises(expected_exception):
            load_schema_imports(loaded_schema, schema_path)

    def test_load_schema_imports(self):
        schema_path = './tests/files/valid'
        unknown_types = [
            RuleType(SchemaTypes.UNKNOWN, lookup='Employee'),
            RuleType(SchemaTypes.UNKNOWN, lookup='Status')
        ]

        loaded_schema = PartiallyLoadedYamlatorSchema(
            root=YamlatorRuleset('main', [
                Rule('employees',
                     RuleType(
                        SchemaTypes.LIST, sub_type=unknown_types[0]
                     ),
                     True),
                Rule('status', unknown_types[1], True)
            ]),
            rulesets={},
            enums={},
            imports=[
                ImportedType('Employee', 'base.ys'),
                ImportedType('User', 'base.ys'),
                ImportedType('Status', 'base.ys'),
            ],
            unknowns=unknown_types
        )

        expected_ruleset_count = 2
        expected_enum_count = 1

        schema = load_schema_imports(loaded_schema, schema_path)
        self.assertEqual(expected_ruleset_count, len(schema.rulesets))
        self.assertEqual(expected_enum_count, len(schema.enums))


if __name__ == '__main__':
    unittest.main()
