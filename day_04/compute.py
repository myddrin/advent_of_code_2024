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

    def is_cross(self, left_word: str, right_word: str, *, pos: Position) -> bool:
        cross_1 = [
            Position(-1, -1),
            Position(1, 1),
        ]
        cross_2 = [
            Position(1, -1),
            Position(-1, 1),
        ]
        for cross in (cross_1, cross_2):
            forward = self.is_in_word(left_word, i=0, pos=pos, vect=cross[0]) and self.is_in_word(
                right_word, i=0, pos=pos, vect=cross[1]
            )
            backward = self.is_in_word(left_word, i=0, pos=pos, vect=cross[1]) and self.is_in_word(
                right_word, i=0, pos=pos, vect=cross[0]
            )
            if not (forward or backward):
                return False

        return True

    def search(self, word: str) -> list[Word]:
        all_vectors = Position.neighbours()
        found = []
        for start_position in self.rev_map[word[0]]:
            for vect in all_vectors:
                if self.is_in_word(word, i=1, pos=start_position + vect, vect=vect):
                    found.append((start_position, vect))
        return found

    def search_x(self, word: str) -> list[Position]:
        if len(word) % 2 == 0:
            raise ValueError("Word needs to have an easy middle")
        middle_idx = len(word) // 2
        left_word = "".join(reversed(word[: middle_idx + 1]))
        right_word = word[middle_idx:]

        found = []
        for middle_position in self.rev_map[word[middle_idx]]:
            print(f"Looking for {left_word=} {right_word=} from {middle_position=}")
            if self.is_cross(left_word, right_word, pos=middle_position):
                found.append(middle_position)
        return found


def q1_find_xmas(card: Card) -> int:
    return len(card.search("XMAS"))


def q2_find_x_mas(card: Card) -> int:
    return len(card.search_x("MAS"))


def main(filename: str):
    data = Card.from_file(filename)
    q1 = q1_find_xmas(data)
    print(f"Q1: {q1} XMAS")
    q2 = q2_find_x_mas(data)
    print(f"Q2: {q2} X-MAS")


if __name__ == "__main__":
    fd = Path(__file__).parent.absolute() / "input.txt"
    parser = ArgumentParser()
    parser.add_argument("--input", type=str, default=str(fd), help="Input file")
    args = parser.parse_args()

    main(args.input)
