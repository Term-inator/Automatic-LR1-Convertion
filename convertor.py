EPS = ''  # 空
END = '$'  # 串末


class Symbol:
    def __init__(self, val: str, is_terminal: bool):
        self.val = val
        self.is_terminal = is_terminal


class ProductionRule:
    def __init__(self, id: int, left: Symbol, right: list):  # id, Symbol, list of Symbols
        self.id = id  # A -> abB
        self.left = left  # A
        self.right = right  # [a, b, B]


symbols = set()
production_rules = dict()  # Symbol -> set of ProductionRule
first = dict()  # Symbol -> set of Symbols


def getSymbol(val: str) -> Symbol:
    for symbol in symbols:
        if symbol.val == val:
            return symbol
    print(val + ' not found')
    raise Exception


def haveDirectEmptyProductionRule(x: Symbol) -> bool:
    assert not x.is_terminal
    x_production_rule_set = production_rules[x]
    for x_production_rule in x_production_rule_set:
        if x_production_rule.right == [EPS]:
            return True
    return False


def initFirst() -> None:
    for symbol in symbols:
        first[symbol] = set()


def first() -> None:
    initFirst()
    while True:
        unchanged = True
        for symbol in symbols:
            if symbol.is_terminal:
                if symbol.val not in first[symbol]:
                    unchanged = False
                first[symbol].add(symbol.val)
            elif haveDirectEmptyProductionRule(symbol.val):
                if EPS not in first[symbol]:
                    unchanged = False
                first[symbol].add(EPS)
            elif not symbol.is_terminal:
                all_EPS = True
                for production_rule in production_rules[symbol]:
                    for i in range(len(production_rule.right)):
                        if len(first[symbol] & first[production_rule.right[i]]) != len(first[symbol]):
                            unchanged = False
                        first[symbol] = first[symbol] | first[production_rule.right[i]]
                        if EPS not in first[production_rule.right[i]]:
                            all_EPS = False
                            break
                if all_EPS:
                    if EPS not in first[symbol]:
                        unchanged = False
                    first(symbol).add(EPS)

        if unchanged:
            break


terminals = []
n_terminals = []


def initProductionRules() -> None:
    for symbol in symbols:
        if symbol.is_terminal:
            continue
        production_rules[symbol] = set()


def showProductionRules():
    for k in production_rules:
        print(k.val, end=' -> ')
        for i, production_rule in enumerate(production_rules[k]):
            for right in production_rule.right:
                if right.val == EPS:
                    print('EPS', end=' ')
                    continue
                print(right.val, end=' ')
            if i < len(production_rules[k]) - 1:
                print(' | ', end='')
        print('\n')


def readSymbols():
    global terminals, n_terminals
    with open('terminals.txt') as f:
        for line in f.readlines():
            terminals = line.strip().split(' ')

    with open('n_terminals.txt') as f:
        for line in f.readlines():
            n_terminals = line.strip().split(' ')

    for terminal in terminals:
        symbols.add(Symbol(terminal, True))
    symbols.add(Symbol(EPS, True))

    for n_terminal in n_terminals:
        symbols.add(Symbol(n_terminal, False))


def readProductionRules():
    initProductionRules()

    with open('production_rules.txt') as f:
        for i, line in enumerate(f.readlines()):
            left, rights = line.strip().split('->')
            left = left.strip()
            rights = rights.strip().split('|')
            for right in rights:
                right = right.strip().split(' ')
                left_symbol = getSymbol(left)
                right_symbol = []
                for r in right:
                    if r == 'EPS':
                        r = ''
                    r_symbol = getSymbol(r)
                    right_symbol.append(r_symbol)
                production_rule = ProductionRule(i, left_symbol, right_symbol)
                production_rules[left_symbol].add(production_rule)


def main():
    readSymbols()
    readProductionRules()
    showProductionRules()


main()

