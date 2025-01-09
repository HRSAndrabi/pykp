import pathlib

import numpy as np
import pytest

from pykp import Item, Knapsack


@pytest.fixture
def knapsack() -> Knapsack:
    items = [
        Item(value=7, weight=3),
        Item(value=10, weight=5),
        Item(value=15, weight=10),
        Item(value=10, weight=10),
    ]
    capacity = 23
    return Knapsack(items=items, capacity=capacity)


def test_initialisation(knapsack: Knapsack):
    assert knapsack.capacity == 23
    assert np.array_equal(knapsack.state, np.zeros(len(knapsack.items)))
    assert knapsack.value == 0
    assert knapsack.weight == 0
    assert knapsack.is_feasible


def test_invalid_initialisation():
    with pytest.raises(ValueError):
        Knapsack(items=np.array([]), capacity=10)

    with pytest.raises(ValueError):
        Knapsack(items="not an array", capacity=10)

    with pytest.raises(ValueError):
        Knapsack(items=np.array([1, 2, 3]), capacity=-5)


def test_add_item(knapsack: Knapsack):
    knapsack.empty()
    knapsack.add(knapsack.items[0])
    assert knapsack.value == 7
    assert knapsack.weight == 3
    assert knapsack.is_feasible
    assert np.array_equal(knapsack.state, [1, 0, 0, 0])


def test_remove_item(knapsack: Knapsack):
    knapsack.empty()
    knapsack.add(knapsack.items[0])
    knapsack.remove(knapsack.items[0])
    assert knapsack.value == 0
    assert knapsack.weight == 0
    assert np.array_equal(knapsack.state, [0, 0, 0, 0])


def test_set_state(knapsack: Knapsack):
    knapsack.set_state([1, 0, 1, 0])
    print(knapsack.items)
    assert knapsack.value == 22
    assert knapsack.weight == 13
    assert knapsack.is_feasible
    assert np.array_equal(knapsack.state, [1, 0, 1, 0])


def test_empty(knapsack: Knapsack):
    knapsack.set_state([1, 0, 1, 0])
    knapsack.empty()
    assert knapsack.value == 0
    assert knapsack.weight == 0
    assert np.array_equal(knapsack.state, [0, 0, 0, 0])


def test_load_from_json(tmp_path: pathlib.Path, knapsack: Knapsack):
    path = tmp_path / "test_knapsack.json"
    knapsack.write_to_json(str(path))
    new_knapsack = Knapsack(
        items=np.array([]), capacity=0, load_from_json=True, path_to_spec=path
    )
    assert new_knapsack.capacity == knapsack.capacity
    assert len(new_knapsack.items) == len(knapsack.items)
