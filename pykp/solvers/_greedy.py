import time

import numpy as np

from pykp.knapsack._arrangement import Arrangement
from pykp.knapsack._item import Item

from ._solution import *


def greedy(items: list[Item], capacity: int) -> Solution:
    """Appy the greedy algorithm to a knapsack problem instance.

    The greedy algorithm selects the best item at each step based on the
    value-to-weight ratio, until no more items can be added to the knapsack.

    Parameters
    ----------
    items : np.ndarray[Item]
        Array of items to consider for the knapsack.
    capacity : int
        Maximum weight capacity of the knapsack.

    Returns
    -------
    Solution : Solution
        The greedy arrangement of items in the knapsack.

    Examples
    --------
    Solve a knapsack problem using the greedy algorithm:

    >>> from pykp import Item
    >>> from pykp import solvers
    >>> items = np.array(
    ...     [
    ...         Item(value=100, weight=50),
    ...         Item(value=200, weight=100),
    ...         Item(value=400, weight=300),
    ...     ]
    ... )
    >>> capacity = 300
    >>> solvers.greedy(items, capacity)
    (v: 300, w: 150, s: 6)

    .. note::
        The greedy algorithm is not guaranteed to find the optimal solution
        to the knapsack problem. It is a heuristic algorithm that selects
        the best item at each step based on the value-to-weight ratio,
        until no more items can be added to the knapsack.
    """
    time_start = time.perf_counter()
    items = np.array(items)
    state = np.zeros(len(items))
    weight = 0
    balance = capacity
    while balance > 0:
        remaining_items = [
            items[i]
            for i, element in enumerate(state)
            if element == 0 and items[i].weight + weight <= capacity
        ]
        if len(remaining_items) == 0:
            break
        best_item = max(
            remaining_items, key=lambda item: item.value / item.weight
        )
        state[items.tolist().index(best_item)] = 1
        balance -= best_item.weight
        weight += best_item.weight

    time_end = time.perf_counter()
    statistics = SolutionStatistics(time=time_end - time_start, n_solutions=1)
    return Solution(
        value=Arrangement(items=items, state=state),
        type=SolutionType.APPROXIMATE,
        statistics=statistics,
    )
