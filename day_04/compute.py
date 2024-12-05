import dataclasses
from argparse import ArgumentParser
from collections import defaultdict
from pathlib import Path
from typing import Self


@dataclasses.dataclass(frozen=True)
class Position:
    x: int
    y: int

    @classmethod
    def neighbours(cls) -> list[Self]:
        return [
            Position(-1, -1),
            Position(-1, 0),
            Position(-1, 1),
            Position(0, -1),
            Position(0, 1),
            Position(1, -1),
            Position(1, 0),
            Position(1, 1),
        ]

    def __add__(self, other: Self) -> Self:
        return Position(x=self.x + other.x, y=self.y + other.y)

    def __sub__(self, other: Self) -> Self:
        return Position(x=self.x - other.x, y=self.y - other.y)


Word = tuple[Position, Position]


@dataclasses.dataclass
class Card:
    map: dict[Position, str] = dataclasses.field(default_factory=dict)
    rev_map: dict[str, set[Position]] = dataclasses.field(default_factory=lambda: defaultdict(set))

    @classmethod
    def from_file(cls, filename: Path | str) -> Self:
        print(f"Loading {filename}")

        with open(filename, "r") as fin:
            obj = cls()
            for y, line in enumerate(fin):
                line = line.strip()
                if not line:
                    continue

                for x, char in enumerate(line):
                    p = Position(x, y)
                    obj.map[p] = char
                    obj.rev_map[char].add(p)

        return obj

    def is_in_word(self, word: str, *, i: int, pos: Position, vect: Position) -> bool:
        current_letter = word[i]
        if pos not in self.rev_map[current_letter]:
            return False

        if i + 1 < len(word):
            return self.is_in_word(word, i=i + 1, pos=pos + vect, vect=vect)
        return True

    def search(self, word: str) -> list[Word]:
        all_vectors = Position.neighbours()
        found = []
        for start_position in self.rev_map[word[0]]:
            for vect in all_vectors:
                if self.is_in_word(word, i=1, pos=start_position + vect, vect=vect):
                    found.append((start_position, vect))
        return found


def q1_find_xmas(card: Card) -> int:
    return len(card.search("XMAS"))


def main(filename: str):
    data = Card.from_file(filename)
    q1 = q1_find_xmas(data)
    print(f"Q1: {q1} XMAS")


if __name__ == "__main__":
    fd = Path(__file__).parent.absolute() / "input.txt"
    parser = ArgumentParser()
    parser.add_argument("--input", type=str, default=str(fd), help="Input file")
    args = parser.parse_args()

    main(args.input)
