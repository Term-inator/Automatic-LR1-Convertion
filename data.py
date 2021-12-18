
EPS = ''  # epsilon
END = '$'  # end of a string

terminals = []
n_terminals = []  # nonterminals

symbols = set()
production_rules = dict()  # str -> set of ProductionRule


class ProductionRule:
    def __init__(self, id: int, left: str, right: list):  # id, str, list of str
        """
        :param id: sequence number
        :param left: str on the left side of ->
        :param right: str on the right side of ->
        A -> abB
        left: A
        right: abB
        """
        self.id = id
        self.left = left
        self.right = right

    def show(self, end: str) -> None:
        print(self.id, end=' ')
        print(self.left, end=' -> ')
        for r in self.right:
            if r == EPS:
                print('EPS', end=' ')
                continue
            print(r, end=' ')
        print(end, end='')


# init symbols and production rules
def initProductionRules() -> None:
    for symbol in symbols:
        if symbol in terminals:
            continue
        production_rules[symbol] = set()


def readSymbols(terminal_file: str, n_terminal_file: str) -> None:
    global terminals, n_terminals
    with open(terminal_file) as f:
        for line in f.readlines():
            terminals = line.strip().split(' ')

    with open(n_terminal_file) as f:
        for line in f.readlines():
            n_terminals = line.strip().split(' ')

    for terminal in terminals:
        symbols.add(terminal)

    terminals.append(EPS)
    symbols.add(EPS)

    for n_terminal in n_terminals:
        symbols.add(n_terminal)


def readProductionRules(production_rule_file: str) -> None:
    initProductionRules()

    id = 0
    with open(production_rule_file) as f:
        for line in f.readlines():
            left, rights = line.strip().split('->')
            left = left.strip()
            rights = rights.strip().split('|')
            for right in rights:
                right = right.strip().split(' ')
                if left in symbols:
                    left_symbol = left
                right_symbol = []
                for r in right:
                    if r == 'EPS':
                        r = ''
                    if r in symbols:
                        r_symbol = r
                    right_symbol.append(r_symbol)
                production_rule = ProductionRule(id, left_symbol, right_symbol)
                production_rules[left_symbol].add(production_rule)
                id += 1


def showProductionRules() -> None:
    for k in production_rules:
        for production_rule in production_rules[k]:
            production_rule.show('\n')


def showSymbols() -> None:
    for symbol in symbols:
        print(symbol, end=' ')
    print()


def haveDirectEmptyProductionRule(x: str) -> bool:
    """
    whether x has a production rule x -> epsilon
    """
    assert x in n_terminals
    x_production_rule_set = production_rules[x]
    for x_production_rule in x_production_rule_set:
        if x_production_rule.right == [EPS]:
            return True
    return False


def readData() -> None:
    readSymbols('./data/terminals.txt', './data/n_terminals.txt')
    # showSymbols()
    readProductionRules('./data/production_rules.txt')
    # showProductionRules()


if __name__ == '__main__':
    readData()
    showProductionRules()

