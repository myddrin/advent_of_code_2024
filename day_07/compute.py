import dataclasses
from argparse import ArgumentParser
from itertools import product
from pathlib import Path
from typing import Self, Callable


def multiply(a: int, b: int) -> int:
    return a * b


def add(a: int, b: int) -> int:
    return a + b


_power_table = {}


def concatenate(a: int, b: int) -> int:
    n = len(str(b))
    mult = _power_table[n]
    return a * mult + b


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
        max_number_len = 0
        with open(filename, "r") as fin:
            for line in fin:
                line = line.replace("\n", "")
                if not line:
                    continue
                lhs, rhs = line.split(":")
                number_strings = rhs.strip().split(" ")
                max_number_len = max([len(s) for s in number_strings] + [max_number_len])
                loaded.append(cls(numbers=list(map(int, number_strings)), total=int(lhs.strip())))
            # preload powers
            _power_table.update({n: pow(10, n) for n in range(max_number_len + 1)})
        return loaded

    def calculate(self, operations: list[Operator]) -> int:
        current = self.numbers[0]
        for i, operator in enumerate(operations, start=1):
            current = operator(current, self.numbers[i])
        return current

    def brute_resolve(self, *, operations: list[Operator], verbose: bool = False) -> list[Operator] | None:
        prod_args = [operations for _ in range(len(self.numbers) - 1)]
        attempts = list(product(*prod_args))
        for op in attempts:
            value = self.calculate(op)
            if value == self.total:
                return op
        if verbose:
            print(f"  -> {self} noop")
        return None


DataSet = list[Equation]


def brute_resolve(
    dataset: DataSet,
    operations: list[Operator],
    *,
    verbose: bool,
) -> int:
    return sum(
        (
            equation.total
            for equation in dataset
            if equation.brute_resolve(operations=operations, verbose=verbose) is not None
        )
    )


def q1_brute(dataset: DataSet) -> int:
    return brute_resolve(dataset, operations=[add, multiply], verbose=False)


def q2_brute(dataset: DataSet, *, verbose: bool) -> int:
    return brute_resolve(dataset, operations=[add, multiply, concatenate], verbose=verbose)


def main(filename: str, verbose: bool):
    dataset = Equation.from_file(filename)
    q1 = q1_brute(dataset)

    q2 = q2_brute(dataset, verbose=verbose)
    print(f"Q1: checksum {q1}")
    print(f"Q2: checksum {q2}")


if __name__ == "__main__":
    fd = Path(__file__).parent.absolute() / "input.txt"
    parser = ArgumentParser()
    parser.add_argument("--input", type=str, default=str(fd), help="Input file")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    main(args.input, args.verbose)
