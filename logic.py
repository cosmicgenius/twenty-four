import operator
from fractions import Fraction
from typing import Callable
from math import log, prod, isqrt

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
NumHist = tuple[Num, str]

def is_atom(n: Num, hist: str) -> bool:
    return n == n.__floor__() and n >= 0 and hist == str(n)

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

    def __str__(self) -> str:
        return str(self.op) + str(self.arity) + str(self.purity)
    
    def __hash__(self) -> int:
        return hash(str(self))

any_domain = lambda *_: True

def floordiv(a: Num, b: Num) -> Num:
    return Num(a // b)

def factorial(n: Num) -> Num:
    return Num(prod(range(1, int(n) + 1)))

def sqrt(f: Num) -> Num:
    return Num(isqrt(f.numerator), isqrt(f.denominator))

# this must be sorted in decreasing order of purity 
# so that we can prioritize pure solutions when discarding 
# searches that reach the same values 
op_table: list[Op] = [
    Op(operator.add,      2, any_domain,          True , "($1 + $2)", 0),
    Op(operator.sub,      2, any_domain,          False, "($1 - $2)", 0),
    Op(operator.mul,      2, any_domain,          True , "($1 * $2)", 0),
    Op(operator.truediv,  2, lambda _, d: d != 0, False, "($1 / $2)", 0),
    Op(operator.pow,      2, lambda a, e: 
       e == e.__floor__() and (a != 0 or e > 0) and (a == 0 or abs(log(abs(a)) * e) <= 25), 
       # prevent undefined, irrational, or very big pows
       False, "($1 ^ $2)", -1),
    Op(operator.mod,      2, lambda n, d: 
       d > 0 and n == n.__floor__() and d == d.__floor__(),
       False, "($1 % $2)", -3),
    Op(factorial,         1, lambda n: 
       n == n.__floor__() and ((n > 2 and n <= 10) or n == 0), # prevent very big factorials, also infinite loops 1!, 2!
        False, "$1!", -5),
    Op(floordiv, 2, lambda _, d: d != 0, False, "($1 // $2)", -10),
    Op(sqrt, 1, lambda f: 
       f >= 0 and f.numerator == isqrt(f.numerator) ** 2 and f.denominator == isqrt(f.denominator)
       and f != 0 and f != 1, # prevent infinite loops
       False, "sqrt($1)", -10),
]
