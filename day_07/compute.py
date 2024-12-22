import dataclasses
from argparse import ArgumentParser
from itertools import product
from pathlib import Path
from typing import Self, Callable


def mult(a: int, b: int) -> int:
    return a * b


def add(a: int, b: int) -> int:
    return a + b


Operator = Callable[[int, int], int]


@dataclasses.dataclass(frozen=True, kw_only=True)
class Equation:
    numbers: list[int]
    total: int

    def __repr__(self):
        return f"E({self.total}, [{','.join(map(str, self.numbers))}])"

    @classmethod
    def from_file(cls, filename: Path | str) -> list[Self]:
        print(f"Loading {filename}")
        loaded = []
        with open(filename, "r") as fin:
            for line in fin:
                line = line.replace("\n", "")
                if not line:
                    continue
                lhs, rhs = line.split(":")
                loaded.append(cls(numbers=list(map(int, rhs.strip().split(" "))), total=int(lhs.strip())))
        return loaded

    def calculate(self, operations: list[Operator]) -> int:
        current = self.numbers[0]
        for i, operator in enumerate(operations, start=1):
            current = operator(current, self.numbers[i])

        # print(f"{self} with {operations} = {current}")
        return current

    def brute_resolve(self) -> list[Operator] | None:
        pos = [add, mult]
        prod_args = [pos for _ in range(len(self.numbers) - 1)]
        attempts = list(product(*prod_args))
        for op in attempts:
            if self.calculate(op) == self.total:
                return op
        return None


DataSet = list[Equation]


def q1_brute(dataset: DataSet) -> int:
    return sum((equation.total for equation in dataset if equation.brute_resolve() is not None))


def main(filename: str):
    dataset = Equation.from_file(filename)
    q1 = q1_brute(dataset)
    print(f"Q1: checksum {q1}")


if __name__ == "__main__":
    fd = Path(__file__).parent.absolute() / "input.txt"
    parser = ArgumentParser()
    parser.add_argument("--input", type=str, default=str(fd), help="Input file")
    args = parser.parse_args()

    main(args.input)
