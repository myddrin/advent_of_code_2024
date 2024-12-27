from pathlib import Path

import pytest

from day_09.compute import Disk


@pytest.fixture(scope="session")
def small_ex_txt() -> Path:
    return Path(__file__).parent.absolute() / "small_ex.txt"


@pytest.fixture(scope="session")
def input_txt() -> Path:
    return Path(__file__).parent.absolute() / "input.txt"


def test_q1_small(small_ex_txt):
    disk = Disk.from_file(small_ex_txt).compress()
    assert disk.checksum() == 1928


def test_q1(input_txt):
    disk = Disk.from_file(input_txt).compress()
    assert disk.checksum() == 6216544403458
