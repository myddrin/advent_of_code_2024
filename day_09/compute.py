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

    def __repr__(self):
        return f"O({self.offset},{self.size})"

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

    def _consolidate_free_spaces(self):
        free_spaces = sorted(self.free_spaces)
        # free_spaces = self.free_spaces
        self.free_spaces = [free_spaces[0]]
        for current in free_spaces[1:]:
            last = self.free_spaces[-1]
            if last.last + 1 == current.offset:
                self.free_spaces.pop(-1)
                self.free_spaces.append(Offset(last.offset, last.size + current.size))
            else:
                self.free_spaces.append(current)

    def _fragment_to_free_space(self, file_id: int):
        this_file_map = self.file_map[file_id]
        size_unmoved = sum((off.size for off in this_file_map))
        size_moved = 0
        original_left_most = this_file_map[0].offset
        # print(f"Fragmenting {file_id=} left_most={original_left_most} right_most={this_file_map[-1].last}")
        this_file_map = []

        while size_unmoved and (found := self._first_free_space(right_of=0, left_of=original_left_most)):
            self.free_spaces.remove(found)
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
                self.free_spaces.insert(0, left_free)
                # self.free_spaces.append(left_free)

        if size_unmoved:
            this_file_map.append(Offset(original_left_most, size_unmoved))
            self.free_spaces.append(Offset(original_left_most + size_moved, size_moved))
        else:
            self.free_spaces.append(Offset(original_left_most, size_moved))

        self.file_map[file_id] = this_file_map
        # self.free_spaces = sorted(self.free_spaces)
        self._consolidate_free_spaces()

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
                    # self.free_spaces.append(new_free)
                # print(f"  -> {file_id=} moved from left_most={left_most}..{new_file.offset}")
                self.free_spaces.append(Offset(left_most, size))
                break
            else:
                last_found = found.offset

        # self.free_spaces = sorted(self.free_spaces)
        self._consolidate_free_spaces()
        # if found is None:
        #     print(f"  -> {file_id=} does not move")

    def compress(self) -> Self:
        obj = deepcopy(self)
        print("Compressing disk")
        if (n_files := len(obj.file_map)) > 100:
            n_files = len(obj.file_map) // 100
        for file_id in sorted(obj.file_map.keys(), reverse=True):
            obj._fragment_to_free_space(file_id)
            if file_id % n_files == (n_files - 1):
                print(".", end="", flush=True)
        print("")
        return obj

    def defragment(self) -> Self:
        obj = deepcopy(self)
        print("Defragmenting disk")
        if (n_files := len(obj.file_map)) > 100:
            n_files = len(obj.file_map) // 100
        for file_id in sorted(obj.file_map.keys(), reverse=True):
            obj._move_to_free_space(file_id)
            if file_id % n_files == (n_files - 1):
                print(".", end="", flush=True)
        print("")
        return obj

    def checksum(self) -> int:
        return sum((sum((off.checksum(file_id) for off in offset)) for file_id, offset in self.file_map.items()))

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
            for offset in self.free_spaces:
                disk_map[offset.offset] = self._size_to_str(None, offset.size)
            for file_id, offsets in self.file_map.items():
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
