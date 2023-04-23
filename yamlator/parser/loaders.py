"""Maintains utility functions that can load Yamlator schemas,
load any import statements in the schema and checks for cycles
"""

import re
import os

from typing import Dict
from typing import List

from yamlator.utils import load_schema
from yamlator.types import RuleType
from yamlator.types import YamlatorSchema
from yamlator.types import YamlatorRuleset
from yamlator.types import YamlatorType
from yamlator.types import SchemaTypes
from yamlator.types import PartiallyLoadedYamlatorSchema
from yamlator.exceptions import ConstructNotFoundError
from yamlator.exceptions import CycleDependencyError
from yamlator.parser.core import parse_schema
from yamlator.parser.dependency import DependencyManager


_SLASHES_REGEX = re.compile(r'(?:\\{1}|\/{1})')


def parse_yamlator_schema(schema_path: str) -> YamlatorSchema:
    """Parses a Yamlator schema from a given path on the file system

    Args:
        schema_path (str): The file path to the schema file

    Returns:
        A `yamlator.types.YamlatorSchema` object that contains
        the contents of the schema file in a format that can
        be processed by Yamlator

    Raises:
        ValueError: If the schema path is `None`, not a string
            or is an empty string

        yamlator.exceptions.InvalidSchemaFilenameError: If the filename
            does not match a file with a `.ys` extension

        yamlator.exceptions.SchemaParseError: Raised when the parsing
            process is interrupted

        yamlator.parser.SchemaSyntaxError: Raised when a syntax error
            is detected in the schema
    """
    if (schema_path is None) or (not isinstance(schema_path, str)):
        raise ValueError('Expected parameter schema_path to be a string')

    schema_content = load_schema(schema_path)

    dependencies = DependencyManager()
    schema_hash = dependencies.add(schema_content)

    schema = parse_schema(schema_content)
    context = fetch_schema_path(schema_path)
    schema = load_schema_imports(schema, context, schema_hash, dependencies)
    return schema


def fetch_schema_path(schema_path: str) -> str:
    """Fetches the current path for a schema file

    Args:
        schema_path (str): The path to the Yamlator schema file

    Returns:
        A string of the path that hosts the schema file

    Raises:
        ValueError: If the parameter `schema_path` is `None` or not
            a string
    """
    if not schema_path:
        raise ValueError(
            'Expected parameter schema_path to be a non-empty string')

    if not isinstance(schema_path, str):
        raise TypeError('Expected parameter schema_path to be a string')

    context = _SLASHES_REGEX.split(schema_path)[:-1]
    if not context:
        return '.'
    return _SLASHES_REGEX.sub('/', os.path.join(*context))


def load_schema_imports(loaded_schema: PartiallyLoadedYamlatorSchema,
                        schema_path: str,
                        parent_hash: str,
                        dependencies: DependencyManager) -> YamlatorSchema:
    """Loads all import statements that have been defined in a Yamlator
    schema file. This function will automatically load any subsequent import
    statements from child schema files

    Args:
        loaded_schema (yamlator.types.PartiallyLoadedYamlatorSchema): A schema
            that has been partially loaded by the Lark transformer but has
            not had all the imports resolved

        context (str): The path that contains the Yamlator schema file

        parent_hash (str): A string hash of the parent of this schema

        dependencies (yamlator.parser.dependency.DependencyManager): A utility
            class that represents dependencies as a graph which can
            be used to detect cycles

    Returns:
        A `yamlator.types.YamlatorSchema` object that has all the types
        resolved

    Raises:
        ValueError: If the `schema_path` is None, not a string or
            `loaded_schema` is `None`

        yamlator.exceptions.InvalidSchemaFilenameError: If the filename
            does not match a file with a `.ys` extension

        yamlator.exceptions.SchemaParseError: Raised when the parsing
            process is interrupted

        yamlator.parser.SchemaSyntaxError: Raised when a syntax error
            is detected in the schema

        yamlator.parser.CycleDependencyError: Raised if a cycle was deteted
            when loading a schema and its imported child schema files
    """
    if loaded_schema is None:
        raise ValueError('Parameter loaded_schema should not None')

    if not schema_path:
        raise ValueError(
            'Expected parameter schema_path to be a non-empty string')

    if not isinstance(schema_path, str):
        raise TypeError('Expected parameter schema_path to be a string')

    if not isinstance(loaded_schema, PartiallyLoadedYamlatorSchema):
        raise TypeError('Expected schema to be yamlator.types.PartiallyLoadedYamlatorSchema')  # nopep8 pylint: disable=C0301

    import_statements = loaded_schema.imports
    root_rulesets = loaded_schema.rulesets
    root_enums = loaded_schema.enums

    for path, resource_type in import_statements.items():
        full_path = os.path.join(schema_path, path)

        schema = _load_child_schema(full_path, parent_hash, dependencies)

        imported_rulesets = schema.rulesets
        imported_enums = schema.enums

        for (resource, namespace) in resource_type:
            has_mapped_rulesets = map_imported_resource(
                namespace,
                resource,
                root_rulesets,
                imported_rulesets
            )

            if has_mapped_rulesets:
                continue

            map_imported_resource(
                namespace,
                resource,
                root_enums,
                imported_enums
            )

    unknown_types = loaded_schema.unknowns_rule_types
    resolve_unknown_types(unknown_types, root_rulesets, root_enums)

    root_rulesets = resolve_ruleset_inheritance(root_rulesets)
    return YamlatorSchema(loaded_schema.root, root_rulesets, root_enums)


def _load_child_schema(schema_path: str, parent_hash: str,
                       dependencies: DependencyManager) -> YamlatorSchema:
    schema_content = load_schema(schema_path)
    schema_hash = dependencies.add(schema_content)

    dependencies.add_child(parent_hash, schema_hash)

    if dependencies.has_cycle():
        message = f'A cycle was detected when loading {schema_path}'
        raise CycleDependencyError(message)

    parsed_schema = parse_schema(schema_content)

    context = fetch_schema_path(schema_path)
    schema = load_schema_imports(parsed_schema, context,
                                 parent_hash, dependencies)
    return schema


def map_imported_resource(namespace: str, resource_type: str,
                          resource_lookup: dict,
                          imported_resources: dict) -> dict:
    """Maps the imported resources to the `resource_lookup` dictionary so that
    the resource can be used in the schema that imported the type

    Args:
        namespace (str): The namespace given in the schema when importing
            the resource. If the namespace is `None` then a namespace
            was not used in the schema

        resource_type (str): The resource type name. E.g if we had a ruleset
            or enum defined in the schema, it may be called `Foo`.

        resource_lookup (dict): A reference to a `dict` that requires the
            resource to be mapped to the `resource_type` and/or `namespace

        imported_resources (dict): A `dict` containing imported resources
            from an imported schema. The parameter `resource_type` is used
            to find the resource in `imported_resources`

    Returns:
        True if the imported type was successfully added to the
        `resource_lookup` otherwise returns False to indicate
        it could not find the resource in `imported_resources`

    Raises:
        ValueError: If the `resource_type`, `resource_lookup` or
            `imported_resources` is `None`

        TypeError: if `resource_lookup` or `imported_resources` is
            not a `dict`
    """
    if resource_type is None:
        raise ValueError('Parameter resource_type should not be None')

    if resource_lookup is None:
        raise ValueError('Parameter resource_lookup should not be None')

    if imported_resources is None:
        raise ValueError('Parameter imported_resources should not be None')

    if not isinstance(resource_lookup, dict):
        raise TypeError('Parameter resource_lookup should be a dictionary')

    if not isinstance(imported_resources, dict):
        raise TypeError('Parameter imported_resources should be a dictionary')

    imported_type: YamlatorType = imported_resources.get(resource_type)
    if imported_type is None:
        return False

    if namespace is not None:
        resource_type = f'{namespace}.{resource_type}'

    resource_lookup[resource_type] = imported_type
    return True


def resolve_unknown_types(unknown_types: List[RuleType],
                          rulesets: dict, enums: dict) -> bool:
    """Resolves any types that are marked as unknown since the ruleset
    or enum was imported into the schema. This function will go through
    each unknown type and populate with the relevant rule type

    Args:
        unknown_types (list[yamlator.types.RuleType]): A list of types that
            have a `schema_type` as `SchemaType.UNKNOWN`

        rulesets (dict): A dictionary of rulesets that have been loaded from
            the import statement defined in the schema

        enums (dict): A dictionary of enums that have been loaded from the
            import statements defined in the schema

    Returns:
        A boolean (true) to indicate it has executed successfully

    Raises:
        yamlator.exceptions.ConstructNotFoundError: If the ruleset or enum
            type was not found
    """
    if unknown_types is None:
        raise ValueError('Expected parameter unknown_types to not be None')

    if not isinstance(unknown_types, list):
        raise TypeError('Expected unknown_types to be a list')

    if (rulesets is None) or (enums is None):
        raise ValueError(
            'Expected parameters rulesets and enums to not be None')

    if (not isinstance(rulesets, dict)) or (not isinstance(enums, dict)):
        raise TypeError(
            'Expected parameters rulesets and enums to be dictionaries')

    while len(unknown_types) > 0:
        curr: RuleType = unknown_types.pop()
        if enums.get(curr.lookup) is not None:
            curr.schema_type = SchemaTypes.ENUM
            continue

        if rulesets.get(curr.lookup) is not None:
            curr.schema_type = SchemaTypes.RULESET
            continue

        raise ConstructNotFoundError(curr.lookup)
    return True


def resolve_ruleset_inheritance(rulesets: Dict[str, YamlatorRuleset]) -> dict:
    """Resolves any rulesets that have a parent ruleset defined in the schema.
    For example:

    ```text
    ruleset Foo(Bar) {
        ...
    }
    ```

    This function will extract all the rules defined in parent ruleset (`Bar`)
    and include them in the `Foo` ruleset. If both parent and child have a rule
    with the same name, the child rule will been used.

    Args:
        rulesets (dict): The rulesets defined in the schema where the key is the
            type and the value is a `yamlator.types.YamlatorRuleset`

    Returns:
        A dictionary where all the rulesets parent dependencies have been
        resolved by merging the parent rules in the child rules

    Raises:
        ValueError: If the ruleset parameter is `None`
        TypeError: If the ruleset parameter is not a `dict`
        yamlator.exceptions.ConstructNotFoundError: If a parent ruleset
            that is being inherited cannot be found in the `rulesets` parameter
        yamlator.exceptions.CycleDependencyError: If there is a cycle in the
            inheritance chain
    """
    if rulesets is None:
        raise ValueError('Parameter rulesets cannot be None')

    if not isinstance(rulesets, dict):
        raise TypeError(
            'Parameter rulesets cannot be None should be a dictionary')

    updated_rulesets = {}

    dependencies_mgmr = DependencyManager()
    for key, ruleset in rulesets.items():
        parent = ruleset.parent
        if not parent:
            updated_rulesets[key] = ruleset
            continue

        if rulesets.get(parent.lookup) is None:
            raise ConstructNotFoundError(parent)

        dependencies_mgmr.add_child(key, ruleset.parent.lookup)

    if dependencies_mgmr.has_cycle():
        msg = 'Detected cycle when resolving inheritance chain'
        raise CycleDependencyError(msg)

    dependencies = dependencies_mgmr.graph
    for node in dependencies:
        if updated_rulesets.get(node) is not None:
            continue

        stack = [(node, None)]
        while len(stack) > 0:
            curr_node, curr_ruleset = stack.pop()

            if curr_ruleset is not None:
                parent_node, _ = stack.pop()
                parent_ruleset = rulesets[parent_node]
                updated_rulesets[parent_node] = _merge_rulesets(parent_ruleset,
                                                                curr_ruleset)
                if len(stack) > 1:
                    stack.append((parent_node, updated_rulesets[parent_node]))
                continue

            if updated_rulesets.get(curr_node) is not None:
                stack.append((curr_node, updated_rulesets[curr_node]))
                continue

            stack.append((curr_node, None))
            stack.append((dependencies[curr_node][0], None))

    return updated_rulesets


def _merge_rulesets(ruleset: YamlatorRuleset,
                    dependent_ruleset: YamlatorRuleset) -> YamlatorRuleset:
    base_rules = ruleset.rules.copy()
    dependent_rules = dependent_ruleset.rules.copy()

    # Index the rules in the base and dependent rulesets to make it
    # easier to merge the different rules together
    base_rules_index = {rule.name: rule for rule in base_rules}
    dependent_rules_index = {rule.name: rule for rule in dependent_rules}

    # Merged the 2 rule lists together. If a rule name is present
    # in both then the base rules will be prioritized since it assumed
    # it is being overridden
    merged_rules = list({**dependent_rules_index, **base_rules_index}.values())
    return YamlatorRuleset(
        name=ruleset.name,
        rules=merged_rules,
        is_strict=ruleset.is_strict
    )
