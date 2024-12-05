import dataclasses
import re
from argparse import ArgumentParser
from pathlib import Path
from typing import Self


@dataclasses.dataclass
class Mult:
    first: int
    second: int

    def value(self) -> int:
        return self.first * self.second

    @classmethod
    def from_file(cls, filename: Path | str) -> list[Self]:
        lines = ""
        print(f"Loading {filename}")
        with open(filename, "r") as fin:
            for line in fin:
                lines += line

        pattern = re.compile(r"mul\((\d{1,3}),(\d{1,3})\)")
        operations = []
        for parts in pattern.findall(lines):
            operations.append(
                cls(
                    int(parts[0]),
                    int(parts[1]),
                )
            )
        return operations


def q1_lazy_mult(data: list[Mult]) -> int:
    return sum((op.value() for op in data))


def main(filename: str):
    operations = Mult.from_file(filename)
    q1 = q1_lazy_mult(operations)
    print(f"Q1: lazy mult {q1}")


if __name__ == "__main__":
    fd = Path(__file__).parent.absolute() / "input.txt"
    parser = ArgumentParser()
    parser.add_argument("--input", type=str, default=str(fd), help="Input file")
    args = parser.parse_args()

    main(args.input)
