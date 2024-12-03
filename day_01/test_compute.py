from pathlib import Path

import pytest

from day_01.compute import q1, ListData


@pytest.fixture(scope="session")
def small_ex_txt() -> Path:
    return Path(__file__).parent.absolute() / "small_ex.txt"


@pytest.fixture(scope="session")
def input_txt():
    return Path(__file__).parent.absolute() / "input.txt"


def test_q1_ex(small_ex_txt):
    assert q1(ListData.from_file(small_ex_txt)) == 11


def test_q1(input_txt):
    assert q1(ListData.from_file(input_txt)) == 1879048
