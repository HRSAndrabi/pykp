"""
Provides an interface for defining arrangements of items.

Example:
    Define an arangement of items for the knapsack problem::

        from pykp import Arrangement, Item

        items = [
            Item(value=10, weight=5),
            Item(value=20, weight=10),
            Item(value=30, weight=15),
        ]
        state = [0, 1, 1]
        arrangement = Arrangement(items=items, state=state)
        print(arrangement)
"""

import numpy as np

from .item import Item


class Arrangement:
    """
    Represents an arrangement of items for the knapsack problem.

    Parameters:
        items (list[Item]): An array of items for the knapsack problem.
        state (list[int]): Binary array indicating the inclusion or
            exclusion of items in the arrangement.
        value (int): The total value of items in the arrangement.
        weight (int): The total weight of items in the arrangement.
    """

    def __init__(
        self,
        items: list[Item],
        state: list[int],
    ):
        if not np.all(np.isin(state, [0, 1])):
            raise ValueError("Elements of `state` must be 0 or 1.")

        if not isinstance(items, np.ndarray):
            items = np.array(items)

        if not isinstance(state, np.ndarray):
            state = np.array(state)

        self._items = items
        self._state = state
        self._value = self.__calculate_value()
        self._weight = self.__calculate_weight()

    @property
    def items(self) -> list[Item]:
        """The items in the arrangement."""
        return list(self._items)

    @property
    def state(self) -> list[int]:
        """
        The state of the arrangement. 1 indicates the item is in the
        arrangement, 0 indicates it is not.
        """
        return list(self._state)

    @property
    def value(self) -> float:
        """The total value of items in the arrangement."""
        return self._value

    @property
    def weight(self) -> float:
        """The total weight of items in the arrangement."""
        return self._weight

    def __calculate_value(self):
        """
        Calculates the total value of items currently in the knapsack.

        Returns:
            float: The total value of items in the knapsack.
        """
        return sum(
            [
                self._items[i].value
                for i, inside in enumerate(self._state)
                if bool(inside)
            ]
        )

    def __calculate_weight(self):
        """
        Calculates the total weight of items currently in the knapsack.

        Returns:
            float: The total weight of items in the knapsack.
        """
        return sum(
            [
                self._items[i].weight
                for i, inside in enumerate(self._state)
                if bool(inside)
            ]
        )

    def __hash__(self):
        return hash(tuple(self._state))

    def __eq__(self, other):
        return np.array_equal(self._state, other.state)

    def __str__(self):
        state = int("".join(self._state.astype(int).astype(str)), 2)
        return f"(v: {self._value}, w: {self._weight}, s: {state})"

    def __repr__(self):
        state = int("".join(self._state.astype(int).astype(str)), 2)
        return f"(v: {self._value}, w: {self._weight}, s: {state})"
