

class Symbol:
    def __init__(self, name: str, is_terminal: bool):
        self.name = name
        self.is_terminal = is_terminal


class ProductionRule:
    def __init__(self, id: int, left: Symbol, right: list): # id, Symbol, list of Symbols
        self.id = id
        self.left = left
        self.right = right




production_rules = []
