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
    def required_rule(self, tokens):
        (name, rtype) = tokens
        return {
            "name": name.value,
            "rtype": rtype,
            "required": True
        }

    def optional_rule(self, tokens):
        (name, rtype) = tokens
        return{
            "name": name.value,
            "rtype": rtype,
            "required": False
        }

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

    def str_type(self, tokens):
        return {'type': str}

    def int_type(self, tokens):
        return {'type': int}

    def ruleset_type(self, tokens):
        (name, ) = tokens
        return {
            'type': 'ruleset',
            'lookup': name.value
        }

    def type(self, tokens):
        (t, ) = tokens
        return t

    list = list


class YamlerType:
    def __init__(self, rtype, ptype):
        self.rtype = rtype
        self.ptype = ptype

    def __str__(self):
        return self.rtype


class YamlerInt(YamlerType):
    def __init__(self):
        super(YamlerInt, self).__init__("int", int)


class YamlerStr(YamlerType):
    def __init__(self):
        super(YamlerStr, self).__init__("str", int)


class YamlerRulesetType(YamlerType):
    def __init__(self, name):
        self.ruleset_name = name
        super(YamlerRulesetType, self).__init__("ruleset", object)

    def __str__(self):
        return f"ruleset {self.ruleset_name}"


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
        # self.rules = self._generate_rules(rules)

    def _generate_rules(self, rules):
        rule_lookup = {}
        for rule in rules:
            rule_lookup[rule.name] = {
                'required': rule.required,
                'type': rule.rtype
            }
        return rule_lookup


class YamlerMainRuleset(YamlerRuleset):
    def __init__(self, rules):
        super(YamlerMainRuleset, self).__init__("main", rules)
