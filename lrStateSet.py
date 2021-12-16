import copy


EPS = ''  # epsilon
END = '$'  # end of a string

terminals = []
n_terminals = []  # nonterminals

symbols = set()
production_rules = dict()  # str -> set of ProductionRule
first = dict()  # str -> set of str


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


########################################################################################################################
# compute first
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
    """
    compute first of every symbol and store them in a set called first
    """
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


def firstOfSymbols(symbol_seq: list) -> set:
    """
    compute first of symbol_seq based on the set first
    :param symbol_seq: a list of nonterminals and terminals, for example ABc
    :return: result of first(ABc)
    """
    assert len(symbol_seq) > 0
    res = set()
    if symbol_seq[0] == END:  # take $ into consideration
        res.add(END)
        return res

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


########################################################################################################################
# init symbols and production rules
def initProductionRules() -> None:
    for symbol in symbols:
        if symbol in terminals:
            continue
        production_rules[symbol] = set()


def showProductionRules() -> None:
    for k in production_rules:
        for production_rule in production_rules[k]:
            production_rule.show('\n')
        print()


def showSymbols() -> None:
    for symbol in symbols:
        print(symbol, end=' ')
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


########################################################################################################################
# compute project(or item) set
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
        self.production_rule_id = production_rule.id  # store the production rule id of which generates this project
        self.left = production_rule.left
        self.queue = []
        if production_rule.right == [EPS]:
            self.out_queue = []
        else:
            self.out_queue = production_rule.right
        self.reduce = False
        self.checkReduce()  # not a reduce project
        self.equivalence = set()  # first level identical LRProject.id
        self.goto = dict()  # X -> LRProject.id  goto LRProject.id when the input is X, where X here is nextSymbol()
        self.look_forward = END  # initialize look_forward as END, will be modified later

    def generateEquivalence(self) -> None:
        """
        generate first level identical project
        id:0 A -> · Ba  equivalence = {1, 3}
        id:1 B -> · Cb  equivalence = {4}
        id:3 B -> · ba  equivalence = {}
        id:4 C -> · c   equivalence = {}
        """
        if self.reduce:  # reduce projects do not have equivalent projects
            return
        next_symbol = self.out_queue[0]
        if next_symbol in terminals:
            return
        if next_symbol in n_terminals:
            for lr_project in lr_projects:
                # equivalent projects are those start with · so their queue is empty
                if lr_project.left == next_symbol and lr_project.queue == []:
                    self.equivalence.add(lr_project.id)

    def generateGoto(self) -> None:
        if self.reduce:  # reduce projects do not have goto projects
            return
        # A -> a · Bb
        queue = copy.deepcopy(self.queue)  # queue = [a]
        out_queue = copy.deepcopy(self.out_queue)  # out_queue = [B, b]
        next_symbol = out_queue.pop(0)  # B
        queue.append(next_symbol)  # queue = [a, B]  out_queue = [b] => A -> aB · b
        for lr_project in lr_projects:
            # find lr_project that meet requirements
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

    def nextSymbol(self) -> str:
        """
        the symbol after ·
        A -> B · abc
        next_symbol = a
        """
        assert not self.reduce
        return self.out_queue[0]

    def restSymbols(self) -> list:
        """
        symbols without next_symbol
        A -> B · abc
        rest_symbols = [b, c]
        """
        assert not self.reduce
        rest_symbols = copy.deepcopy(self.out_queue)
        rest_symbols.pop(0)
        return rest_symbols

    def nextProject(self):
        """
        this project: A -> B · abc
        next project: A -> Ba · bc
        :return: LRProject
        """
        assert not self.reduce  # reduce projects do not have next projects

        lr_project = copy.deepcopy(self)
        symbol = lr_project.out_queue.pop(0)
        lr_project.queue.append(symbol)
        lr_project.checkReduce()

        return lr_project

    def checkReduce(self) -> None:
        """
        whether this is a reduce project
        """
        if len(self.out_queue) == 0:
            self.reduce = True

    def __hash__(self):
        # TODO hash conflict ?
        return hash(self.id) + hash(self.look_forward)

    def __eq__(self, other):
        return self.id == other.id and self.look_forward == other.look_forward

    def show(self, end: str) -> None:
        print(self.id, end=' ')
        print(self.left, end=' -> ')
        for r in self.queue:
            print(r, end=' ')
        print('·', end=' ')
        for r in self.out_queue:
            print(r, end=' ')
        print("  look_forward: %s" % self.look_forward, end=' ')
        print("  link_info:", end=' ')
        print(self.equivalence, end=' ')
        print(self.goto, end=' ')
        print(end, end='')


lr_projects = set()


def getProductionRuleById(id) -> ProductionRule:
    for k in production_rules:
        for production_rule in production_rules[k]:
            if production_rule.id == id:
                return production_rule
    print("production rule with id = %d not found" % id)
    raise Exception


def showLRProjects() -> None:
    for lr_project in lr_projects:
        production_rule = getProductionRuleById(lr_project.production_rule_id)
        production_rule.show('    ')
        lr_project.show('\n')


def initLRProjects() -> None:
    """
    for every production rule A -> BC
    put A -> · BC, A -> B · C, A -> BC · in lr_projects
    after initialization, set lr_projects will not change
    use function getLRProjectById(id: int) -> LRProject to get a LRProject from it
    """
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


def generateLRProjects() -> None:
    initLRProjects()
    for lr_project in lr_projects:
        lr_project.generateEquivalence()
        lr_project.generateGoto()


class State:
    def __init__(self, id: int):
        self.id = id
        self.lr_projects = set()
        self.goto = dict()  # X -> state.id  goto state.id when the input is X, where X here is nextSymbol()

    def addLRProject(self, lr_project: LRProject) -> None:
        self.lr_projects.add(lr_project)

    def __hash__(self):
        return self.id

    def __eq__(self, other):
        return self.id == other.id

    def show(self, end) -> None:
        print('I%d' % self.id)
        for lr_project in self.lr_projects:
            lr_project.show('\n')
        print(self.goto, end='')
        print(end)


def identicalState(state_a: State, state_b: State) -> bool:
    """
    if every lr_project in state_a is in state_b
    then they are regarded as the same
    """
    for lr_project in state_b.lr_projects:
        if lr_project not in state_a.lr_projects:
            return False
    return True


def getLRProjectById(id: int) -> LRProject:
    for lr_project in lr_projects:
        if lr_project.id == id:
            return lr_project
    print("LR project with id = %d not found" % id)
    raise Exception


def getLRProjectByProductionRuleId(id: int) -> LRProject:
    for lr_project in lr_projects:
        if lr_project.production_rule_id == id:
            return lr_project
    print("LR project with production_rule_id = %d not found" % id)
    raise Exception


def closure(state: State) -> State:
    if len(state.lr_projects) == 0:
        return state
    while True:
        project_tmp = set()
        unchanged = True
        # add equivalent projects
        # A -> · aB, b
        # for every terminal t in first(Bb)
        # add A -> a · B, t to the state
        for lr_project in state.lr_projects:
            for id in lr_project.equivalence:
                equivalent_lr_project = copy.deepcopy(getLRProjectById(id))
                symbol_seq = copy.deepcopy(lr_project.restSymbols())  # [B]
                symbol_seq.append(lr_project.look_forward)  # [B, b]
                first_set = firstOfSymbols(symbol_seq)

                for new_look_forward in first_set:
                    equivalent_lr_project.look_forward = new_look_forward
                    project_tmp.add(copy.deepcopy(equivalent_lr_project))

        for project in project_tmp:
            if project not in state.lr_projects:
                unchanged = False
                state.addLRProject(project)

        if unchanged:
            break

    return state


def goto(state: State, symbol: str) -> set:
    res = set()
    for lr_project in state.lr_projects:
        if lr_project.reduce:  # reduce project do not have goto
            continue
        # A -> a · Bb  next_symbol = B
        # so if symbol == B, state will goto a new state,and res is in its attribute lr_project
        assert len(lr_project.goto) == 1
        for next_symbol in lr_project.goto:
            if next_symbol == symbol:
                next_project = copy.deepcopy(getLRProjectById(lr_project.goto[next_symbol]))
                res.add(next_project)
    return res


state_set = set()  # set of State


def items():
    global state_set
    id = 0
    state = State(id)
    id += 1
    # S' -> S, $
    start_item = getLRProjectByProductionRuleId(0)
    start_item.look_forward = END
    state.addLRProject(start_item)
    state = closure(state)
    state_set.add(state)

    while True:
        unchanged = True
        new_states = set()
        for state in state_set:
            for symbol in symbols:
                new_lr_projects = goto(state, symbol)
                if len(new_lr_projects) != 0:
                    new_state = State(id)
                    id += 1
                    new_state.lr_projects = copy.deepcopy(new_lr_projects)
                    new_state = closure(new_state)

                    # whether state_set contains new_state
                    contain = False
                    for s in state_set:
                        if identicalState(new_state, s):
                            contain = True
                            id -= 1
                            break
                    if not contain:
                        new_states.add(new_state)
                        state.goto[symbol] = new_state.id
                        unchanged = False

        if unchanged:
            break

        state_set = state_set | new_states


def showStates() -> None:
    for state in state_set:
        state.show('\n')


def generateLRStateSet():
    # expand your CFG and update n_terminals.txt and production_rules.txt first
    # and make sure that the first rule is the start rule
    readSymbols('terminals.txt', 'n_terminals.txt')
    # showSymbols()
    readProductionRules('production_rules.txt')
    # showProductionRules()
    generateFirst()
    # showFirst()
    generateLRProjects()
    # showLRProjects()
    items()
    print(len(state_set))
    showStates()


if __name__ == '__main__':
    generateLRStateSet()
