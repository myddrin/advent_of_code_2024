from pathlib import Path

import pytest

from day_09.compute import Disk


@pytest.fixture(scope="session")
def small_ex_txt() -> Disk:
    return Disk.from_file(Path(__file__).parent.absolute() / "small_ex.txt")


@pytest.fixture(scope="session")
def input_txt() -> Disk:
    return Disk.from_file(Path(__file__).parent.absolute() / "input.txt")


def test_load_small_ex(small_ex_txt):
    assert small_ex_txt.file_size == 28
    assert small_ex_txt.free_size == 14
    assert small_ex_txt.disk_size == 42


def test_load_input(input_txt):
    assert input_txt.file_size + input_txt.free_size == input_txt.disk_size


def test_q1_small(small_ex_txt):
    disk = small_ex_txt.compress()
    assert disk is not small_ex_txt
    assert disk.file_size == small_ex_txt.file_size
    assert disk.free_size == small_ex_txt.free_size
    assert disk.checksum() == 1928


def test_q2_small(small_ex_txt):
    disk = small_ex_txt.defragment()
    assert disk is not small_ex_txt
    assert disk.file_size == small_ex_txt.file_size
    assert disk.free_size == small_ex_txt.free_size
    assert disk.checksum() == 2858


def test_q1(input_txt):
    disk = input_txt.compress()
    assert disk.file_size + disk.free_size == disk.disk_size
    assert disk.file_size == input_txt.file_size
    assert disk.free_size == input_txt.free_size
    assert disk.checksum() == 6216544403458


def test_q2(input_txt):
    disk = input_txt.defragment()
    assert disk.file_size + disk.free_size == disk.disk_size
    assert disk.file_size == input_txt.file_size
    assert disk.free_size == input_txt.free_size
    assert disk.checksum() == 6237075041489
