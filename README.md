# Twenty-four

A solver for the generalized [24 game](https://en.wikipedia.org/wiki/24_(puzzle)) 
and its variants
(e.g. [Four fours](https://en.wikipedia.org/wiki/Four_fours)). 
The [main branch](https://github.com/cosmicgenius/twenty-four/tree/main) 
currently holds a basic complete search, while a better 
MCTS based algorithm is being developed in the 
[mcts branch](https://github.com/cosmicgenius/twenty-four/tree/mcts).

### Basics of the Game

The object of the game is to construct an expression 
equal to a target value (e.g. 23) given some input numbers 
(e.g. 4, 4, 4, and 4) while maximizing a score called "purity"
(an idea I was first introduced to 
[here](https://artofproblemsolving.com/community/c3h1576542)).
For example, one possible solution is 4! - 4 ^ (4 - 4) = 23.

Solutions are given a purity score like so: each operation 
used is assigned a purity score (a nonpositive integer, 
more positive is better) according 
to the following table, and then summed:

| Operation        | Symbol | Arity  | Purity | Example     |
| ---------------- | ------ | ------ | ------ | ----------- |
| Addition         | +      | 2      | 0      | 2 + 2 = 4   |
| Subtraction      | -      | 2      | 0      | 4 - 1 = 3   |
| Multiplication   | *      | 2      | 0      | 3 * 4 = 12  |
| Division         | /      | 2      | 0      | 6 / 2 = 3   |
| Negation         | -      | 1      | 0      | 6 / 2 = 3   |
| Exponentiation   | ^      | 2      | -1     | 2 ^ 4 = 16  |
| Modulus          | %      | 2      | -3     | 7 % 4 = 3   |
| Factorial        | !      | 1      | -5     | 5! = 120    |
| Divide and floor | //     | 2      | -10    | 5 // 3 = 1  |
| Square Root      | sqrt   | 1      | -10    | sqrt(9) = 3 |

(arity refers to the number of operands taken, only these operations 
are allowed currently).

For example, the solution 4! - 4 ^ (4 - 4) = 23 has
purity -5 + 0 - 1 + 0 = -6. 
