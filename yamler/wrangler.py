class YamlerWrangler:
    """Reads the instructions from the parser to validate if a
    YAML file meets the define rules
    """

    def __init__(self, instructions: dict):
        """YamlerWrangler constructor

        Args:
            instructions (dict): Contains the main ruleset and a list of
                                 other rulesets

        Raises:
            ValueError: If instructions is None
        """
        if instructions is None:
            raise ValueError("instructions should not be None")

        self._instructions = instructions
        self._main = instructions.get('main', {})

    def wrangle(self, yaml_data: dict) -> dict:
        """Wrangle the YAML file to determine if there are any
        violations when compared to the rulesets

        Args:
            yaml_data (dict): The yaml data represented as a dict

        Returns:
            A `dict` of violations that were detected

        Raises:
            ValueError: If `yaml_data` is None
        """
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
                continue

            if sub_data is None and not required:
                continue

            if sub_data is None:
                sub = violations.get(name, {})
                sub["required"] = f"{name} is missing"
                violations[name] = sub
                continue
            
            t = rtype['type']
            if (type(sub_data) != t):
                sub = violations.get(name, {})
                sub["type"] = f"{name} should type({t.__name__})"
                violations[name] = sub

        return violations
