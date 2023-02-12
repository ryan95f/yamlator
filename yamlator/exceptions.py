"""Yamlator exceptions"""


class InvalidSchemaFilenameError(RuntimeError):
    """When the schema filename does not match the expected regex pattern"""

    def __init__(self, filename: str):
        """InvalidSchemaFilenameError init

        Args:
            filename (str): The filename that was invalid
        """
        message = f'{filename} is not a valid Yamlator schema filename'
        super().__init__(message)


class ConstructNotFoundError(RuntimeError):
    """Represents a enum or ruleset not being found during the
    schema parsing process
    """

    def __init__(self, construct_name: str):
        """ConstructNotFoundError init

        Args:
            construct_name (str): The name of the Enum or Ruleset construct
        """
        message = f'Type {construct_name} was not found in the schema definition'  # nopep8 pylint: disable=C0301
        super().__init__(message)


class SchemaParseError(RuntimeError):
    """Represents a parse error when reading the schema"""
    pass


class NestedUnionError(RuntimeError):
    """When a union has another union nested within it"""

    def __init__(self):
        """NestedUnionError init"""

        message = 'Unions cannot have a union nested within it'
        super().__init__(message)
