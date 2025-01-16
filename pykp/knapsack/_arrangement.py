import numpy as np

from pykp.knapsack._item import Item


class Arrangement:
    """Represents an arrangement of items for the knapsack problem.

    Used to store the state of items in the knapsack, as well as the total
    value and weight of items in the arrangement. The state is represented
    as a binary array, where 1 indicates the item is in the arrangement, and
    0 indicates it is not.


    Parameters
    ----------
    items: list[Item]
        An array of items for the knapsack problem.
    state: list[int]
        Binary array indicating the inclusion or exclusion of items in the
        arrangement.
    value: int
        The total value of items in the arrangement.
    weight int:
        The total weight of items in the arrangement.

    Attributes
    ----------
    items: list[Item]
        The items in the arrangement.
    state: list[int]
        The state of the arrangement.
    value: float
        The total value of items in the arrangement.
    weight: float
        The total weight of items in the arrangement.
    """

    def __init__(
        self,
        items: list[Item],
        state: list[int],
    ):
        if not np.all(np.isin(state, [0, 1])):
            raise ValueError("Elements of `state` must be 0 or 1.")

        if isinstance(items, list):
            items = np.array(items)

        if isinstance(state, list):
            state = np.array(state)

        self._items = items
        self._state = state
        self._value = self.__calculate_value()
        self._weight = self.__calculate_weight()

    @property
    def items(self) -> list[Item]:
        return list(self._items)

    @property
    def state(self) -> list[int]:
        return list(self._state)

    @property
    def value(self) -> float:
        return self._value

    @property
    def weight(self) -> float:
        return self._weight

    def __calculate_value(self):
        """Calculate total value of items currently in the knapsack.

        Returns
        -------
        float
            The total value of items in the knapsack.
        """
        return sum(
            [
                self._items[i].value
                for i, inside in enumerate(self._state)
                if bool(inside)
            ]
        )

    def __calculate_weight(self):
        """Calculate the total weight of items currently in the knapsack.

        Returns
        -------
        float
            The total weight of items in the knapsack.
        """
        return sum(
            [
                self._items[i].weight
                for i, inside in enumerate(self._state)
                if bool(inside)
            ]
        )

    def __hash__(self):
        """Hash the state of the arrangement."""
        return hash(tuple(self._state))

    def __eq__(self, other):
        """Check if two arrangements are equal."""
        return np.array_equal(self._state, other.state)

    def __str__(self):
        """Return a string representation of the arrangement."""
        state = int("".join(self._state.astype(int).astype(str)), 2)
        return f"(v: {self._value}, w: {self._weight}, s: {state})"

    def __repr__(self):
        """Return a string representation of the arrangement."""
        state = int("".join(self._state.astype(int).astype(str)), 2)
        return f"(v: {self._value}, w: {self._weight}, s: {state})"
