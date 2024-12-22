from pathlib import Path

import pytest

from day_05.compute import SetOfRules, q1_middle_page, q2_reordered_middle_page


@pytest.fixture(scope="session")
def small_ex_txt() -> SetOfRules:
    return SetOfRules.from_file(Path(__file__).parent.absolute() / "small_ex.txt")


@pytest.fixture(scope="session")
def input_txt() -> SetOfRules:
    return SetOfRules.from_file(Path(__file__).parent.absolute() / "input.txt")


def test_q1_small_ex(small_ex_txt):
    assert q1_middle_page(small_ex_txt) == 143


def test_q2_small_ex(small_ex_txt):
    assert q2_reordered_middle_page(small_ex_txt) == 123


def test_q1(input_txt):
    assert q1_middle_page(input_txt) == 6612


def test_q2(input_txt):
    assert q2_reordered_middle_page(input_txt) == 4944
