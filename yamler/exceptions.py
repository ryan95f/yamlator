class InvalidRulesetFilenameError(RuntimeError):
    """When the schema filename does not match the expected pattern"""

    def __init__(self, filename: str) -> None:
        """InvalidRulesetFilenameError init

        Args:
            filename (str): The filename that was invalid
        """
        message = f'{filename} is not a valid ruleset filename'
        super().__init__(message)
