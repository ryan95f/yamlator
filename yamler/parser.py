from lark import Lark
from lark import Transformer

_GRAMMER_FILE = "grammer.lark"


class YamlerParser:    
    def __init__(self):
        self._parser = Lark.open(_GRAMMER_FILE)
        self._transfomer = YamlerTransformer()

    def parse(self, text):
        tokens = self._parser.parse(text)
        return self._transfomer.transform(tokens)


class YamlerTransformer(Transformer):
    def enum(self, tokens):
        return YamlerEnum(tokens[0], tokens[1])

    def number(self, number):
        (n, ) = number
        return int(n)

    def required_rule(self, tokens):
        (name, rtype) = tokens
        return YamlerRule(name.value, rtype, True)

    def optional_rule(self, tokens):
        (name, rtype) = tokens
        return YamlerRule(name.value, rtype, False)
        
    def ruleset(self, tokens):
        name = tokens[0].value
        rules = tokens[1:]
        return YamlerRuleset(name, rules)

    def main_ruleset(self, tokens):
        rules = tokens
        return YamlerMainRuleset(rules)

    def start(self, instructions):
        return list(instructions)

    list = list


class YamlerEnum:
    def __init__(self, name, values):
        self.name = name
        self.values = values

    def __str__(self):
        return f"{self.name} -> {self.values}"


class YamlerRule:
    def __init__(self, name, rtype, required=False):
        self.name = name
        self.rtype = rtype
        self.required = required

    def __str__(self):
        return f"{self.name} {self.rtype}({self.required})"


class YamlerRuleset:
    def __init__(self, name, rules):
        self.name = name
        self.rules = self._generate_rules(rules)
    
    def _generate_rules(self, rules):
        rule_lookup = {}
        for rule in rules:
            rule_lookup[rule.name] = {
                'required': rule.required
            }
        return rule_lookup

class YamlerMainRuleset(YamlerRuleset):
    def __init__(self, rules):
        super(YamlerMainRuleset, self).__init__("main", rules)