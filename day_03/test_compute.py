from pathlib import Path

import pytest

from day_03.compute import q1_lazy_mult, Mult, q2_active_mult


@pytest.fixture(scope="session")
def small_ex_txt() -> list[Mult]:
    return Mult.from_file(Path(__file__).parent.absolute() / "small_ex.txt")


@pytest.fixture(scope="session")
def small_ex_2_txt() -> list[Mult]:
    return Mult.from_file(Path(__file__).parent.absolute() / "small_ex_2.txt")


@pytest.fixture(scope="session")
def input_txt() -> list[Mult]:
    return Mult.from_file(Path(__file__).parent.absolute() / "input.txt")


def test_q1_small_ex(small_ex_txt):
    assert q1_lazy_mult(small_ex_txt) == 161


def test_q2_small_ex(small_ex_2_txt):
    assert q2_active_mult(small_ex_2_txt) == 48


def test_q1(input_txt):
    assert q1_lazy_mult(input_txt) == 169021493


def test_q2(input_txt):
    assert q2_active_mult(input_txt) == 111762583
