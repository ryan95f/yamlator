class YamlerWrangler:
    def __init__(self, instructions: dict):
        if instructions is None:
            raise ValueError("instructions should not be None")

        self._instructions = instructions
        self._main = instructions.get('main', {})

    def wrangle(self, yaml_data: dict) -> dict:
        if yaml_data is None:
            raise ValueError("yaml_data should not be None")

        violations = {}
        main_rules = self._main.get('rules', [])
        self._wrangle(yaml_data, main_rules, violations)
        return violations

    def _wrangle(self, data: dict, rules: list, violations: dict):
        for rule in rules:
            name = rule.get('name')
            rtype = rule.get('rtype')
            required = rule.get('required')

            sub_data = data.get(name, None)
            if sub_data is not None and rtype['type'] == 'ruleset':
                ruleset_name = rtype['lookup']
                ruleset = self._instructions['rules'].get(ruleset_name)
                self._wrangle(sub_data, ruleset['rules'], violations)

            if sub_data is None and not required:
                continue

            if sub_data is None:
                violations[name] = {
                    "required": f"{name} is missing"
                }
        return violations
