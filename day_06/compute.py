import dataclasses
from argparse import ArgumentParser
from enum import Enum
from pathlib import Path
from typing import Self, ClassVar


@dataclasses.dataclass(frozen=True)
class Position:
    x: int
    y: int

    def __add__(self, other: Self) -> Self:
        return Position(
            self.x + other.x,
            self.y + other.y,
        )

    def __repr__(self):
        return f"({self.x}, {self.y})"


class Direction(Enum):
    UP = Position(0, -1)
    RIGHT = Position(1, 0)
    DOWN = Position(0, 1)
    LEFT = Position(-1, 0)

    @classmethod
    def from_str(cls, char: str) -> Self:
        match char:
            case "^":
                return cls.UP
            case ">":
                return cls.RIGHT
            case "v":
                return cls.DOWN
            case "<":
                return cls.LEFT
        raise NotImplementedError(f"For {char=}")


@dataclasses.dataclass(kw_only=True)
class Guard:
    location: Position
    facing: Direction

    def rotate_90_clock(self) -> None:
        match self.facing:
            case Direction.UP:
                self.facing = Direction.RIGHT
            case Direction.RIGHT:
                self.facing = Direction.DOWN
            case Direction.DOWN:
                self.facing = Direction.LEFT
            case Direction.LEFT:
                self.facing = Direction.UP
            case _:
                raise NotImplementedError(f"For {self.facing.name}")

    def __repr__(self):
        return f"@ {self.location} facing {self.facing.name}"


@dataclasses.dataclass(kw_only=True)
class Map:
    EMPTY: ClassVar = "."
    OBSTACLE: ClassVar = "#"

    width: int
    height: int
    guard: Guard
    obstacles: set[Position] = dataclasses.field(default_factory=set)

    @classmethod
    def from_file(cls, filename: Path | str) -> Self:
        print(f"Loading {filename}")
        obstacles = set()
        guard = None
        with open(filename, "r") as fin:
            y = 0
            for y, line in enumerate(fin):
                line = line.replace("\n", "")
                if not line:
                    continue
                x = 0
                for x, char in enumerate(line):
                    match char:
                        case cls.EMPTY:
                            continue
                        case cls.OBSTACLE:
                            obstacles.add(Position(x, y))
                        case _:
                            guard = Guard(
                                location=Position(x, y),
                                facing=Direction.from_str(char),
                            )
        if guard is None:
            raise ValueError("Did not find the guard")
        print(f"Loaded a grid of {x + 1}x{y + 1}")
        return cls(
            width=x + 1,
            height=y + 1,
            obstacles=obstacles,
            guard=guard,
        )

    def contains_position(self, p: Position) -> bool:
        return 0 <= p.x < self.width and 0 <= p.y < self.height

    def predict_guard(self) -> list[Position]:
        current_guard = Guard(
            location=self.guard.location,
            facing=self.guard.facing,
        )
        visited = [self.guard.location]
        print(f"Starting {current_guard}")
        while self.contains_position(current_guard.location):
            if current_guard.location != visited[-1]:
                visited.append(current_guard.location)

            next_position = current_guard.location + current_guard.facing.value
            if next_position in self.obstacles:
                current_guard.rotate_90_clock()
            else:
                current_guard.location = next_position

        return visited


def main(filename: str):
    map = Map.from_file(filename)
    q1 = len(set(map.predict_guard()))
    print(f"Q1: the guard visited {q1} locations")


if __name__ == "__main__":
    fd = Path(__file__).parent.absolute() / "input.txt"
    parser = ArgumentParser()
    parser.add_argument("--input", type=str, default=str(fd), help="Input file")
    args = parser.parse_args()

    main(args.input)
