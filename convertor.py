import copy


EPS = ''  # epsilon
END = '$'  # end of a string


class Symbol:
    def __init__(self, val: str, is_terminal: bool):
        """
        :param val: value(terminal) or name(not terminal)
        :param is_terminal: True if is a terminal
        """
        self.val = val
        self.is_terminal = is_terminal


class ProductionRule:
    def __init__(self, id: int, left: Symbol, right: list):  # id, Symbol, list of Symbols
        """
        :param id: sequence number
        :param left: Symbol on the left side of ->
        :param right: Symbols on the right side of ->
        A -> abB
        left: A
        right: abB
        """
        self.id = id
        self.left = left
        self.right = right


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
    """
    whether x has a production rule x -> epsilon
    """
    assert not x.is_terminal
    x_production_rule_set = production_rules[x]
    for x_production_rule in x_production_rule_set:
        if x_production_rule.right == [EPS]:
            return True
    return False


def initFirst() -> None:
    for symbol in symbols:
        first[symbol] = set()


def showFirst() -> None:
    for k in first:
        if k.val == EPS:
            print('EPS', end=' ')
        print(k.val, end=' [ ')
        for f in first[k]:
            if f == EPS:
                print('EPS', end=' ')
                continue
            print(f, end=' ')
        print(']')


def generateFirst() -> None:
    initFirst()
    while True:
        unchanged = True  # repeat until no more elements are added to any first set
        for symbol in symbols:
            if symbol.is_terminal:
                if symbol.val not in first[symbol]:
                    unchanged = False
                first[symbol].add(symbol.val)
            elif haveDirectEmptyProductionRule(symbol):
                if EPS not in first[symbol]:
                    unchanged = False
                first[symbol].add(EPS)
            elif not symbol.is_terminal:  # X -> Y1 Y2 ... Yk
                for production_rule in production_rules[symbol]:
                    all_EPS = True  # if forall i from 1 to k, first(Yi) contains epsilon, then add epsilon to first(X)
                    for right in production_rule.right:  # Yi
                        first_right = copy.deepcopy(first[right])  # deepcopy first(Yi) as first_Yi
                        try:
                            first_right.remove(EPS)  # remove epsilon from first_Yi
                        except KeyError:
                            pass
                        if len(first[symbol] | first_right) != len(first[symbol]):  # | means Union
                            unchanged = False
                        first[symbol] = first[symbol] | first_right
                        if EPS not in first[right]:  # whether first(Yi) contains epsilon
                            all_EPS = False
                            break

                    if all_EPS:
                        if EPS not in first[symbol]:
                            unchanged = False
                        first[symbol].add(EPS)

        if unchanged:
            break


def firstOfSymbols(symbol_seq):
    assert len(symbol_seq) > 0
    for symbol in symbol_seq:
        if symbol.is_terminal:
            return symbol.val



terminals = []
n_terminals = []  # nonterminals


def initProductionRules() -> None:
    for symbol in symbols:
        if symbol.is_terminal:
            continue
        production_rules[symbol] = set()


def showProductionRules() -> None:
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
        print()


def readSymbols(terminal_file: str, n_terminal_file: str) -> None:
    global terminals, n_terminals
    with open(terminal_file) as f:
        for line in f.readlines():
            terminals = line.strip().split(' ')

    with open(n_terminal_file) as f:
        for line in f.readlines():
            n_terminals = line.strip().split(' ')

    for terminal in terminals:
        symbols.add(Symbol(terminal, True))
    symbols.add(Symbol(EPS, True))

    for n_terminal in n_terminals:
        symbols.add(Symbol(n_terminal, False))


def readProductionRules(production_rule_file: str) -> None:
    initProductionRules()

    with open(production_rule_file) as f:
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


class LRProject:
    def __init__(self):
        pass

    def initWithParams(self, left: Symbol, queue: list, out_queue: list, look_forward: Symbol):
        self.left = left
        self.queue = queue  # list of Symbol
        self.out_queue = out_queue  # list of Symbol
        self.look_forward = look_forward
        if len(self.out_queue) == 0:
            self.reduce = True  # a reduce project
        else:
            self.reduce = False

    def initWithProductionRule(self, production_rule: ProductionRule, look_forward: Symbol):
        """
        transfer a production rule to a LRProject
        A -> ·abB
        left: A
        queue: []
        out_queue: abB
        """
        self.left = production_rule.left
        self.queue = []
        self.out_queue = production_rule.right
        self.look_forward = look_forward
        self.reduce = False  # not a reduce project

    def nextSymbol(self):
        try:
            return self.out_queue[0]
        except IndexError:
            self.reduce = True
            return None

    def restSymbols(self):
        try:
            return self.out_queue[1:]
        except IndexError:
            return [EPS]


class State:
    def __init__(self, id: int):
        self.id = id
        self.items = set()
        self.unchanged = True

    def addItem(self, lr_project: LRProject) -> bool:
        if lr_project in self.items:
            self.unchanged = False
        self.items.add(lr_project)
        return self.unchanged


def closure(state: State) -> None:
    unchanged = True
    while True:
        for lr_project in state.items:
            next_symbol = lr_project.nextSymbol()
            if next_symbol is None:
                continue
            for production_rule in production_rules[next_symbol]:
                new_lr_project = LRProject()
                symbol_seq = copy.deepcopy(lr_project.restSymbols())
                symbol_seq.append(lr_project.look_forward)
                new_lr_project.initWithProductionRule(production_rule, firstOfSymbols(symbol_seq))
                unchanged = state.addItem(new_lr_project)

        if unchanged:
            break


def main():
    # expand your CFG and update n_terminals.txt and production_rules.txt first
    readSymbols('terminals.txt', 'n_terminals.txt')
    readProductionRules('production_rules.txt')
    # showProductionRules()
    generateFirst()
    showFirst()


main()
