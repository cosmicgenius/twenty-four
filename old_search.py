from logic import Num, op_table
from itertools import permutations

fail = -1000

# Tries to find a working combination of inputs
# producing the output
#
# Currently is a full search that just returns one
# with maximal purity
def old_search(inputs: tuple[tuple[Num, str], ...], target: Num) -> tuple[str, int]:
    #s_inputs = tuple(sorted(t[0] for t in inputs))
    #print(inputs)
    N = len(inputs)
    if N < 1:
        return ("???", fail)

    if N == 1 and inputs[0][0] == target:
        #print(inputs[0][1])
        return (inputs[0][1], 0)

    best, best_pur = inputs[0][1], fail
    for op in op_table:
        if op.arity == 1: # unary
            for i in range(N):
                #print(inputs[i][0], inputs[i][1])
                if not op.domain(inputs[i][0]): continue
                if op.purity <= best_pur: continue # cannot be a better solution

                new_num: Num = op.op(inputs[i][0])
                new_hist: str = op.pretty(inputs[i][1])
                res, pur = old_search(inputs[:i] + inputs[i+1:] +
                                  ((new_num, new_hist),), target)
                pur += op.purity

                if pur > best_pur:
                    best = res
                    best_pur = pur

        elif op.arity == 2: # binary
            for i, j in permutations(range(N), 2):
                x, y = i, j
                if i > j: x, y = j, i

                if not op.domain(inputs[i][0], inputs[j][0]): continue
                if op.comm and i > j: continue # redundant
                if op.purity <= best_pur: continue # cannot be a better solution

                new_num: Num = op.op(inputs[i][0], inputs[j][0])
                new_hist: str = op.pretty(inputs[i][1], inputs[j][1])

                res, pur = old_search(inputs[:x] + inputs[x+1:y] + inputs[y+1:] + 
                                  ((new_num, new_hist),), target)
                pur += op.purity

                if pur > best_pur:
                    best = res
                    best_pur = pur

    return (best, best_pur)
