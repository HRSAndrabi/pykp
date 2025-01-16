"""Interface for defining items inside a knapsack problem.

The :class:`Item` class is used to define items for the knapsack problem. Each
item has a value and a weight associated with it.

Example:
    Use the Item class to define items for the knapsack problem::

        from pykp import Item

        items = [
            Item(value=10, weight=5),
            Item(value=20, weight=10),
            Item(value=30, weight=15),
        ]

"""

from dataclasses import dataclass, field


@dataclass(frozen=True, eq=False)
class Item:
    """
    Represents an item for the knapsack problem.

    Parameters
    ----------
    value: int
        The value of the item.
    weight: int
        The weight of the item.

    Attributes
    ----------
    value: int
        The value of the item.
    weight: int
        The weight of the item.
    """

    value: int = field(compare=False)
    weight: int = field(compare=False)
