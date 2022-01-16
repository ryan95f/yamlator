from yamler.parser import YamlerMainRuleset
from yamler.parser import YamlerRuleset
from yamler.parser import YamlerRulesetType


class YamlerWrangler:
    def __init__(self, rules: dict, rulests):
        self.rules = rules
        self.rulesets = rulests

    def wrangle(self, yaml_data: dict) -> dict:
        violations = {}
        self._r_wrangle(yaml_data, self.rules, violations)
        return violations

    def _r_wrangle(self, data: dict, rules: dict, violations: dict):
        for name, rule in rules.items():
            required = rule.get('required')
            dtype = rule.get('type')                

            d = data.get(name, None)
            if d is not None and isinstance(dtype, YamlerRulesetType):
                r_name = dtype.ruleset_name
                r = self.rulesets.get(r_name).rules
                self._r_wrangle(d, r, violations)

            if d is None and not required:
                continue
            
            if d is None:
                violations[name] = {
                    "required": f"{name} is missing"
                }
        return violations

class RuleBuilder:
    def __init__(self, components):
        self._identify_components(components)
        self._rule_shake()


    def _identify_components(self, components):
        self.main = None
        self.rulesets = {}
        for item in components:
            if isinstance(item, YamlerMainRuleset):
                self.main = item
                continue
            
            if isinstance(item, YamlerRuleset):
                self.rulesets[item.name] = item

    def _rule_shake(self):
        self.rules = self.main.rules