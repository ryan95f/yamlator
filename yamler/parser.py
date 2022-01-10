from lark import Lark

_GRAMMER_FILE = "grammer.lark"

class YamlerParser:
    
    def __init__(self):
        self._parser = Lark.open(_GRAMMER_FILE)

    def parse(self, text):
        return self._parser.parse(text)
