from enum import Enum


class ViolationType(Enum):
    REQUIRED = "required",
    TYPE = "type"


class Violation:
    def __init__(self, message: str, v_type: ViolationType):
        self._message = message
        self.v_type = v_type

    @property
    def message(self):
        return self._message


class RequiredViolation(Violation):
    def __init__(self, message: str):
        super().__init__(message, ViolationType.REQUIRED)


class TypeViolation(Violation):
    def __init__(self, message: str):
        super().__init__(message, ViolationType.TYPE)


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

        self.violations = {}
        main_rules = self._main.get('rules', [])
        self._wrangle(yaml_data, main_rules)
        return self.violations

    def _wrangle(self, data: dict, rules: list, parent: str = ""):
        for rule in rules:
            name = rule.get('name')
            rtype = rule.get('rtype')
            required = rule.get('required')

            sub_data = data.get(name, None)
            if required and sub_data is None:
                msg = f"{name} is missing"
                self._update_violation(name, RequiredViolation(msg))
                continue

            if rtype['type'] == 'ruleset':
                if self._is_ruleset_type(sub_data):
                    ruleset_name = rtype['lookup']
                    ruleset = self._instructions['rules'].get(ruleset_name)
                    self._wrangle(sub_data, ruleset['rules'], name)
                    continue
                else:
                    msg = f"{name} should be type(ruleset)"
                    self._update_violation(name, TypeViolation(msg))
            else:
                if type(sub_data) != rtype['type']:
                    msg = f"{name} should be type({rtype['type'].__name__})"
                    self._update_violation(name, TypeViolation(msg))
        return self.violations

    def _is_ruleset_type(self, data):
        return type(data) == dict

    def _update_violation(self, name: str, violation: Violation):
        sub = self.violations.get(name, [])
        sub.append(violation)
        self.violations[name] = sub
