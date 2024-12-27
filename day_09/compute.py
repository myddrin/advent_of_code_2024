import dataclasses
from argparse import ArgumentParser
from copy import deepcopy
from pathlib import Path
from typing import Self


@dataclasses.dataclass(frozen=True)
class Offset:
    offset: int
    size: int

    @property
    def last(self) -> int:
        return self.offset + self.size - 1

    def __lt__(self, other: Self) -> bool:
        return self.offset < other.offset

    def checksum(self, file_id: int) -> int:
        return sum((i * file_id for i in range(self.offset, self.offset + self.size)))


@dataclasses.dataclass
class Disk:
    disk_size: int = 0
    file_map: dict[int, list[Offset]] = dataclasses.field(default_factory=dict)
    free_spaces: list[Offset] = dataclasses.field(default_factory=list)

    @property
    def free_size(self) -> int:
        return sum((offset.size for offset in self.free_spaces))

    @property
    def file_size(self) -> int:
        return sum((sum((off.size for off in offsets)) for offsets in self.file_map.values()))

    @classmethod
    def from_file(cls, filename: Path | str) -> Self:
        print(f"Loading {filename}")
        obj = cls()
        current_file_id = 0
        current_offset = 0
        with open(filename, "r") as fin:
            for line in fin:
                line = line.rstrip("\n")
                if not line:
                    continue
                for i, size in enumerate(map(int, line)):
                    size = size
                    offset = Offset(current_offset, size)
                    is_file = i % 2 == 0
                    if is_file:
                        obj.file_map[current_file_id] = [offset]
                        current_file_id += 1
                    else:
                        obj.free_spaces.append(offset)
                    current_offset += size

        obj.disk_size = current_offset
        assert obj.free_size + obj.file_size == obj.disk_size
        print(f"  -> Loaded {len(obj.file_map)} files and {len(obj.free_spaces)} free spaces")
        print(f"  -> Free {obj.free_size}/{obj.disk_size}")
        return obj

    def _first_free_space(self, *, right_of: int, left_of: int) -> Offset | None:
        # if self.free_spaces and (found := self.free_spaces[0]).offset < left_of:
        #     return found
        for space in self.free_spaces:
            if right_of < space.offset < left_of:
                return space

    def _fragment_to_free_space(self, file_id: int):
        this_file_map = self.file_map[file_id]
        size_unmoved = sum((off.size for off in this_file_map))
        original_left_most = this_file_map[0].offset
        # print(f"Fragmenting {file_id=} left_most={original_left_most} right_most={this_file_map[-1].last}")
        this_file_map = []

        while size_unmoved and (found := self._first_free_space(right_of=0, left_of=original_left_most)):
            self.free_spaces.remove(found)
            if found.size <= size_unmoved:
                this_file_map.append(found)
                size_unmoved -= found.size
            else:
                # remove original one!
                this_file_map.append(
                    Offset(
                        found.offset,
                        size_unmoved,
                    )
                )
                left_free = Offset(
                    found.offset + size_unmoved,
                    found.size - size_unmoved,
                )
                size_unmoved = 0
                self.free_spaces.insert(0, left_free)

        if size_unmoved:
            this_file_map.append(Offset(original_left_most, size_unmoved))
        self.file_map[file_id] = this_file_map
        # this_file_map = self.file_map[file_id]
        print(f"  -> {file_id=} left_most={this_file_map[0].offset} right_most={this_file_map[-1].last}")

    def _move_to_free_space(self, file_id: int):
        assert len(self.file_map[file_id]) == 1, "lazy logic"
        size = self.file_map[file_id][0].size
        left_most = self.file_map[file_id][0].offset
        last_found = 0

        while found := self._first_free_space(right_of=last_found, left_of=left_most):
            if found.size >= size:
                self.free_spaces.remove(found)
                new_file = Offset(
                    found.offset,
                    size,
                )
                new_free = Offset(
                    new_file.last + 1,
                    found.size - size,
                )
                self.file_map[file_id] = [new_file]
                if new_free.size > 0:
                    self.free_spaces.insert(0, new_free)
                print(f"  -> {file_id=} moved from left_most={left_most}..{new_file.offset}")
                return
            else:
                last_found = found.offset

        if found is None:
            print(f"  -> {file_id=} does not move")

    def compress(self) -> Self:
        obj = deepcopy(self)
        for file_id in sorted(obj.file_map.keys(), reverse=True):
            obj._fragment_to_free_space(file_id)
        return obj

    def defragment(self) -> Self:
        obj = deepcopy(self)
        for file_id in sorted(obj.file_map.keys(), reverse=True):
            obj._move_to_free_space(file_id)
        return obj

    def checksum(self) -> int:
        return sum((sum((off.checksum(file_id) for off in offset)) for file_id, offset in self.file_map.items()))

    def to_file(self, filename: Path | str):
        print(f"Writing {filename}")
        with open(filename, "w") as fout:
            disk_map = ["." for _ in range(self.disk_size)]
            for file_id, offsets in self.file_map.items():
                for off in offsets:
                    for i in range(off.offset, off.last + 1):
                        disk_map[i] = f"{file_id:04d}"
            fout.write(",".join(disk_map) + "\n")


def main(filename: str, output_base: str | None):
    if output_base and not output_base.endswith(".txt"):
        output_base += ".txt"
    disk = Disk.from_file(filename)
    if output_base:
        disk.to_file(f"initial_{output_base}")
    q1_disk = disk.compress()
    q1 = q1_disk.checksum()
    print(f"Q1: checksum after fragmentation is {q1}")
    if output_base:
        q1_disk.to_file(f"q1_{output_base}")
    q2_disk = disk.defragment()
    q2 = q2_disk.checksum()
    print(f"Q2: checksum after defragmentation is {q2}")
    if output_base:
        q2_disk.to_file(f"q2_{output_base}")


if __name__ == "__main__":
    fd = Path(__file__).parent.absolute() / "input.txt"
    parser = ArgumentParser()
    parser.add_argument("--input", type=str, default=str(fd), help="Input file")
    parser.add_argument("--output", type=str, help="Base output filename")
    args = parser.parse_args()

    main(args.input, args.output)
