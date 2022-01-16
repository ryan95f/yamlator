from yamler.parser import YamlerMainRuleset
from yamler.parser import YamlerRuleset
from yamler.parser import YamlerRulesetType


class YamlerWrangler:
    def __init__(self, rules: dict, rulests):
        self.rules = rules
        self.rulesets = rulests

    def wrangle(self, yaml_data: dict) -> dict:
        violations = {}
        for rule, config in self.rules.items():
            required = config.get('required')
            dtype = config.get('type')

            d = yaml_data.get(rule, None)
            if d is not None:
                print(type(d))

            if d is None and not required:
                continue
            
            if d is None:
                violations[rule] = {
                    "required": f"{rule} is missing"
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