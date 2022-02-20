from lark import Lark
from lark import Transformer
from lark.exceptions import UnexpectedEOF

from .types import Rule
from .types import RuleType


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
    def required_rule(self, tokens):
        (name, rtype) = tokens
        return Rule(name.value, rtype, True)

    def optional_rule(self, tokens):
        (name, rtype) = tokens
        return Rule(name.value, rtype, False)

    def ruleset(self, tokens):
        name = tokens[0].value
        rules = tokens[1:]
        return {
            "name": name,
            "rules": rules
        }

    def main_ruleset(self, tokens):
        rules = tokens
        return {
            'name': 'main',
            'rules': rules
        }

    def start(self, instructions):
        root = None
        rules = {}
        for instruction in instructions:
            name = instruction.get('name')
            if name == 'main':
                root = instruction
            else:
                rules[name] = instruction
        return {
            'main': root,
            'rules': rules
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

    def type(self, tokens):
        (t, ) = tokens
        return t

    list = list
