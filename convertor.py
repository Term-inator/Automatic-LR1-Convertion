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
        self.equivalence = set()  # one level identical LRProject.id
        self.goto = dict()  # X -> LRProject.id  goto LRProject.id when the input is X, where X here is nextSymbol()
        self.look_forward = END

    def generateEquivalence(self):
        if self.reduce:
            return
        next_symbol = self.out_queue[0]
        if next_symbol in terminals:
            return
        if next_symbol in n_terminals:
            for lr_project in lr_projects:
                if lr_project.left == next_symbol and lr_project.queue == []:
                    self.equivalence.add(lr_project.id)

    def generateGoto(self):
        if self.reduce:
            return
        queue = copy.deepcopy(self.queue)
        out_queue = copy.deepcopy(self.out_queue)
        next_symbol = out_queue.pop(0)
        queue.append(next_symbol)
        for lr_project in lr_projects:
            if lr_project.left != self.left:
                continue
            if len(lr_project.queue) != len(queue):
                continue
            else:
                equal = True
                for i in range(len(queue)):
                    if lr_project.queue[i] != queue[i]:
                        equal = False
                        break

                if not equal:
                    continue
            if len(lr_project.out_queue) != len(out_queue):
                continue
            else:
                equal = True
                for i in range(len(out_queue)):
                    if lr_project.out_queue[i] != out_queue[i]:
                        equal = False
                        break
                if not equal:
                    continue

            self.goto[next_symbol] = lr_project.id
            break

    def nextSymbol(self):
        assert not self.reduce
        return self.out_queue[0]

    def restSymbols(self):
        assert not self.reduce
        rest_symbols = copy.deepcopy(self.out_queue)
        rest_symbols.pop(0)
        return rest_symbols

    def nextProject(self):
        assert not self.reduce

        lr_project = copy.deepcopy(self)
        symbol = lr_project.out_queue.pop(0)
        lr_project.queue.append(symbol)
        lr_project.checkReduce()

        return lr_project

    def checkReduce(self):
        if len(self.out_queue) == 0:
            self.reduce = True

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
        print(self.equivalence, end=' ')
        print(self.goto, end=' ')
        print(end, end='')


lr_projects = set()


def getProductionRuleById(id):
    for k in production_rules:
        for production_rule in production_rules[k]:
            if production_rule.id == id:
                return production_rule
    print("production rule with id = %d not found" % id)
    raise Exception


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


def generateLRProjects():
    for lr_project in lr_projects:
        lr_project.generateEquivalence()
        lr_project.generateGoto()


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

    def show(self, end):
        print(self.id, end=' ')
        for lr_project in self.lr_projects:
            lr_project.show('\n')
        print(end)


def identicalState(state_a: State, state_b: State):
    for lr_project in state_b.lr_projects:
        if lr_project not in state_a.lr_projects:
            return False
    return True


def getLRProjectById(id: int):
    for lr_project in lr_projects:
        if lr_project.id == id:
            return lr_project
    print("LR project with id = %d not found" % id)
    raise Exception


def getLRProjectByProductionRuleId(id: int):
    for lr_project in lr_projects:
        if lr_project.production_rule_id == id:
            return lr_project
    print("LR project with production_rule_id = %d not found" % id)
    raise Exception


def closure(state: State) -> None:
    while True:
        item_tmp = set()
        unchanged = True
        for lr_project in state.lr_projects:
            for id in lr_project.equivalence:
                equivalent_lr_project = getLRProjectById(id)
                symbol_seq = copy.deepcopy(lr_project.restSymbols())
                symbol_seq.append(lr_project.look_forward)
                equivalent_lr_project.look_forward = firstOfSymbols(symbol_seq)
                item_tmp.add(equivalent_lr_project)

        for item in item_tmp:
            unchanged = state.addItem(item)

        if unchanged:
            break

    return state


def goto(state: State, symbol: str):
    res = set()
    for lr_project in state.lr_projects:
        if lr_project.reduce:
            continue
        for next_symbol in lr_project.goto:
            if next_symbol == symbol:
                # print(next_symbol)
                next_project = getLRProjectById(lr_project.goto[next_symbol])
                res.add(next_project)
    return res


state_set = set()  # set of State


def items():
    global state_set
    id = 0
    state = State(id)
    id += 1
    start_item = getLRProjectByProductionRuleId(0)
    start_item.look_forward = END
    state.addItem(start_item)
    state = closure(state)
    state_set.add(state)

    while True:
        unchanged = True
        new_states = set()
        for state in state_set:
            state.show('\n')
            for symbol in symbols:
                # print(symbol, end=' ')
                # state.show('\n')
                new_lr_projects = goto(state, symbol)
                if len(new_lr_projects) != 0:
                    new_state = State(id)
                    id += 1
                    new_state.lr_projects = copy.deepcopy(new_lr_projects)
                    new_state = closure(new_state)
                    # print(symbol)
                    # new_state.show('\n')
                    contain = False
                    for s in state_set:
                        if identicalState(new_state, s):
                            contain = True
                            break
                    if not contain:
                        new_states.add(new_state)
                        unchanged = False

        if unchanged:
            break

        state_set = state_set | new_states


def showSymbols():
    for symbol in symbols:
        print(symbol, end=' ')
    print()


def main():
    # expand your CFG and update n_terminals.txt and production_rules.txt first
    # and make sure that the first rule is the start rule
    readSymbols('terminals.txt', 'n_terminals.txt')
    # showSymbols()
    readProductionRules('production_rules.txt')
    # showProductionRules()
    generateFirst()
    # showFirst()
    initLRProjects()
    generateLRProjects()
    # showLRProjects()
    items()
    print(len(state_set))


main()
