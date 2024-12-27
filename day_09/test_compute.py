from pathlib import Path

import pytest

from day_09.compute import Disk


@pytest.fixture(scope="session")
def small_ex_txt() -> Disk:
    return Disk.from_file(Path(__file__).parent.absolute() / "small_ex.txt")


@pytest.fixture(scope="session")
def input_txt() -> Disk:
    return Disk.from_file(Path(__file__).parent.absolute() / "input.txt")


def test_q1_small(small_ex_txt):
    disk = small_ex_txt.compress()
    assert disk.checksum() == 1928


def test_q2_small(small_ex_txt):
    disk = small_ex_txt.defragment()
    assert disk.checksum() == 2858


def test_q1(input_txt):
    disk = input_txt.compress()
    assert disk.checksum() == 6216544403458


def test_q2(input_txt):
    disk = input_txt.defragment()
    assert disk.checksum() < 7912125338026
