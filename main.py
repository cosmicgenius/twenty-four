from logic import Num, NumHist
import random
import numpy as np
import mcts
import math

rep = 100_000

def run_mcts(inputs: tuple[NumHist, ...], target: Num):
    root: mcts.Node = mcts.Node(inputs, None, None)

    best_num_hist: NumHist = (Num(0), '')
    best_weight: float = -np.inf

    for i in range(rep):
        # Select a leaf
        node: mcts.Node = root
        expand: bool = False
        a_idx = np.intp(-1)
        while True:
            a_idx = node.select_next_action()
            if node.actions[a_idx] == mcts.NullAction: # forced dead end
                break

            if a_idx in node.children:
                node = node.children[a_idx]
            else:
                expand = True
                break

        purity = node.purity_debt
        # If the leaf is a dead end, we are done,
        # otherwise, expand
        if expand:
            node.add_child(a_idx)
            node = node.children[a_idx]
            purity = node.purity_debt

            # evaluate by randomly selecting actions
            state = node.state
            actions = node.actions

            while len(actions) > 0:
                b_idx = random.randrange(0, len(actions))

                if actions[b_idx] == mcts.NullAction:
                    break

                purity += actions[b_idx][0].purity
                state = mcts.apply_action(state, actions[b_idx])
                actions = mcts.get_actions(state)

            num_hist = state[0]
        else:
            num_hist = node.state[0]

        weight = mcts.accuracy(num_hist[0], target) * mcts.ACCURACY_WEIGHT + purity
        node.back_propagate(weight)

        if weight > best_weight:
            best_num_hist = num_hist
            best_weight = weight

        if i % 10_000 == 0:
            print(root.child_weight_sum)
            print(root.child_num_visits)
            print(root.child_weight_sum / root.child_num_visits)
            print(np.sqrt(root.child_weight_sos / root.child_num_visits - (root.child_weight_sum / root.child_num_visits) ** 2))

    if -best_weight < math.log(2) * mcts.ACCURACY_WEIGHT:
        print("Found:", best_num_hist[1])
        print("Purity:", best_weight)
    else:
        print("Failed")
        print("Closest solution: Attains", best_num_hist[0], "with loss", 
              best_weight, "using", best_num_hist[1])

if __name__ == "__main__":
    inputs: list[tuple[Num, str]] = []
    N: int = int(input("Number of inputs: "))
    for i in range(N):
        num = input("Next number: ").strip()
        inputs.append((Num(num), num))

    target = Num(input("Target number: "))

    run_mcts(tuple(inputs), target)

    """
    res, pur = old_search(tuple(inputs), target)
    if pur == fail:
        print("No solution found")
    else: 
        print("Found:", res)
        print("Purity:", pur)
    """
