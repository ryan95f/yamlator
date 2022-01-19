class YamlerWrangler:
    def __init__(self, instructions: dict):
        self.instructions = instructions
        self.main = instructions.get('main')

    def wrangle(self, yaml_data: dict) -> dict:
        violations = {}
        self._wrangle(yaml_data, self.main.get('rules'), violations)
        return violations

    def _wrangle(self, data: dict, rules: list, violations: dict):
        for rule in rules:
            name = rule.get('name')
            rtype = rule.get('rtype')
            required = rule.get('required')

            d = data.get(name, None)
            if d is not None and rtype['type'] == 'ruleset':
                r_name = rtype['lookup']
                r = self.instructions['rules'].get(r_name)
                self._wrangle(d, r['rules'], violations)

            if d is None and not required:
                continue

            if d is None:
                violations[name] = {
                    "required": f"{name} is missing"
                }
        return violations
