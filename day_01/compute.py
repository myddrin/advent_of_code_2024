import dataclasses
import re
from argparse import ArgumentParser
from collections import defaultdict
from pathlib import Path
from typing import Self


@dataclasses.dataclass(kw_only=True, frozen=True)
class ListData:
    list_a: list[int]
    list_b: list[int]

    @classmethod
    def from_file(cls, filename: Path | str) -> Self:
        obj = cls(list_a=[], list_b=[])
        print(f"Loading {filename}")
        pattern = re.compile(r"(\d+)\s+(\d+)")
        with open(filename, "r") as fin:
            for line in fin:
                if match := pattern.match(line):
                    a_str, b_str = match.groups()
                    obj.list_a.append(int(a_str))
                    obj.list_b.append(int(b_str))
        return obj


def q1_distance(list_data: ListData) -> int:
    list_a = sorted(list_data.list_a)
    list_b = sorted(list_data.list_b)
    total_distance = 0
    for i, a in enumerate(list_a):
        total_distance += abs(a - list_b[i])
    return total_distance


def q2_similarity(list_data: ListData) -> int:
    list_b_index = defaultdict(int)
    for entry in list_data.list_b:
        list_b_index[entry] += 1

    total_similarity = 0
    for a in list_data.list_a:
        total_similarity += a * list_b_index.get(a, 0)
    return total_similarity


def main(filename: str):
    list_data = ListData.from_file(filename)
    first = q1_distance(list_data)
    print(f"Q1: total distance: {first}")
    second = q2_similarity(list_data)
    print(f"Q2: similarity: {second}")


if __name__ == "__main__":
    fd = Path(__file__).parent.absolute() / "input.txt"
    parser = ArgumentParser()
    parser.add_argument("--input", type=str, default=str(fd), help="Input file")
    args = parser.parse_args()

    main(args.input)
