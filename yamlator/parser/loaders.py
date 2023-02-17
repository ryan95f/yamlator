import os

from yamlator.utils import load_schema
from yamlator.types import YamlatorSchema
from yamlator.parser.core import parse_schema


def parse_yamlator_schema(schema_path: str) -> YamlatorSchema:
    root_schema_content = load_schema(schema_path)
    root_schema = parse_schema(root_schema_content)

    context = fetch_root_schema_context(schema_path)

    instructions = load_child_resources(root_schema, context)
    return instructions


def fetch_root_schema_context(schema_path: str) -> str:
    context = schema_path.split('\\')[:-1]
    return os.path.join(*context)


def load_child_resources(root_schema, context):
    import_statements = root_schema.imports
    for path, items in import_statements.items():
        full_path = os.path.join(context, path)
        schema = load_schema(full_path)
        parsed_schema = parse_schema(schema)
        rulesets = parsed_schema.rulesets

        for item in items:
            item = rulesets.get(item)
            root_schema.rulesets[item.name] = item
    return root_schema
