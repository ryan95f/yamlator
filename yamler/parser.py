from __future__ import annotations
from cProfile import label

import os
from pathlib import Path
from typing import Iterator
from lark import Lark, UnexpectedInput
from lark import Transformer
from lark.exceptions import VisitError

from yamler.types import Rule
from yamler.types import ContainerTypes
from yamler.types import YamlerRuleset
from yamler.types import YamlerEnum
from yamler.types import YamlerType
from yamler.types import RuleType
from yamler.types import EnumItem
from yamler.types import SchemaTypes
from yamler.exceptions import ConstructNotFoundError
from yamler.exceptions import YamlerParseError


_package_dir = Path(__file__).parent.absolute()
_GRAMMER_FILE = os.path.join(_package_dir, 'grammer/grammer.lark')


def parse_rulesets(ruleset_content: str) -> dict:
    """Parses a ruleset into a set of instructions that can be
    used to validate a YAML file.

    Args:
        ruleset_content (str): The string contnet of a ruleset schema

    Returns:
        A `dict` that contains the instructions to validate the YAML file

    Raises:
        ValueError: Raised when `ruleset_content` is `None`
        YamlerParseError: Raised when the parsing process is interrupted
        YamlerSyntaxError: Raised when a syntax error is detected in the schema
    """
    if ruleset_content is None:
        raise ValueError("ruleset_content should not be None")

    lark_parser = Lark.open(_GRAMMER_FILE)
    transformer = YamlerTransformer()

    try:
        tokens = lark_parser.parse(ruleset_content)
        return transformer.transform(tokens)
    except VisitError as ve:
        raise YamlerParseError(ve.__context__)
    except UnexpectedInput as u:
        _handle_syntax_errors(u, lark_parser, ruleset_content)


class YamlerTransformer(Transformer):
    seen_constructs = {}

    def __init__(self, visit_tokens: bool = True) -> None:
        super().__init__(visit_tokens)
        self.seen_constructs = {}

    def required_rule(self, tokens):
        (name, rtype) = tokens
        return Rule(name.value, rtype, True)

    def optional_rule(self, tokens):
        (name, rtype) = tokens
        return Rule(name.value, rtype, False)

    def ruleset(self, tokens):
        name = tokens[0].value
        rules = tokens[1:]
        self.seen_constructs[name] = SchemaTypes.RULESET
        return YamlerRuleset(name, rules)

    def start(self, instructions: Iterator[YamlerType]):
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

    def str_type(self, _):
        return RuleType(type=SchemaTypes.STR)

    def int_type(self, _):
        return RuleType(type=SchemaTypes.INT)

    def float_type(self, _):
        return RuleType(type=SchemaTypes.FLOAT)

    def list_type(self, tokens):
        return RuleType(type=SchemaTypes.LIST, sub_type=tokens[0])

    def map_type(self, tokens):
        return RuleType(type=SchemaTypes.MAP, sub_type=tokens[0])

    def any_type(self, tokens):
        return RuleType(type=SchemaTypes.ANY)

    def enum_item(self, tokens):
        name, value = tokens
        return EnumItem(name=name.value, value=value.value)

    def enum(self, tokens):
        enums = {}

        name = tokens[0]
        items = tokens[1:]

        for item in items:
            enums[item.value] = item
        self.seen_constructs[name] = SchemaTypes.ENUM
        return YamlerEnum(name.value, enums)

    def container_type(self, token):
        name = token[0]
        schema_type = self.seen_constructs.get(name)
        if schema_type is None:
            raise ConstructNotFoundError(name)
        return RuleType(type=schema_type, lookup=name)

    def type(self, tokens):
        (t, ) = tokens
        return t

    def schema_entry(self, tokens):
        return YamlerRuleset('main', tokens)


class _InstructionHandler:
    _next_handler = None

    def set_next_handler(self, handler: _InstructionHandler) -> _InstructionHandler:
        self._next_handler = handler
        return handler

    def handle(self, instruction: YamlerType) -> None:
        if self._next_handler is not None:
            self._next_handler.handle(instruction)


class _EnumInstructionHandler(_InstructionHandler):
    def __init__(self, enums: dict):
        super().__init__()
        self._enums = enums

    def handle(self, instruction: YamlerType) -> None:
        if instruction.type != ContainerTypes.ENUM:
            super().handle(instruction)
            return

        self._enums[instruction.name] = instruction


class _RulesetInstructionHandler(_InstructionHandler):
    def __init__(self, rulesets: dict):
        super().__init__()
        self._rulesets = rulesets

    def handle(self, instruction: YamlerType) -> None:
        if instruction.type != ContainerTypes.RULESET:
            super().handle(instruction)
            return

        self._rulesets[instruction.name] = instruction


class YamlerSyntaxError(SyntaxError):
    """A generic syntax error in the Yamler content"""

    label = None

    def __str__(self) -> str:
        context, line, column = self.args
        if self.label is None:
            return f'Error on line {line}, column {column}.\n\n{context}'
        return f'{self.label} at line {line}, column {column}.\n\n{context}'


class YamlerMalformedRulesetName(YamlerSyntaxError):
    label = 'Invalid ruleset name'


class YamlerMalformedEnumName(YamlerSyntaxError):
    label = 'Invalid enum name'


class YamlerMissingRules(YamlerSyntaxError):
    label = 'Missing rules'


def _handle_syntax_errors(u: UnexpectedInput, parser: Lark, content: str):
    exc_class = u.match_examples(parser.parse, {
        YamlerMalformedRulesetName: [
            'ruleset foo',
            'ruleset 1234Foo',
            'ruleset FOO',
        ],
        YamlerMalformedEnumName: [
            'enum foo',
            'enum 1234Foo',
            'enum FOO',
        ],
        YamlerMissingRules: [
            'ruleset Foo {}',
            'schema {}'
        ]
    }, use_accepts=True)
    if not exc_class:
        raise YamlerSyntaxError(u.get_context(content), u.line, u.column)
    raise exc_class(u.get_context(content), u.line, u.column)
