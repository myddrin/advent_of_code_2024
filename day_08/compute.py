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

    def _calculate_antinodes(self, pair: tuple[Position, Position], *, limit: int | None = 1) -> list[Position]:
        v1 = pair[1] - pair[0]
        v0 = pair[0] - pair[1]
        all_found = []
        for start, vector in (
            (pair[0], v0),
            (pair[1], v1),
        ):
            found = []
            pos = start + vector
            while self.contains(pos):
                found.append(pos)
                if limit is not None and len(found) >= limit:
                    break
                pos += vector
            all_found.extend(found)
        if limit is None:
            all_found.extend(pair)

        return all_found

    def populate_antinodes(self, *, limit: int | None = 1) -> int:
        """Returns unique nodes - removes locations of towers"""
        self.antinodes_map = {}
        for freq, nodes in self.frequency_map.items():
            antinodes = set()

            for pair in combinations(nodes, 2):
                antinodes.update(self._calculate_antinodes(pair, limit=limit))
            # print(f"Found {len(antinodes)} antinodes for {freq=} {antinodes}")
            for pos in antinodes:
                if pos not in self.antinodes_map:
                    self.antinodes_map[pos] = []
                self.antinodes_map[pos].append(freq)

        return len(self.antinodes_map)

    def to_file(self, filename: Path | str):
        print(f"Writing to {filename}")
        node_map = {pos: "#" for pos in self.antinodes_map.keys()}
        for freq, nodes in self.frequency_map.items():
            for pos in nodes:
                node_map[pos] = freq
        with open(filename, "w") as fout:
            for y in range(self.height):
                line = []
                for x in range(self.width):
                    pos = Position(x, y)
                    char = node_map.get(pos, ".")
                    line.append(char)
                fout.write("".join(line) + "\n")


def main(filename: str, output_base: str | None):
    if output_base is not None and not output_base.endswith(".txt"):
        output_base += ".txt"
    data = Data.from_file(filename)
    q1 = data.populate_antinodes()
    print(f"Q1: found {q1} antinode locations")
    if output_base:
        data.to_file(f"q1_{output_base}")
    q2 = data.populate_antinodes(limit=None)
    print(f"Q2: found {q2} antinode with resonance")
    if output_base:
        data.to_file(f"q2_{output_base}")


if __name__ == "__main__":
    fd = Path(__file__).parent.absolute() / "input.txt"
    parser = ArgumentParser()
    parser.add_argument("--input", type=str, default=str(fd), help="Input file")
    parser.add_argument("--output", type=str, help="base filename for output")
    args = parser.parse_args()

    main(args.input, args.output)
