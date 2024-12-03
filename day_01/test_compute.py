from pathlib import Path

import pytest

from day_01.compute import q1_distance, ListData, q2_similarity


@pytest.fixture(scope="session")
def small_ex_txt() -> ListData:
    return ListData.from_file(Path(__file__).parent.absolute() / "small_ex.txt")


@pytest.fixture(scope="session")
def input_txt() -> ListData:
    return ListData.from_file(Path(__file__).parent.absolute() / "input.txt")


def test_q1_ex(small_ex_txt):
    assert q1_distance(small_ex_txt) == 11


def test_q2_ex(small_ex_txt):
    assert q2_similarity(small_ex_txt) == 31


def test_q1(input_txt):
    assert q1_distance(input_txt) == 1879048


def test_q2(input_txt):
    assert q2_similarity(input_txt) == 21024792
