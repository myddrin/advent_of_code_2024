import dataclasses
import re
from argparse import ArgumentParser
from collections import defaultdict
from pathlib import Path
from typing import Self, ClassVar


@dataclasses.dataclass(kw_only=True, frozen=True)
class Rule:
    first: int
    second: int


@dataclasses.dataclass(kw_only=True, frozen=True)
class Updates:
    pages: list[int]
    is_valid: bool

    @property
    def middle_page(self) -> int:
        if len(self.pages) % 2 == 1:
            return self.pages[len(self.pages) // 2]
        else:
            raise ValueError("Odd update")


class SetOfRules:
    pattern: ClassVar = re.compile(r"(\d+)\|(\d+)")

    def __init__(self):
        self.rules = []
        self.page_rules: dict[int, list[Rule]] = defaultdict(list)
        self.updates: list[Updates] = []

    def add_rule(self, line: str) -> bool:
        match = self.pattern.match(line)
        if not match:
            return False

        rule = Rule(first=int(match.group(1)), second=int(match.group(2)))
        self.rules.append(rule)
        self.page_rules[rule.first].append(rule)
        self.page_rules[rule.second].append(rule)
        return True

    def check_valid_update(self, pages: list[int]) -> bool:
        update_idx: dict[int, int] = {page: i for i, page in enumerate(pages)}
        for page in update_idx.keys():
            for potential_rule in self.page_rules[page]:
                first = update_idx.get(potential_rule.first)
                second = update_idx.get(potential_rule.second)
                is_active = first is not None and second is not None
                if is_active and first > second:
                    return False

        return True

    def add_update(self, line: str) -> bool:
        if "," not in line:
            return False
        pages = [int(v) for v in line.split(",")]
        is_valid = self.check_valid_update(pages)
        self.updates.append(Updates(pages=pages, is_valid=is_valid))
        return True

    @classmethod
    def from_file(cls, filename: Path | str) -> Self:
        obj = cls()

        print(f"Loading {filename}")
        with open(filename, "r") as fin:
            for line in fin:
                line = line.strip()
                if not line:
                    continue

                if not obj.add_rule(line):
                    obj.add_update(line)

        return obj


def q1_middle_page(data: SetOfRules) -> int:
    return sum((update.middle_page for update in data.updates if update.is_valid))


def main(filename: str):
    data = SetOfRules.from_file(filename)
    q1 = q1_middle_page(data)
    print(f"Q1: {q1} middle page checksum")


if __name__ == "__main__":
    fd = Path(__file__).parent.absolute() / "input.txt"
    parser = ArgumentParser()
    parser.add_argument("--input", type=str, default=str(fd), help="Input file")
    args = parser.parse_args()

    main(args.input)
