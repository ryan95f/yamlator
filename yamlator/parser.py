"""Maintains the parser transformers"""


from __future__ import annotations

import re
import os

from pathlib import Path
from typing import Iterator
from lark import Lark
from lark import v_args
from lark import Transformer
from lark import UnexpectedInput
from lark.exceptions import VisitError
from typing import Any

from yamlator.types import Rule
from yamlator.types import ContainerTypes
from yamlator.types import YamlatorRuleset
from yamlator.types import YamlatorEnum
from yamlator.types import YamlatorType
from yamlator.types import RuleType
from yamlator.types import EnumItem
from yamlator.types import SchemaTypes
from yamlator.exceptions import ConstructNotFoundError
from yamlator.exceptions import SchemaParseError


_package_dir = Path(__file__).parent.absolute()
_GRAMMAR_FILE = os.path.join(_package_dir, 'grammar/grammar.lark')

_SPEECH_MARKS_REGEX = re.compile(r'\"|\'')


def parse_schema(schema_content: str) -> dict:
    """Parses a schema into a set of instructions that can be
    used to validate a YAML file.

    Args:
        schema_content (str): The content of a schema

    Returns:
        A `dict` that contains the instructions to validate the YAML file

    Raises:
        ValueError: Raised when `schema_content` is `None`
        SchemaParseError: Raised when the parsing process is interrupted
        SchemaSyntaxError: Raised when a syntax error is detected in the schema
    """
    if schema_content is None:
        raise ValueError('schema_content should not be None')

    lark_parser = Lark.open(_GRAMMAR_FILE)
    transformer = SchemaTransformer()

    try:
        tokens = lark_parser.parse(schema_content)
        return transformer.transform(tokens)
    except VisitError as ve:
        raise SchemaParseError(ve) from ve
    except UnexpectedInput as u:
        _handle_syntax_errors(u, lark_parser, schema_content)


class SchemaTransformer(Transformer):
    """Transforms the schema contents into a set of objects that
    can be used to validate a YAML file. This class will be used by Lark
    during the parsing process.

    Each method matches to a terminal or rule in the grammar (.lark) file.
    E.g the method `required_rule` corresponds to the following rule
    in the grammar:

    required_rule: /[a-zA-Z0-9_]+/ type "required"
                 | /[a-zA-Z0-9_]+/ type
    """

    # Used to track previously seen enums or rulesets to dynamically
    # determine the type of the rule if a enum or ruleset is used
    seen_constructs = {}

    def required_rule(self, tokens: Any) -> Rule:
        """Transforms the required rule tokens in a Rule object"""
        (name, rtype) = tokens
        return Rule(name.value, rtype, True)

    def optional_rule(self, tokens: Any) -> Rule:
        """Transforms the optional rule tokens in a Rule object"""
        (name, rtype) = tokens
        return Rule(name.value, rtype, False)

    def ruleset(self, tokens: Any) -> YamlatorRuleset:
        """Transforms the ruleset tokens into a YamlatorRuleset object"""
        name = tokens[0].value
        rules = tokens[1:]
        self.seen_constructs[name] = SchemaTypes.RULESET
        return YamlatorRuleset(name, rules)

    def start(self, instructions: Iterator[YamlatorType]) -> dict:
        """Transforms the instructions into a dict that sorts the rulesets,
        enums and entry point to validate YAML data"""
        root = None
        rules = {}
        enums = {}

        handler_chain = _RulesetInstructionHandler(rules)
        handler_chain.set_next_handler(_EnumInstructionHandler(enums))

        for instruction in instructions:
            handler_chain.handle(instruction)

        root = rules.get('main')
        if root is not None:
            del rules['main']

        return {
            'main': root,
            'rules': rules,
            'enums': enums
        }

    def str_type(self, _: Any) -> RuleType:
        """Transforms a string type token into a RuleType object"""
        return RuleType(schema_type=SchemaTypes.STR)

    def int_type(self, _: Any) -> RuleType:
        """Transforms a int type token into a RuleType object"""
        return RuleType(schema_type=SchemaTypes.INT)

    def float_type(self, _: Any) -> RuleType:
        """Transforms a float type token into a RuleType object"""
        return RuleType(schema_type=SchemaTypes.FLOAT)

    def list_type(self, tokens: Any) -> RuleType:
        """Transforms a list type token into a RuleType object"""
        return RuleType(schema_type=SchemaTypes.LIST, sub_type=tokens[0])

    def map_type(self, tokens: Any) -> RuleType:
        """Transforms a map type token into a RuleType object"""
        return RuleType(schema_type=SchemaTypes.MAP, sub_type=tokens[0])

    def any_type(self, _: Any) -> RuleType:
        """Transforms the any type token into a RuleType object"""
        return RuleType(schema_type=SchemaTypes.ANY)

    def bool_type(self, _: Any) -> RuleType:
        """Transforms a bool type token into a RuleType object"""
        return RuleType(schema_type=SchemaTypes.BOOL)

    def enum_item(self, tokens: Any) -> EnumItem:
        """Transforms a enum item token into a EnumItem object"""
        name, value = tokens
        return EnumItem(name=name, value=value)

    def enum(self, tokens: Any) -> YamlatorEnum:
        """Transforms a enum token into a YamlatorEnum object"""
        enums = {}

        name = tokens[0]
        items = tokens[1:]

        for item in items:
            enums[item.value] = item
        self.seen_constructs[name] = SchemaTypes.ENUM
        return YamlatorEnum(name.value, enums)

    def container_type(self, token: Any) -> RuleType:
        """Transforms a container type token into a RuleType object

        Raises:
            ConstructNotFoundError: Raised if the enum or ruleset
            cannot be found
        """
        name = token[0]
        schema_type = self.seen_constructs.get(name)
        if schema_type is None:
            raise ConstructNotFoundError(name)
        return RuleType(schema_type=schema_type, lookup=name)

    def regex_type(self, tokens: Any) -> RuleType:
        """Transforms a regex type token into a RuleType object"""
        (regex, ) = tokens
        return RuleType(schema_type=SchemaTypes.REGEX, regex=regex)

    def type(self, tokens: Any) -> Any:
        """Extracts the type tokens and passes them through onto
        the next stage in the transformer
        """
        (t, ) = tokens
        return t

    def schema_entry(self, rules: list) -> YamlatorRuleset:
        """Transforms the schema entry point token into a YamlatorRuleset called
        main that will act as the entry point for validaiting the YAML data
        """
        return YamlatorRuleset('main', rules)

    @v_args(inline=True)
    def integer(self, token: str) -> int:
        """Convers a integer string into a int type"""
        return int(token)

    @v_args(inline=True)
    def float(self, token: str) -> float:
        """Convers a float string into a int type"""
        return float(token)

    @v_args(inline=True)
    def string(self, token: str) -> str:
        """Transforms the escaped string by removing speech
        marks from the value
        """
        return _SPEECH_MARKS_REGEX.sub('', token)


class _InstructionHandler:
    """Base handle for dealing with Yamlator types"""
    _next_handler = None

    def set_next_handler(self,
                         handler: _InstructionHandler) -> _InstructionHandler:
        """Set the next handler in the chain

        Args:
            handler: The next instruction handler

        Returns:
            The instance of the instruction handler that was
            passed as an argument
        """
        self._next_handler = handler
        return handler

    def handle(self, instruction: YamlatorType) -> None:
        if self._next_handler is not None:
            self._next_handler.handle(instruction)


class _EnumInstructionHandler(_InstructionHandler):
    """Enum type instruction handler"""

    def __init__(self, enums: dict):
        super().__init__()
        self._enums = enums

    def handle(self, instruction: YamlatorType) -> None:
        if instruction.container_type != ContainerTypes.ENUM:
            super().handle(instruction)
            return

        self._enums[instruction.name] = instruction


class _RulesetInstructionHandler(_InstructionHandler):
    """Ruleset type instruction handler"""

    def __init__(self, rulesets: dict):
        super().__init__()
        self._rulesets = rulesets

    def handle(self, instruction: YamlatorType) -> None:
        if instruction.container_type != ContainerTypes.RULESET:
            super().handle(instruction)
            return

        self._rulesets[instruction.name] = instruction


class SchemaSyntaxError(SyntaxError):
    """A generic syntax error in the schema content"""

    label = None

    def __str__(self) -> str:
        context, line, column, *_ = self.args
        if self.label is None:
            return f'Error on line {line}, column {column}.\n\n{context}'
        return f'{self.label} at line {line}, column {column}.\n\n{context}'


class MalformedRulesetNameError(SchemaSyntaxError):
    """Indicates an error in the ruleset name"""
    label = 'Invalid ruleset name'


class MalformedEnumNameError(SchemaSyntaxError):
    """Indicates an error in the enum name"""
    label = 'Invalid enum name'


class MissingRulesError(SchemaSyntaxError):
    """Indicates that a ruleset or schema block is missing rules"""
    label = 'Missing rules'


def _handle_syntax_errors(u: UnexpectedInput, parser: Lark,
                          content: str) -> None:
    exc_class = u.match_examples(parser.parse, {
        MalformedRulesetNameError: [
            'ruleset foo',
            'ruleset 1234Foo',
            'ruleset FOO',
        ],
        MalformedEnumNameError: [
            'enum foo',
            'enum 1234Foo',
            'enum FOO',
        ],
        MissingRulesError: [
            'ruleset Foo {}',
            'schema {}'
        ]
    }, use_accepts=True)
    if not exc_class:
        raise SchemaSyntaxError(u.get_context(content), u.line, u.column)
    raise exc_class(u.get_context(content), u.line, u.column)
