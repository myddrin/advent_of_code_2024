import dataclasses
import re
from argparse import ArgumentParser
from collections import defaultdict
from copy import copy
from pathlib import Path
from typing import Self, ClassVar


@dataclasses.dataclass(kw_only=True, frozen=True)
class Rule:
    first: int
    second: int

    def __repr__(self):
        return f"R({self.first}, {self.second})"


RuleMap = dict[int, list[Rule]]


@dataclasses.dataclass(kw_only=True, frozen=True)
class Updates:
    pages: list[int]
    was_reordered: bool

    @property
    def middle_page(self) -> int:
        if len(self.pages) % 2 == 1:
            return self.pages[len(self.pages) // 2]
        else:
            raise ValueError("Odd update")


@dataclasses.dataclass
class Node:
    """Node in a graph of page order"""

    page: int
    prev_nodes: set[Self] = dataclasses.field(default_factory=set)

    def __hash__(self):
        return hash(self.page)

    @classmethod
    def build_graph(cls, active_rules: RuleMap) -> dict[int, Self]:
        graph = {}

        unique_rules = set()
        for rules in active_rules.values():
            unique_rules.update(rules)

        for rule in unique_rules:
            if not (first_node := graph.get(rule.first)):
                first_node = Node(rule.first)
                graph[rule.first] = first_node
            if not (second_node := graph.get(rule.second)):
                second_node = Node(rule.second)
                graph[rule.second] = second_node

            second_node.prev_nodes.add(first_node)

        return graph

    @classmethod
    def generate_order(cls, pages: list[int], graph: dict[int, Self]) -> list[int]:
        pending = copy(graph)
        result = [p for p in pages if p not in pending]

        while pending:
            to_insert = []
            for node in pending.values():
                if not any((second.page in pending for second in node.prev_nodes)):
                    to_insert.append(node.page)
            if not to_insert:
                raise RuntimeError("Nothing to do")
            for page in to_insert:
                pending.pop(page)
                result.append(page)

        return result


class SetOfRules:
    pattern: ClassVar = re.compile(r"(\d+)\|(\d+)")

    def __init__(self):
        self.rules = []
        self.page_rules: dict[int, list[Rule]] = defaultdict(list)
        self.updates: list[Updates] = []
        self.active_rules: list[set[Rule]] = []

    def add_rule(self, line: str) -> bool:
        match = self.pattern.match(line)
        if not match:
            return False

        rule = Rule(first=int(match.group(1)), second=int(match.group(2)))
        self.rules.append(rule)
        self.page_rules[rule.first].append(rule)
        self.page_rules[rule.second].append(rule)
        return True

    def _find_rules(self, pages: list[int]) -> tuple[RuleMap, dict[int, int]]:
        update_idx: dict[int, int] = {page: i for i, page in enumerate(pages)}
        active_rules: dict[int, set[Rule]] = defaultdict(set)
        for page in update_idx.keys():
            for potential_rule in self.page_rules[page]:
                first = update_idx.get(potential_rule.first)
                second = update_idx.get(potential_rule.second)
                is_active = first is not None and second is not None
                if is_active:
                    active_rules[page].add(potential_rule)
        return {page: list(rules) for page, rules in active_rules.items()}, update_idx

    def _check_valid_update(self, active_rules: RuleMap, update_idx: dict[int, int]) -> bool:
        for page in update_idx.keys():
            for rule in active_rules[page]:
                if update_idx[rule.first] > update_idx[rule.second]:
                    return False

        return True

    def _graph_reorder_pages(self, pages: list[int], active_rules: RuleMap) -> list[int]:
        print(f"Graph attempt to reorder {pages=} using {active_rules}")
        graph = Node.build_graph(active_rules)
        result = Node.generate_order(pages, graph)
        if not self._check_valid_update(*self._find_rules(result)):
            raise RuntimeError("Generated invalid order!")
        return result

    def add_update(self, line: str) -> bool:
        if "," not in line:
            return False
        pages = [int(v) for v in line.split(",")]
        active_rules, update_idx = self._find_rules(pages)
        is_valid = self._check_valid_update(active_rules, update_idx)
        if not is_valid:
            pages = self._graph_reorder_pages(pages, active_rules)
        self.updates.append(Updates(pages=pages, was_reordered=not is_valid))
        return True

    @classmethod
    def from_file(cls, filename: Path | str) -> Self:
        obj = cls()

        print(f"Loading {filename}")
        with open(filename, "r") as fin:
            for line in fin:
                line = line.strip()
                if not line:
                    continue

                if not obj.add_rule(line):
                    obj.add_update(line)

        return obj


def q1_middle_page(data: SetOfRules) -> int:
    return sum((update.middle_page for update in data.updates if not update.was_reordered))


def q2_reordered_middle_page(data: SetOfRules) -> int:
    return sum((update.middle_page for update in data.updates if update.was_reordered))


def main(filename: str):
    data = SetOfRules.from_file(filename)
    q1 = q1_middle_page(data)
    print(f"Q1: {q1} middle page checksum")
    q2 = q2_reordered_middle_page(data)
    print(f"Q2: {q2} after reordered middle page checksum")


if __name__ == "__main__":
    fd = Path(__file__).parent.absolute() / "input.txt"
    parser = ArgumentParser()
    parser.add_argument("--input", type=str, default=str(fd), help="Input file")
    args = parser.parse_args()

    main(args.input)
