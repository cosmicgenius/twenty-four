from logic import Num, NumHist, op_table, Op
from typing import Optional
import functools
import itertools
import numpy as np
import math

np.seterr(divide='ignore', invalid='ignore')

Action = tuple[Op, tuple[int, ...]]
NullAction: Action = (Op(lambda: Num(0), 0, lambda: True, True, '', 0), ())

ACCURACY_WEIGHT: float = 1000.0
C: float = 25.0 * ACCURACY_WEIGHT
D: float = 100.0 * ACCURACY_WEIGHT ** 2

LIN_WEIGHT = 2.0

def dist(f: Num, shf: int = 0) -> float:
    return math.log(abs(f.numerator) + abs(f.denominator) + shf)

def accuracy(achieved: Num, target: Num) -> float:
    return max(-dist(Num(achieved - target)) * LIN_WEIGHT, -np.inf if achieved == 0 else -dist(Num(achieved / target), -1))

@functools.lru_cache()
def compute_actions(N: int) -> tuple[Action, ...]:
    res = [] if N > 1 else [NullAction]
    for op in op_table:
        if op.arity == 1: # unary
            res += [(op, (i,)) for i in range(N)]
        if op.arity == 2:
            if op.comm:
                res += [(op, (i,j)) for i, j in itertools.combinations(range(N), 2)]
            else:
                res += [(op, (i,j)) for i, j in itertools.permutations(range(N), 2)]
    return tuple(res)

def is_in_domain(state: tuple[NumHist, ...], a: Action) -> bool: # i.e. in domain
    return a[0].domain(*(state[i][0] for i in a[1]))

def get_actions(state: tuple[NumHist, ...]) -> tuple[Action, ...]:
    actions_no_hist = set() # filter actions based on their raw values, not history
    actions = []

    for a in compute_actions(len(state)):
        if not is_in_domain(state, a):
            continue
        a_no_hist = (str(a[0]), tuple(state[i][0] for i in a[1]))
        if a_no_hist in actions_no_hist:
            continue

        actions_no_hist.add(a_no_hist)
        actions.append(a)
    return tuple(actions)


def apply_action(state: tuple[NumHist, ...], a: Action) -> tuple[NumHist, ...]:
    mask = [1] * len(state)
    for i in a[1]:
        mask[i] = 0
    res: tuple[NumHist, ...] = tuple(itertools.compress(state, mask))

    new_num: Num  = a[0].op(*(state[i][0] for i in a[1]))
    new_hist: str = a[0].pretty(*(state[i][1] for i in a[1]))

    return res + ((new_num, new_hist),)

# Maximize accuracy * ACCURACY_WEIGHT + purity via MCTS
class Node():
    state: tuple[NumHist, ...]
    num_actions: int
    actions: tuple[Action, ...]
    weight_sum: float
    weight_sos: float
    num_visits: int
    purity_debt: int
    child_num_visits: np.ndarray # N
    child_weight_sum: np.ndarray # W
    child_weight_sos: np.ndarray # W
    #child_quality   : np.ndarray # Q
    #child_variance  : np.ndarray # Q
    #child_prior     : np.ndarray # P
    children: dict[np.intp, 'Node'] # bruh
    parent: Optional['Node']
    parent_action_idx: Optional[np.intp]

    # see https://dke.maastrichtuniversity.nl/m.winands/documents/CGSameGame.pdf
    def __init__(self, state: tuple[NumHist, ...], parent: Optional['Node'], parent_action_idx: Optional[np.intp],
                 purity_debt: int = 0):
        self.state = state
        self.actions = get_actions(state)
        self.num_actions = len(self.actions)
        self.weight_sum = 0.0
        self.weight_sos = 0.0
        self.num_visits = 0
        self.purity_debt = purity_debt
        self.child_num_visits = np.zeros(self.num_actions, dtype=int)
        self.child_weight_sum = np.zeros(self.num_actions, dtype=float)
        self.child_weight_sos = np.zeros(self.num_actions, dtype=float)
        #self.child_quality    = np.zeros(self.num_actions, dtype=float)
        #self.child_variance   = np.zeros(self.num_actions, dtype=float)
        #self.child_prior = np.zeros(self.num_actions) 
        self.children = {}
        self.parent = parent
        self.parent_action_idx = parent_action_idx
    
    """
    def update_stats(self) -> None:
        # set Q = W / N, put the average if N = 0
        
        self.child_quality = np.divide(self.child_weight_sum, self.child_num_visits,
                                       out=np.full_like(self.child_weight_sum, self.weight_sum / self.num_visits),
                                       where=(self.child_num_visits != 0))
        self.child_variance = np.divide(self.child_weight_sos, self.child_num_visits,
                                       out=np.full_like(self.child_weight_sos, self.weight_sum / self.num_visits),
                                       where=(self.child_num_visits != 0)) \
                             - self.child_quality ** 2
        
        self.child_quality = self.child_weight_sum / self.child_num_visits
        self.child_variance = self.child_weight_sos / self.child_num_visits - self.child_quality ** 2
    """

    def select_next_action(self) -> np.intp:
        """
        action_val = self.child_quality + C * np.sqrt(
                     np.divide(np.log(self.num_visits), self.child_num_visits,
                               out=np.full_like(self.child_quality, np.log(self.num_visits) / self.num_visits * len(self.children)),
                               where=(self.child_num_visits != 0))
                   ) + np.sqrt(self.child_variance + 
                     np.divide(D, self.child_num_visits,
                               out=np.full_like(self.child_quality, D / self.num_visits * len(self.children)),
                               where=(self.child_num_visits != 0))
                   )
        """
        child_quality = self.child_weight_sum / self.child_num_visits
        child_variance = self.child_weight_sos / self.child_num_visits - child_quality ** 2

        action_val = child_quality + \
                     C * np.sqrt(np.log(self.num_visits) / self.child_num_visits) + \
                     abs(np.sqrt(child_variance + D / self.child_num_visits) / child_quality)

        return np.argmax(action_val)

    def add_child(self, action_idx: np.intp) -> None:
        self.children[action_idx] = Node(apply_action(self.state, self.actions[action_idx]),
                                         self, action_idx,
                                         self.purity_debt + self.actions[action_idx][0].purity)

    def back_propagate(self, weight: float) -> None:
        self.num_visits += 1
        self.weight_sum += weight
        self.weight_sos += weight ** 2

        if self.parent is None or self.parent_action_idx is None:
            return

        self.parent.child_num_visits[self.parent_action_idx] += 1
        self.parent.child_weight_sum[self.parent_action_idx] += weight
        self.parent.child_weight_sos[self.parent_action_idx] += weight ** 2

        self.parent.back_propagate(weight)

