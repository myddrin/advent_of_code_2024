import dataclasses
from argparse import ArgumentParser
from collections import defaultdict
from itertools import combinations
from pathlib import Path
from typing import Self, ClassVar


@dataclasses.dataclass(frozen=True)
class Position:
    x: int
    y: int

    def __add__(self, other: Self) -> Self:
        return Position(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Self) -> Self:
        return Position(
            self.x - other.x,
            self.y - other.y,
        )

    def __repr__(self):
        return f"P({self.x}, {self.y})"


@dataclasses.dataclass
class Data:
    SKIP: ClassVar = {"."}

    width: int
    height: int
    frequency_map: dict[str, list[Position]]

    antinodes_map: dict[Position, list[str]] = dataclasses.field(default_factory=dict)

    @classmethod
    def from_file(cls, filename: Path | str) -> Self:
        print(f"Loading {filename}")
        frequencies = defaultdict(list)
        with open(filename, "r") as fin:
            y = 0
            x = 0
            for y, line in enumerate(fin):
                line = line.replace("\n", "")
                if not line:
                    continue
                for x, char in enumerate(line):
                    if char not in cls.SKIP:
                        frequencies[char].append(Position(x, y))

        return cls(
            x + 1,
            y + 1,
            frequencies,
        )

    def contains(self, position: Position) -> bool:
        return (0 <= position.x < self.width) and (0 <= position.y < self.height)

    def _calculate_antinode(self, pair: tuple[Position, Position]) -> list[Position]:
        vector = pair[1] - pair[0]
        results = [
            pair[0] - vector,
            pair[1] + vector,
        ]
        return [pos for pos in results if self.contains(pos)]

    def populate_antinodes(self) -> int:
        """Returns unique nodes - removes locations of towers"""
        self.antinodes_map = {}
        for freq, nodes in self.frequency_map.items():
            antinodes = set()

            for pair in combinations(nodes, 2):
                antinodes.update(self._calculate_antinode(pair))
            # print(f"Found {len(antinodes)} antinodes for {freq=} {antinodes}")
            for pos in antinodes:
                if pos not in self.antinodes_map:
                    self.antinodes_map[pos] = []
                self.antinodes_map[pos].append(freq)

        return len(self.antinodes_map)


def main(filename: str):
    data = Data.from_file(filename)
    q1 = data.populate_antinodes()
    print(f"Q1: found {q1} antinode locations")


if __name__ == "__main__":
    fd = Path(__file__).parent.absolute() / "input.txt"
    parser = ArgumentParser()
    parser.add_argument("--input", type=str, default=str(fd), help="Input file")
    args = parser.parse_args()

    main(args.input)
