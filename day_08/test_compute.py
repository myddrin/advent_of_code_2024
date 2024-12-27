from pathlib import Path

import pytest

from day_08.compute import Data, Position


@pytest.fixture(scope="session")
def small_ex_txt() -> Data:
    return Data.from_file(Path(__file__).parent.absolute() / "small_ex.txt")


@pytest.fixture(scope="session")
def input_txt() -> Data:
    return Data.from_file(Path(__file__).parent.absolute() / "input.txt")


class TestData:
    def test_populate_antinode_single_pair(self):
        obj = Data(10, 10, {"a": [Position(4, 3), Position(5, 5)]})
        expected = {
            Position(3, 1): ["a"],
            Position(6, 7): ["a"],
        }
        assert obj.populate_antinodes() == len(expected)
        assert obj.antinodes_map == expected

    def test_populate_antinode_double_pair(self):
        obj = Data(10, 10, {"a": [Position(4, 3), Position(5, 5), Position(8, 4)]})
        expected = {
            Position(0, 2): ["a"],
            Position(2, 6): ["a"],
            Position(3, 1): ["a"],
            Position(6, 7): ["a"],
        }
        assert obj.populate_antinodes() == len(expected)
        assert obj.antinodes_map == expected

    def test_populate_antinode_multi_pairs(self):
        obj = Data(
            12, 12, {"0": [Position(8, 1), Position(5, 2), Position(7, 3)], "A": [Position(6, 5), Position(8, 8)]}
        )
        expected = {
            Position(3, 1): ["0"],
            Position(2, 3): ["0"],
            Position(6, 5): ["0"],
            Position(9, 4): ["0"],
            Position(11, 0): ["0"],
            Position(4, 2): ["A"],
            Position(10, 11): ["A"],
        }
        assert obj.populate_antinodes() == len(expected)
        assert obj.antinodes_map == expected


def test_q1_small(small_ex_txt):
    found = small_ex_txt.populate_antinodes()
    assert found == 14


def test_q1(input_txt):
    found = input_txt.populate_antinodes()
    assert found < 303
