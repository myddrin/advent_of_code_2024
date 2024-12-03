import dataclasses
from argparse import ArgumentParser
from pathlib import Path
from typing import Self, ClassVar


class UnsafeDifference(ValueError):
    def __init__(self, *, index: int, message: str):
        super().__init__(message)
        self.index = index

    def __str__(self):
        return super().__str__() + f" at :{self.index}"


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

    def is_safe(self, *, raise_on_error: bool = False) -> bool:
        current = self.data[0]
        diff_is_positive = None

        for i, next_entry in enumerate(self.data[1:], start=1):
            diff = next_entry - current
            current_diff_is_positive = diff > 0

            if not (self.MIN_DIFF <= abs(diff) <= self.MAX_DIFF):
                if not raise_on_error:
                    return False
                raise UnsafeDifference(index=i, message=f"Found {diff=}")
            if diff_is_positive is not None and current_diff_is_positive is not diff_is_positive:
                if not raise_on_error:
                    return False
                raise UnsafeDifference(index=i, message=f"Found {diff_is_positive=} but {current_diff_is_positive=}")

            if diff_is_positive is None:
                diff_is_positive = diff > 0
            current = next_entry
        return True


def q1_count_safe(data: list[Report]) -> int:
    total_safe = 0
    for report in data:
        if report.is_safe():
            total_safe += 1
    return total_safe


def q2_remove_safe(data: list[Report]) -> int:
    total_safe = 0
    for line, report in enumerate(data, start=1):
        try:
            report.is_safe(raise_on_error=True)
        except UnsafeDifference as e:
            brute_to_try = range(len(report.data))
            for i in brute_to_try:
                alt_report = Report(
                    data=list(report.data),
                )
                alt_report.data.pop(i)
                if alt_report.is_safe():
                    total_safe += 1
                    break
            else:
                print(f"Report at {line=} is unsafe {e}")

        else:
            total_safe += 1
    return total_safe


def main(filename: str):
    all_reports = Report.from_file(filename)
    q1 = q1_count_safe(all_reports)
    print(f"Q1: {q1} safe reports found")
    q2 = q2_remove_safe(all_reports)
    print(f"Q1: {q2} safe reports found with dampener")


if __name__ == "__main__":
    fd = Path(__file__).parent.absolute() / "input.txt"
    parser = ArgumentParser()
    parser.add_argument("--input", type=str, default=str(fd), help="Input file")
    args = parser.parse_args()

    main(args.input)
