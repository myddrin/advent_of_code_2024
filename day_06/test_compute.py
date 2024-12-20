from pathlib import Path

import pytest

from day_06.compute import Map


@pytest.fixture(scope="session")
def small_ex_txt() -> Map:
    return Map.from_file(Path(__file__).parent.absolute() / "small_ex.txt")


@pytest.fixture(scope="session")
def input_txt() -> Map:
    return Map.from_file(Path(__file__).parent.absolute() / "input.txt")


def test_q1_small(small_ex_txt):
    visited = small_ex_txt.predict_guard()
    assert len(visited) == 41


def test_q2_small(small_ex_txt):
    visited = small_ex_txt.predict_guard()
    assert small_ex_txt.brute_force_obstructions(visited) == 6


def test_q1_input(input_txt):
    assert len(input_txt.predict_guard()) == 4973


@pytest.mark.slow
def test_q2_input(input_txt):
    visited = input_txt.predict_guard()
    assert input_txt.brute_force_obstructions(visited) == 1482
