from logic import Num
from search import search, fail

if __name__ == "__main__":
    inputs: list[tuple[Num, str]] = []
    N: int = int(input("Number of inputs: "))
    for i in range(N):
        num = input("Next number: ").strip()
        inputs.append((Num(num), num))

    target = Num(input("Target number: "))

    res, pur = search(tuple(inputs), target)
    if pur == fail:
        print("No solution found")
    else: 
        print("Found:", res)
        print("Purity:", pur)

