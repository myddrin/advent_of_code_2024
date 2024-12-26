from pathlib import Path

import pytest

from day_07.compute import Equation, DataSet, q1_brute, q2_brute


@pytest.fixture(scope="session")
def small_ex_txt() -> DataSet:
    return Equation.from_file(Path(__file__).parent.absolute() / "small_ex.txt")


@pytest.fixture(scope="session")
def input_txt() -> DataSet:
    return Equation.from_file(Path(__file__).parent.absolute() / "input.txt")


def test_q1_small(small_ex_txt):
    assert q1_brute(small_ex_txt) == 3749


def test_q2_small(small_ex_txt):
    assert q2_brute(small_ex_txt, verbose=False) == 11387


def test_q1_input(input_txt):
    assert q1_brute(input_txt) == 3312271365652


@pytest.mark.slow
def test_q2_input(input_txt):
    assert q2_brute(input_txt, verbose=False) == 509463489296712
