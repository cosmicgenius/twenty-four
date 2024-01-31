from logic import Num, unary_op, binary_op
from itertools import permutations

fail = -1000

checked = set()

# Tries to find a working combination of inputs
# producing the output
#
# Currently is a full search that just returns one
# with maximal purity
def search(inputs: tuple[tuple[Num, str], ...], target: Num) -> tuple[str, int]:
    s_inputs = tuple(sorted(t[0] for t in inputs))
    if s_inputs in checked:
        return ('', fail) # no use checking this
    checked.add(s_inputs)

    best, best_pur = '', fail
    N = len(inputs)
    """
    # This won't terminate
    for i in range(N):
        for op in unary_op:
            new_num: Num = op.op(inputs[i][0])
            new_hist: str = op.pretty(inputs[i][1])
            res, pur = search(inputs[:i] + inputs[i+1:] +
                              ((new_num, new_hist),), output)
            if pur > best_pur:
                best = res
                best_pur = pur
    """
    if N < 1:
        return ("???", fail)

    if N == 1:
        if inputs[0][0] == target:
            return (inputs[0][1], 0)
        #print(inputs[0])
        return (inputs[0][1], fail)
    
    # binary op
    for i, j in permutations(range(N), 2):
        x, y = i, j
        if i > j: x, y = j, i
        for op in binary_op:
            if not op.domain(inputs[i][0], inputs[j][0]): continue
            if op.comm and i > j: continue # redundant
            if op.purity <= best_pur: continue # cannot be a better solution

            new_num: Num = op.op(inputs[i][0], inputs[j][0])
            new_hist: str = op.pretty(inputs[i][1], inputs[j][1])

            res, pur = search(inputs[:x] + inputs[x+1:y] + inputs[y+1:] + 
                              ((new_num, new_hist),), target)
            pur = min(pur, op.purity)

            if pur > best_pur:
                best = res
                best_pur = pur
    return (best, best_pur)
