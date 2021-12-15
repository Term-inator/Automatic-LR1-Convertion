import copy

import xlrd.timemachine

EPS = ''  # epsilon
END = '$'  # end of a string


terminals = []
n_terminals = []  # nonterminals


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

    def show(self, end: str):
        print(self.id, end=' ')
        print(self.left, end=' -> ')
        for r in self.right:
            if r == EPS:
                print('EPS', end=' ')
                continue
            print(r, end=' ')
        print(end, end='')


symbols = set()
production_rules = dict()  # str -> set of ProductionRule
first = dict()  # str -> set of str


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


def initFirst() -> None:
    for symbol in symbols:
        first[symbol] = set()


def showFirst() -> None:
    for k in first:
        if k == EPS:
            print('EPS', end=' ')
        print(k, end=' [ ')
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
            if symbol in terminals:
                if symbol not in first[symbol]:
                    unchanged = False
                first[symbol].add(symbol)
                continue
            if haveDirectEmptyProductionRule(symbol):
                if EPS not in first[symbol]:
                    unchanged = False
                first[symbol].add(EPS)
            if symbol in n_terminals:  # X -> Y1 Y2 ... Yk
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
    res = set()
    all_EPS = True
    for symbol in symbol_seq:
        if symbol == END:
            continue
        first_symbol = copy.deepcopy(first[symbol])
        try:
            first_symbol.remove(EPS)
        except KeyError:
            pass
        res = res | first_symbol
        if EPS not in first[symbol]:
            all_EPS = False
            break

    if all_EPS:
        res.add(EPS)

    return res


def initProductionRules() -> None:
    for symbol in symbols:
        if symbol in terminals:
            continue
        production_rules[symbol] = set()


def showProductionRules() -> None:
    for k in production_rules:
        for i, production_rule in enumerate(production_rules[k]):
            production_rule.show('\n')
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


class LRProject:
    def __init__(self, id: int, production_rule: ProductionRule):
        """
        transfer a production rule to a LRProject
        A -> ·abB
        left: A
        queue: []
        out_queue: abB
        """
        self.id = id
        self.production_rule_id = production_rule.id
        self.left = production_rule.left
        self.queue = []
        if production_rule.right == [EPS]:
            self.out_queue = []
        else:
            self.out_queue = production_rule.right
        self.reduce = False
        self.checkReduce()  # not a reduce project

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

    def checkReduce(self):
        if len(self.out_queue) == 0:
            self.reduce = True

    def nextProject(self):
        assert not self.reduce

        lr_project = copy.deepcopy(self)
        symbol = lr_project.out_queue.pop(0)
        lr_project.queue.append(symbol)
        lr_project.checkReduce()

        return lr_project

    def __hash__(self):
        return self.id

    def __eq__(self, other):
        return self.id == other.id

    def show(self, end: str):
        print(self.id, end=' ')
        print(self.left, end=' -> ')
        for r in self.queue:
            print(r, end=' ')
        print('·', end=' ')
        for r in self.out_queue:
            print(r, end=' ')
        print(end, end='')


lr_projects = set()


def getProductionRuleById(id):
    for k in production_rules:
        for production_rule in production_rules[k]:
            if production_rule.id == id:
                return production_rule


def showLRProjects():
    for lr_project in lr_projects:
        production_rule = getProductionRuleById(lr_project.production_rule_id)
        production_rule.show('    ')
        lr_project.show('\n')


def initLRProjects():
    id = 0
    for k in production_rules:
        for production_rule in production_rules[k]:
            project = LRProject(id, production_rule)
            while True:
                lr_projects.add(project)
                id += 1
                if project.reduce:
                    break
                project = project.nextProject()
                project.id = id


class State:
    def __init__(self, id: int):
        self.id = id
        self.lr_projects = set()
        self.unchanged = True

    def addItem(self, lr_project: LRProject) -> bool:
        if lr_project in self.lr_projects:
            self.unchanged = False
        self.lr_projects.add(lr_project)
        return self.unchanged

    def __hash__(self):
        return self.id

    def __eq__(self, other):
        return self.id == other.id


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

    return state


def goto(state: State, symbol: str):
    assert symbol in n_terminals
    res = set()
    for item in state.items:
        if item.reduce:
            break
        if item.nextSymbol() == symbol:
            next_project = item.nextProject()
            res.add(next_project)
    return res


item_set = set()  # set of State


def items():
    initLRProjects()

    id = 0
    state = State(id)
    start_item = lr_projects[0]
    start_item.look_forward = END
    state.addItem(start_item)
    item_set.add(state)

    unchanged = True
    while True:
        for item in item_set:
            for symbol in symbols:
                new_item = goto(item, symbol)
                if len(new_item) != 0:
                    if new_item not in item_set:
                        item_set.add(new_item)
                        unchanged = False

            if unchanged:
                break


def main():
    # expand your CFG and update n_terminals.txt and production_rules.txt first
    # and make sure that the first rule is the start rule
    readSymbols('terminals.txt', 'n_terminals.txt')
    readProductionRules('production_rules.txt')
    # showProductionRules()
    generateFirst()
    # showFirst()
    # items()
    initLRProjects()
    showLRProjects()


main()
