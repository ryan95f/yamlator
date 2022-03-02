from __future__ import annotations
from typing import Iterator
from lark import Lark
from lark import Transformer
from lark.exceptions import UnexpectedEOF

from yamler.wranglers import RuleSetWrangler

from .types import Rule
from .types import ContainerTypes
from .types import YamlerRuleSet
from .types import YamlerEnum
from .types import YamlerType
from .types import RuleType
from .types import EnumItem


_GRAMMER_FILE = "grammer.lark"


class YamlerParser:
    """Parsers a YAML file to generate the rules that will be
    applied against a YAML file
    """

    def __init__(self):
        """YamlerParser Constructor"""
        self._parser = Lark.open(_GRAMMER_FILE)
        self._transfomer = YamlerTransformer()

    def parse(self, text: str) -> dict:
        """Parses the yamler file contents to generate the rules

        Args:
            text (str): The content of the yamler file

        Returns:
            dict of the rules in a format that can be used
            to validate a YAML file
        """
        if text is None:
            raise ValueError("text cannot be None")

        try:
            tokens = self._parser.parse(text)
            return self._transfomer.transform(tokens)
        except UnexpectedEOF:
            return {}


class YamlerTransformer(Transformer):
    def __init__(self, visit_tokens: bool = True) -> None:
        super().__init__(visit_tokens)

    def required_rule(self, tokens):
        (name, rtype) = tokens
        return Rule(name.value, rtype, True)

    def optional_rule(self, tokens):
        (name, rtype) = tokens
        return Rule(name.value, rtype, False)

    def ruleset(self, tokens):
        name = tokens[0].value
        rules = tokens[1:]
        return YamlerRuleSet(name, rules)

    def main_ruleset(self, tokens):
        rules = tokens
        return YamlerRuleSet("main", rules)

    def start(self, instructions: Iterator[YamlerType]):
        root = None
        rules = {}
        enums = {}

        handler_chain = _RulesetInstructionHandler(rules)
        handler_chain.set_next_handler(_EnumInstructionHandler(enums))

        for instruction in instructions:
            handler_chain.handle(instruction)

        root = rules.get('main')
        del rules['main']

        return {
            'main': root,
            'rules': rules,
            'enums': enums
        }

    def str_type(self, _):
        return RuleType(type=str)

    def int_type(self, _):
        return RuleType(type=int)

    def ruleset_type(self, tokens):
        (name, ) = tokens
        return RuleType(type="ruleset", lookup=name.value)

    def list_type(self, tokens):
        return RuleType(type=list, sub_type=tokens[0])

    def map_type(self, tokens):
        return RuleType(type=dict, sub_type=tokens[0])

    def any_type(self, tokens):
        return RuleType(type='any')

    def enum_type(self, tokens):
        (name, ) = tokens
        return RuleType(type='enum', lookup=name.value)

    def enum_item(self, tokens):
        name, value = tokens
        return EnumItem(name=name.value, value=value.value)

    def enum(self, tokens):
        name = tokens[0]
        items = tokens[1:]
        enums = {}
        for item in items:
            enums[item.value] = item
        return YamlerEnum(name.value, enums)

    def type(self, tokens):
        (t, ) = tokens
        return t


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
