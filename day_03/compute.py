import dataclasses
import re
from argparse import ArgumentParser
from pathlib import Path
from typing import Self


@dataclasses.dataclass(kw_only=True, frozen=True)
class Mult:
    first: int
    second: int
    is_active: bool

    def value(self) -> int:
        return self.first * self.second

    @classmethod
    def _build_activation_block(cls, data: str) -> dict[int, bool]:
        activation_block = {0: True}

        activation_idx = 0
        while (activation_idx := data.find("do()", activation_idx)) > 0:
            activation_block[activation_idx] = True
            activation_idx += 4

        deactivation_idx = 0
        while (deactivation_idx := data.find("don't()", deactivation_idx)) > 0:
            activation_block[deactivation_idx] = False
            deactivation_idx += 7

        return activation_block

    @classmethod
    def _mult_is_active(cls, offset: int, activation_block: dict[int, bool]) -> bool:
        changes = sorted(activation_block.keys())

        start = changes[0]
        for end in changes[1:]:
            if start < offset < end:
                return activation_block[start]
            start = end
        print(f"{offset=} is_active={activation_block[start]}")
        return activation_block[start]

    @classmethod
    def from_file(cls, filename: Path | str) -> list[Self]:
        lines = ""
        print(f"Loading {filename}")
        with open(filename, "r") as fin:
            for line in fin:
                lines += line

        activation_block = cls._build_activation_block(lines)
        print(f"  built {activation_block=}")

        op_pattern = re.compile(r"mul\((\d{1,3}),(\d{1,3})\)")
        operations = []
        start = 0
        while (next_mul := lines.find("mul(", start)) > 0:
            is_active = cls._mult_is_active(next_mul, activation_block)
            if match := op_pattern.match(lines[next_mul:]):
                operations.append(cls(first=int(match.group(1)), second=int(match.group(2)), is_active=is_active))

            start = next_mul + 4

        return operations


def q1_lazy_mult(data: list[Mult]) -> int:
    return sum((op.value() for op in data))


def q2_active_mult(data: list[Mult]) -> int:
    return sum((op.value() for op in data if op.is_active))


def main(filename: str):
    operations = Mult.from_file(filename)
    q1 = q1_lazy_mult(operations)
    print(f"Q1: lazy mult {q1}")
    q2 = q2_active_mult(operations)
    print(f"Q2: active mult {q2}")


if __name__ == "__main__":
    fd = Path(__file__).parent.absolute() / "input.txt"
    parser = ArgumentParser()
    parser.add_argument("--input", type=str, default=str(fd), help="Input file")
    args = parser.parse_args()

    main(args.input)
