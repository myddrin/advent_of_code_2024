from pathlib import Path

import pytest

from day_02.compute import q1_count_safe, Report, q2_remove_safe


@pytest.fixture(scope="session")
def small_ex_txt() -> list[Report]:
    return Report.from_file(Path(__file__).parent.absolute() / "small_ex.txt")


@pytest.fixture(scope="session")
def input_txt() -> list[Report]:
    return Report.from_file(Path(__file__).parent.absolute() / "input.txt")


def test_q1_ex(small_ex_txt):
    assert q1_count_safe(small_ex_txt) == 2


def test_q2_ex(small_ex_txt):
    assert q2_remove_safe(small_ex_txt) == 4


def test_q1(input_txt):
    assert q1_count_safe(input_txt) == 526


def test_q2(input_txt):
    assert q2_remove_safe(input_txt) == 566
