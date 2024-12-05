from pathlib import Path

import pytest

from day_03.compute import q1_lazy_mult, Mult


@pytest.fixture(scope="session")
def small_ex_txt() -> Path:
    return Path(__file__).parent.absolute() / "small_ex.txt"


@pytest.fixture(scope="session")
def input_txt():
    return Path(__file__).parent.absolute() / "input.txt"


def test_q1_small_ex(small_ex_txt):
    assert q1_lazy_mult(Mult.from_file(small_ex_txt)) == 161


def test_q1(input_txt):
    assert q1_lazy_mult(Mult.from_file(input_txt)) == 169021493
