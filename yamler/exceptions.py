class InvalidRulesetFilenameError(RuntimeError):
    def __init__(self, filename: str) -> None:
        message = f'{filename} is not a valid ruleset filename'
        super().__init__(message)
