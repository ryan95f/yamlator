import os

from yamlator.utils import load_schema
from yamlator.types import RuleType
from yamlator.types import YamlatorSchema
from yamlator.types import YamlatorRuleset
from yamlator.types import YamlatorEnum
from yamlator.types import SchemaTypes
from yamlator.types import LoadedYamlatorSchema
from yamlator.parser.core import parse_schema
from yamlator.exceptions import ConstructNotFoundError


def parse_yamlator_schema(schema_path: str) -> YamlatorSchema:
    root_schema_content = load_schema(schema_path)
    root_schema = parse_schema(root_schema_content)

    context = fetch_root_schema_context(schema_path)
    instructions = load_schema_imports(root_schema, context)
    return instructions


def fetch_root_schema_context(schema_path: str) -> str:
    context = schema_path.split('\\')[:-1]
    return os.path.join(*context)


def load_schema_imports(root_schema: LoadedYamlatorSchema,
                         context: str) -> YamlatorSchema:
    if root_schema is None:
        raise ValueError('root_schema should not None')

    import_statements = root_schema.imports
    root_rulesets = root_schema.rulesets
    root_enums = root_schema.enums

    for path, resource_type in import_statements.items():
        full_path = os.path.join(context, path)
        schema = parse_yamlator_schema(full_path)

        imported_rulesets = schema.rulesets
        imported_enums = schema.enums

        for resource in resource_type:
            ruleset: YamlatorRuleset = imported_rulesets.get(resource)
            if ruleset is not None:
                root_rulesets[ruleset.name] = ruleset
                continue

            enum: YamlatorEnum = imported_enums.get(resource)
            if enum is not None:
                root_enums[enum.name] = enum
                continue

    unknown_types = root_schema.unknowns_rule_types
    ruleset, enums = resolve_unknown_types(unknown_types,
                                           root_rulesets, root_enums)
    return YamlatorSchema(root_schema.root, ruleset, enums)


def resolve_unknown_types(unknown_types: list, rulesets: dict, enums: dict):
    while len(unknown_types) > 0:
        curr: RuleType = unknown_types.pop()
        if enums.get(curr.lookup) is not None:
            curr.schema_type = SchemaTypes.ENUM
            continue

        if rulesets.get(curr.lookup) is not None:
            curr.schema_type = SchemaTypes.RULESET
            continue

        raise ConstructNotFoundError(curr.lookup)
    return rulesets, enums
