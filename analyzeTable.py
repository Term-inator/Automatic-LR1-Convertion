import data
import lrStateSet

action_table = []  # list of maps
goto_table = []  # list of maps


def initializeActionTable() -> None:
    for i in range(lrStateSet.length):
        d = dict()
        for terminal in data.terminals:
            d[terminal] = 0
        d[data.END] = 0
        action_table.append(d)


def initializeGotoTable() -> None:
    for i in range(lrStateSet.length):
        d = dict()
        for n_terminal in data.n_terminals:
            d[n_terminal] = 0
        goto_table.append(d)


def initializeTable() -> None:
    initializeActionTable()
    initializeGotoTable()


def generateAnalyzeTable() -> None:
    initializeTable()
    for state in lrStateSet.state_set:
        for lr_project in state.lr_projects:
            if lr_project.reduce:
                action_table[state.id][lr_project.look_forward] = ('r', lr_project.production_rule_id)
        for symbol in state.goto:
            if symbol in data.terminals:
                action_table[state.id][symbol] = ('s', state.goto[symbol])
                continue
            if symbol in data.n_terminals:
                goto_table[state.id][symbol] = state.goto[symbol]
                continue


def showAnalyzeTable() -> None:
    print('  ', end='')
    for terminal in data.terminals:
        print(terminal, end=' ')
    for n_terminal in data.n_terminals:
        print(n_terminal, end=' ')
    print()
    for i in range(lrStateSet.length):
        print(i, end=' ')
        for terminal in data.terminals:
            print(action_table[i][terminal], end=' ')
        print(action_table[i][data.END], end=' ')
        for n_terminal in data.n_terminals:
            print(goto_table[i][n_terminal], end=' ')
        print()


if __name__ == '__main__':
    data.readData()
    lrStateSet.generateLRStateSet()
    lrStateSet.showStates()
    # generateAnalyzeTable()
    # showAnalyzeTable()
