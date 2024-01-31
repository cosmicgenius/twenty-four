import operator
from fractions import Fraction
from typing import Callable

class Num(Fraction):
    pass
    """
    readable = ''

    def __init__(self, numerator=0, denominator=1):
        super().__init__()
        self.readable = '(' + str(numerator) + ' / ' + str(denominator) + ')' \
                        if denominator != 1 else \
                        str(numerator)
    """


class Op:
    def __init__(self, op: Callable[..., Num], arity: int, domain: Callable[..., bool],
                 comm: bool, readable: str, purity: int) -> None:
        self.op = op
        self.arity = arity
        self.domain = domain
        self.comm = comm
        self.readable = readable
        self.purity = purity

    def pretty(self, *operands: str) -> str:
        # can you regex this?
        res = self.readable
        for n in range(0, self.arity):
            res = res.replace('$' + str(n + 1), operands[n])
        return res


# Stores pairs (operator, purity, )
any_domain = lambda *_: True

unary_op: list[Op] = []
binary_op: list[Op] = [
    Op(operator.add,     2, any_domain,          True , "($1 + $2)", 0),
    Op(operator.sub,     2, any_domain,          False, "($1 - $2)", 0),
    Op(operator.mul,     2, any_domain,          True , "($1 * $2)", 0),
    Op(operator.truediv, 2, lambda _, d: d != 0, False, "($1 / $2)", 0),
    Op(operator.pow,     2, lambda a, e: 
       e == e.__floor__() and (a != 0 or e > 0) and (e < 100), # prevent very bad pows
       False, "($1 ^ $2)", -1),
]
