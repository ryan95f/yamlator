"""Test cases for the load_schema_imports function"""
import hashlib
import unittest

from parameterized import parameterized

from yamlator.types import Rule
from yamlator.types import RuleType
from yamlator.types import SchemaTypes
from yamlator.types import ImportedType
from yamlator.types import YamlatorRuleset
from yamlator.types import PartiallyLoadedYamlatorSchema
from yamlator.parser.loaders import load_schema_imports
from yamlator.parser.dependency import DependencyManager
from yamlator.exceptions import CycleDependencyError
from yamlator.utils import load_schema


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
    def setUp(self):
        md5_digest = hashlib.md5('root'.encode('utf-8'))
        self.parent_hash = md5_digest.hexdigest()
        self.dependencies = DependencyManager()

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
            load_schema_imports(loaded_schema, schema_path,
                                self.parent_hash, self.dependencies)

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

        schema = load_schema_imports(loaded_schema, schema_path,
                                     self.parent_hash, self.dependencies)
        self.assertEqual(expected_ruleset_count, len(schema.rulesets))
        self.assertEqual(expected_enum_count, len(schema.enums))

    def test_load_schema_imports_cycle_raises_error(self):
        schema_path = './tests/files/invalid_files/cycles'
        unknown_types = [
            RuleType(SchemaTypes.UNKNOWN, lookup='core.Value'),
            RuleType(SchemaTypes.UNKNOWN, lookup='core.Status')
        ]

        # This schema is a representation of the file located in
        # './tests/files/invalid_files/cycles/root.ys' to help test
        # the function when a cycle is present
        loaded_schema = PartiallyLoadedYamlatorSchema(
            root=YamlatorRuleset('main', [
                Rule('project',
                     RuleType(
                        SchemaTypes.RULESET, lookup='Project'
                     ),
                     True),
                Rule('project',
                     RuleType(
                        SchemaTypes.RULESET, lookup='core.Values'
                     ),
                     True),
            ]),
            rulesets={
                'Project': YamlatorRuleset(
                    name='Project',
                    rules=[
                        Rule('version', RuleType(SchemaTypes.STR), True),
                        Rule('name', RuleType(SchemaTypes.STR), True),
                        Rule('status',
                             RuleType(
                                SchemaTypes.RULESET,
                                lookup='core.Status'),
                             False)
                    ]
                )
            },
            enums={},
            imports=[
                ImportedType('Value', 'common.ys', 'core'),
                ImportedType('Status', 'common.ys', 'core'),
            ],
            unknowns=unknown_types
        )

        # Load the actual schema file so the md5 hash can be extracted
        #  so subsequent load imports hashes match to detect the cycle
        file_path = f'{schema_path}/root.ys'
        schema = load_schema(file_path)
        schema_hash = self.dependencies.add(schema)

        with self.assertRaises(CycleDependencyError):
            load_schema_imports(loaded_schema, schema_path,
                                schema_hash, self.dependencies)

    def test_load_schema_self_cycle_raises_error(self):
        schema_path = './tests/files/invalid_files/cycles'

        # This schema is a representation of the file located in
        # './tests/files/invalid_files/cycles/self_cycle.ys' to help test
        # the function when a cycle is present
        loaded_schema = PartiallyLoadedYamlatorSchema(
            root=YamlatorRuleset('main', [
                Rule('test',
                     RuleType(
                        SchemaTypes.RULESET, lookup='Test'
                     ),
                     False),
            ]),
            rulesets={
                'Test': YamlatorRuleset(
                    name='Test',
                    rules=[
                        Rule('data', RuleType(SchemaTypes.STR), True),
                        Rule('number', RuleType(SchemaTypes.INT), True),
                    ]
                )
            },
            enums={},
            imports=[
                ImportedType('Test', 'self_cycle.ys'),
            ],
            unknowns=[]
        )

        # Load the actual schema file so the md5 hash can be extracted
        #  so subsequent load imports hashes match to detect the cycle
        file_path = f'{schema_path}/self_cycle.ys'
        schema = load_schema(file_path)
        schema_hash = self.dependencies.add(schema)

        with self.assertRaises(CycleDependencyError):
            load_schema_imports(loaded_schema, schema_path,
                                schema_hash, self.dependencies)

if __name__ == '__main__':
    unittest.main()
