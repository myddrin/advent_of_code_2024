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

    @property
    def next(self) -> int:
        return self.offset + self.size

    def __lt__(self, other: Self) -> bool:
        return self.offset < other.offset

    def __repr__(self):
        return f"O({self.offset},{self.size})"

    def checksum(self, file_id: int) -> int:
        return sum((i * file_id for i in range(self.offset, self.offset + self.size)))


@dataclasses.dataclass
class Disk:
    disk_size: int = 0
    _file_map: dict[int, list[Offset]] = dataclasses.field(default_factory=dict)
    _free_spaces: dict[int, Offset] = dataclasses.field(default_factory=dict)
    _prev_free_spaces: dict[int, int] = dataclasses.field(default_factory=dict)

    @property
    def free_size(self) -> int:
        return sum((offset.size for offset in self._free_spaces.values()))

    @property
    def file_size(self) -> int:
        return sum((sum((off.size for off in offsets)) for offsets in self._file_map.values()))

    def file(self, file_id: int) -> Offset | None:
        return self._file_map.get(file_id)

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
                        obj._file_map[current_file_id] = [offset]
                        current_file_id += 1
                    else:
                        obj.add_free_space(offset)
                    current_offset += size

        obj.disk_size = current_offset
        assert obj.free_size + obj.file_size == obj.disk_size
        print(f"  -> Loaded {len(obj._file_map)} files and {len(obj._free_spaces)} free spaces")
        print(f"  -> Free {obj.free_size}/{obj.disk_size}")
        return obj

    def first_free_space(self, *, left_of: int, size_gte: int | None = None) -> Offset | None:
        found: Offset | None = None
        for offset, space in self._free_spaces.items():
            if (
                offset < left_of
                and (size_gte is None or space.size >= size_gte)
                and (found is None or offset < found.offset)
            ):
                found = space
        return found

    def add_free_space(self, space: Offset):
        if existing := self._free_spaces.get(space.next):
            self.rem_free_space(existing)
            self.add_free_space(
                Offset(
                    space.offset,
                    space.size + existing.size,
                )
            )
        elif offset := self._prev_free_spaces.get(space.offset):
            existing = self._free_spaces[offset]
            self.rem_free_space(existing)
            self.add_free_space(Offset(existing.offset, existing.size + space.size))
        else:
            self._free_spaces[space.offset] = space
            self._prev_free_spaces[space.next] = space.offset

    def rem_free_space(self, space: Offset) -> None:
        offset = space.offset
        self._free_spaces.pop(offset)
        self._prev_free_spaces.pop(space.next)

    def _fragment_to_free_space(self, file_id: int):
        this_file_map = self._file_map[file_id]
        size_unmoved = sum((off.size for off in this_file_map))
        size_moved = 0
        original_left_most = this_file_map[0].offset
        this_file_map = []

        while size_unmoved and (found := self.first_free_space(left_of=original_left_most)):
            self.rem_free_space(found)
            if found.size <= size_unmoved:
                this_file_map.append(found)
                size_unmoved -= found.size
                size_moved += found.size
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
                size_moved += size_unmoved
                size_unmoved = 0
                self.add_free_space(left_free)

        if size_unmoved:
            this_file_map.append(Offset(original_left_most, size_unmoved))
            new_free_space = Offset(original_left_most + size_moved, size_moved)
        else:
            new_free_space = Offset(original_left_most, size_moved)

        self.add_free_space(new_free_space)
        self._file_map[file_id] = this_file_map

    def _move_to_free_space(self, file_id: int):
        size = 0
        left_most = self.disk_size
        for off in self._file_map[file_id]:
            size += off.size
            left_most = min(left_most, off.offset)

        if found := self.first_free_space(size_gte=size, left_of=left_most):
            self.rem_free_space(found)
            new_file = Offset(
                found.offset,
                size,
            )
            left_free = Offset(
                new_file.last + 1,
                found.size - size,
            )
            if left_free.size > 0:
                self.add_free_space(left_free)
            for space in self._file_map[file_id]:
                self.add_free_space(space)
            self._file_map[file_id] = [new_file]
            # print(f"  -> {file_id=} moved from left_most={left_most}..{new_file.offset}")

        # if found is None:
        #     print(f"  -> {file_id=} does not move")

    def compress(self) -> Self:
        obj = deepcopy(self)
        print("Compressing disk")
        if (n_files := len(obj._file_map)) > 100:
            n_files = len(obj._file_map) // 100
        for file_id in sorted(obj._file_map.keys(), reverse=True):
            obj._fragment_to_free_space(file_id)
            if file_id % n_files == (n_files - 1):
                print(".", end="", flush=True)
        print("")
        return obj

    def defragment(self) -> Self:
        obj = deepcopy(self)
        print("Defragmenting disk")
        if (n_files := len(obj._file_map)) > 100:
            n_files = len(obj._file_map) // 100
        for file_id in sorted(obj._file_map.keys(), reverse=True):
            obj._move_to_free_space(file_id)
            if file_id % n_files == (n_files - 1):
                print(".", end="", flush=True)
        print("")
        return obj

    def checksum(self) -> int:
        return sum((sum((off.checksum(file_id) for off in offset)) for file_id, offset in self._file_map.items()))

    def _size_to_str(self, file_id: int | None, size: int) -> str:
        half = size // 2
        if file_id is None:
            file_str = "----"
        else:
            file_str = f"{file_id:04d}"
        return "".join(["____"] * half) + file_str + "".join(["____"] * (size - half))

    def to_file(self, filename: Path | str):
        print(f"Writing {filename}")
        with open(filename, "w") as fout:
            disk_map = {}
            fout.write(f"free={self.free_size} file={self.file_size} total={self.disk_size}\n")
            fout.write("|")
            for offset in self._free_spaces.values():
                disk_map[offset.offset] = self._size_to_str(None, offset.size)
            for file_id, offsets in self._file_map.items():
                for off in offsets:
                    disk_map[off.offset] = self._size_to_str(file_id, off.size)
            for off in sorted(disk_map.keys()):
                fout.write(disk_map[off] + "|")
            fout.write("\n")


def main(filename: str, output: bool):
    disk = Disk.from_file(filename)
    if output:
        disk.to_file("d9_initial.txt")
    q1_disk = disk.compress()
    q1 = q1_disk.checksum()
    print(f"Q1: checksum after fragmentation is {q1}")
    if output:
        q1_disk.to_file("d9_q1.txt")
    q2_disk = disk.defragment()
    q2 = q2_disk.checksum()
    print(f"Q2: checksum after defragmentation is {q2}")
    if output:
        q2_disk.to_file("d9_q2.txt")


if __name__ == "__main__":
    fd = Path(__file__).parent.absolute() / "input.txt"
    parser = ArgumentParser()
    parser.add_argument("--input", type=str, default=str(fd), help="Input file")
    parser.add_argument("--output", action="store_true", help="Output steps")
    args = parser.parse_args()

    main(args.input, args.output)
