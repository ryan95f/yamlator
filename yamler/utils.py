import yaml


def load_yaml_file(filename: str) -> dict:
    if filename is None:
        raise ValueError("filename cannot be None")

    if len(filename) == 0:
        raise ValueError("filename cannot be an empty string")

    with open(filename, 'r') as f:
        return yaml.load(f, Loader=yaml.Loader)


def load_yamler_ruleset(filename: str) -> str:
    with open(filename) as f:
        return f.read()
