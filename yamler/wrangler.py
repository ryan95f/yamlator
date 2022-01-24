from enum import Enum


class ViolationType(Enum):
    REQUIRED = "required"
    TYPE = "type"


class Violation:
    def __init__(self, message: str, v_type: ViolationType):
        self._message = message
        self._v_type = v_type

    @property
    def message(self):
        return self._message

    @property
    def violation_type(self):
        return self._v_type.value


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

            sub_data = data.get(name, None)
            if self._is_missing_required_data(sub_data, rule):
                msg = f"{name} is missing"
                self._update_violation(name, RequiredViolation(msg))
                continue

            if self._is_ruleset_rule(rule):
                self._wrangle_rulesets(name, sub_data, rule)
                continue

            if self._has_incorrect_type(sub_data, rule):
                msg = f"{name} should be type({rtype['type'].__name__})"
                self._update_violation(name, TypeViolation(msg))

        return self.violations

    def _is_missing_required_data(self, data, rule):
        required = rule['required']
        return required and data is None

    def _is_ruleset_type(self, data):
        return type(data) == dict

    def _update_violation(self, name: str, violation: Violation):
        sub = self.violations.get(name, [])
        sub.append(violation)
        self.violations[name] = sub

    def _is_ruleset_rule(self, rule):
        rtype = rule['rtype']
        return rtype['type'] == 'ruleset'

    def _wrangle_rulesets(self, name, data, rule):
        rtype = rule.get('rtype')
        if self._is_ruleset_type(data):
            ruleset_name = rtype['lookup']
            ruleset = self._instructions['rules'].get(ruleset_name)
            self._wrangle(data, ruleset['rules'], name)
            return

        # Ignore optional rulesets
        required = rule.get('required', True)
        if not required and data is None:
            return

        msg = f"{name} should be type(ruleset)"
        self._update_violation(name, TypeViolation(msg))

    def _has_incorrect_type(self, data, rule: dict):
        rtype = rule['rtype']
        return (type(data) != rtype['type']) and (data is not None)
