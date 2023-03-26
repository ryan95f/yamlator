"""Contains constants for the test files paths"""

_BASE_INVALID_PATH = './tests/files/invalid_files'

INVALID_ENUM_NAME_SCHEMA = f'{_BASE_INVALID_PATH}/invalid_enum_name.ys'
INVALID_RULESET_NAME_SCHEMA = f'{_BASE_INVALID_PATH}/invalid_ruleset_name.ys'
INVALID_SYNTAX_SCHEMA = f'{_BASE_INVALID_PATH}/invalid_syntax.ys'
MISSING_RULESET_DEF_SCHEMA = f'{_BASE_INVALID_PATH}/missing_defined_ruleset.ys'
NESTED_UNION_SCHEMA = f'{_BASE_INVALID_PATH}/nested_union.ys'
MISSING_RULESET_RULES_SCHEMA = f'{_BASE_INVALID_PATH}/ruleset_missing_rules.ys'
MISSING_SCHEMA_RULES_SCHEMA = f'{_BASE_INVALID_PATH}/schema_missing_rules.ys'
SELF_CYCLE_SCHEMA = f'{_BASE_INVALID_PATH}/cycles/self_cycle.ys'
INVALID_YAML_DATA = f'{_BASE_INVALID_PATH}/invalid.yaml'

_BASE_VALID_PATH = './tests/files/valid'
VALID_YAML_DATA = f'{_BASE_VALID_PATH}/valid.yaml'
VALID_SCHEMA = f'{_BASE_VALID_PATH}/valid.ys'
VALID_KEYLESS_DIRECTIVE_SCHEMA = f'{_BASE_VALID_PATH}/keyless_directive.ys'
VALID_KEYLESS_RULES_SCHEMA = f'{_BASE_VALID_PATH}/keyless_and_standard_rules.ys'

# These files don't exists and are used to force specific errors in tests
NONE_PATH = None
EMPTY_PATH = ''
NOT_FOUND_SCHEMA = 'not_found.ys'
NOT_FOUND_YAML_DATA = 'not_found.yaml'
INVALID_SCHEMA_EXTENSION = './tests/files/hello.ruleset'
