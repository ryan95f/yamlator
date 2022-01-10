class YamlerWrangler:
    def __init__(self, rules: dict):
        self.rules = rules

    def wrangle(self, yaml_data: dict) -> dict:
        violations = {}
        for rule, required in self.rules.items():
            d = yaml_data.get(rule, None)
            if d is None and not required:
                continue
            
            if d is None:
                violations[rule] = {
                    "required": f"{rule} is missing"
                }
        return violations
