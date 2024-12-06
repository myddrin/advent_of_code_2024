from pathlib import Path

import pytest

from day_04.compute import Card, q1_find_xmas, q2_find_x_mas


@pytest.fixture(scope="session")
def small_ex_txt() -> Card:
    return Card.from_file(Path(__file__).parent.absolute() / "small_ex.txt")


@pytest.fixture(scope="session")
def input_txt() -> Card:
    return Card.from_file(Path(__file__).parent.absolute() / "input.txt")


def test_q1_small_ex(small_ex_txt):
    assert q1_find_xmas(small_ex_txt) == 18


def test_q2_small(small_ex_txt):
    assert q2_find_x_mas(small_ex_txt) == 9


def test_q1(input_txt):
    assert q1_find_xmas(input_txt) == 2414


def test_q2(input_txt):
    assert q2_find_x_mas(input_txt) == 1871
