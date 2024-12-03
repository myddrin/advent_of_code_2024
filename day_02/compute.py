import dataclasses
from argparse import ArgumentParser
from pathlib import Path
from typing import Self, ClassVar


@dataclasses.dataclass
class Report:
    data: list[int]

    @classmethod
    def from_file(cls, filename: Path | str) -> list[Self]:
        loaded = []
        print(f"Loading {filename}")
        with open(filename, "r") as fin:
            for line in fin:
                line = line.strip()
                if not line:
                    continue
                loaded.append(cls(data=list(map(int, line.split(" ")))))
        return loaded

    MIN_DIFF: ClassVar[int] = 1
    MAX_DIFF: ClassVar[int] = 3

    def is_safe(self) -> bool:
        current = self.data[0]
        last_diff_is_positive = None

        for next_entry in self.data[1:]:
            diff = next_entry - current
            current_diff_is_positive = diff > 0

            if not (self.MIN_DIFF <= abs(diff) <= self.MAX_DIFF):
                # print(f"Found {diff=}")
                return False
            if last_diff_is_positive is not None and current_diff_is_positive is not last_diff_is_positive:
                # print(f"Found {last_diff_is_positive=} but {current_diff_is_positive=}")
                return False

            last_diff_is_positive = diff > 0
            current = next_entry
        return True


def q1_count_safe(data: list[Report]) -> int:
    total_safe = 0
    for report in data:
        if report.is_safe():
            total_safe += 1
    return total_safe


def main(filename: str):
    all_reports = Report.from_file(filename)
    q1 = q1_count_safe(all_reports)
    print(f"Q1: {q1} safe reports found")


if __name__ == "__main__":
    fd = Path(__file__).parent.absolute() / "input.txt"
    parser = ArgumentParser()
    parser.add_argument("--input", type=str, default=str(fd), help="Input file")
    args = parser.parse_args()

    main(args.input)
