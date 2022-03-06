class InvalidRulesetFilenameError(RuntimeError):
    """Exception for when the schema filename does not match the expected pattern"""

    def __init__(self, filename: str) -> None:
        """Represents an error in the filename that does not match the expected pattern

        Args:
            filename (str): The filename that was invalid
        """
        message = f'{filename} is not a valid ruleset filename'
        super().__init__(message)
