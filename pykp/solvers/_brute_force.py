import itertools
import operator
import time

import numpy as np

from pykp.knapsack._arrangement import Arrangement
from pykp.knapsack._item import Item

from ._solution import *


def _is_subset_feasible(subset: list[Item], capacity) -> bool:
    """Determine whether subset of items is feasible.

    A subset of items is considered feasible if the total weight of the
    items is less than or equal to the capacity of the knapsack.

    Parameters
    ----------
    subset : list[Item]
        Subset of items.
    capacity : int
        Capacity of the knapsack.

    Returns
    -------
    bool
        Whether the node is feasible.
    """
    weight = sum([i.weight for i in subset])
    balance = capacity - weight
    if balance < 0:
        return False
    return True


def _is_subset_terminal(
    subset: list[Item], items: list[Item], capacity
) -> bool:
    """Determine whether subset of items is terminal.

    A subset of items is considered terminal if the total weight of the
    items is less than or equal to the capacity of the knapsack and no
    remaining items can be added to the knapsack without exceeding the
    capacity.

    Parameters
    ----------
    subset : list[Item]
        Subset of items.
    items : list[Item]
        All items in the knapsack.
    capacity : int
        Capacity of the knapsack.

    Returns
    -------
    bool
        Whether the node is terminal
    """
    weight = sum([i.weight for i in subset])
    balance = capacity - weight
    if balance < 0:
        return False
    remaining_items = set(items) - set(subset)
    for i in remaining_items:
        if i.weight <= balance:
            return False
    return True


def brute_force(items: list[Item], capacity: int) -> Solution:
    """Solves the knapsack problem using brute force.

    Parameters
    ----------
    items : list[Item]
        List of items to consider for the knapsack.
    capacity : int
        Maximum weight capacity of the knapsack.

    Returns
    -------
    Solution
        ``Solution.value`` is a dictionary that provides various subsets
        of nodes in the graph representation of the provided knapsack instance.
        These subsets are: "optimal_nodes", "terminal_nodes", "feasible_nodes",
        and "all".

    Examples
    --------
    To solve a knapsack problem instance using the brute-force
    algorithm, first create a list of items and then call the solver
    with the items and capacity.

    >>> from pykp import Item, solvers
    >>>
    >>> items = [
    ...     Item(value=10, weight=5),
    ...     Item(value=15, weight=10),
    ...     Item(value=5, weight=5),
    ... ]
    >>> capacity = 15
    >>> solution = solvers.brute_force(items, capacity)
    >>> print(solution["optimal"])
    [(v: 25, w: 15, s: 6)]

    Alternatively, construct an instance of the `Knapsack` class and
    call the `initialise_graph()` method.

    >>> from pykp import Item, Knapsack
    >>>
    >>> items = [
    ...     Item(value=10, weight=5),
    ...     Item(value=15, weight=10),
    ...     Item(value=5, weight=5),
    ... ]
    >>> capacity = 15
    >>> instance = Knapsack(items=items, capacity=capacity)
    >>>
    >>> instance.initialise_graph()
    >>> instace.optimal_nodes
    [(v: 25, w: 15, s: 6)]
    >>> instance.terminal_nodes
    [(v: 25, w: 15, s: 6), (v: 20, w: 15, s: 3), (v: 15, w: 10, s: 5)]
    >>> instance.feasible_nodes
    [(v: 0, w: 0, s: 0),
    (v: 5, w: 5, s: 1),
    (v: 10, w: 5, s: 4),
    (v: 15, w: 10, s: 2),
    (v: 15, w: 10, s: 5),
    (v: 20, w: 15, s: 3),
    (v: 25, w: 15, s: 6)]
    >>> instance.nodes
    [(v: 10, w: 5, s: 4),
    (v: 15, w: 10, s: 2),
    (v: 5, w: 5, s: 1),
    (v: 25, w: 15, s: 6),
    (v: 15, w: 10, s: 5),
    (v: 20, w: 15, s: 3),
    (v: 30, w: 20, s: 7),
    (v: 0, w: 0, s: 0)]

    .. note::
        The brute-force algorithm is computationally expensive and should be
        used with caution for large problem instances.
    """
    time_start = time.perf_counter()

    nodes = np.array([])
    feasible_nodes = np.array([])
    terminal_nodes = np.array([])
    optimal_nodes = np.array([])

    for i in range(1, len(items) + 1):
        subsets = list(itertools.combinations(items, i))
        for subset in subsets:
            nodes = np.append(
                nodes,
                Arrangement(
                    items=items,
                    state=np.array([int(item in subset) for item in items]),
                ),
            )
            if _is_subset_feasible(subset, capacity):
                feasible_nodes = np.append(
                    feasible_nodes,
                    Arrangement(
                        items=items,
                        state=np.array(
                            [int(item in subset) for item in items]
                        ),
                    ),
                )
            if _is_subset_terminal(subset, items, capacity):
                terminal_nodes = np.append(
                    terminal_nodes,
                    Arrangement(
                        items=items,
                        state=np.array(
                            [int(item in subset) for item in items]
                        ),
                    ),
                )
    nodes = np.append(
        nodes,
        Arrangement(items=items, state=np.zeros(len(items), dtype=int)),
    )
    feasible_nodes = np.append(
        feasible_nodes,
        Arrangement(items=items, state=np.zeros(len(items), dtype=int)),
    )
    feasible_nodes = sorted(
        feasible_nodes,
        key=operator.attrgetter("value"),
    )
    terminal_nodes = sorted(
        terminal_nodes, key=operator.attrgetter("value"), reverse=True
    )
    optimal_nodes = np.array(
        [
            arrangement
            for arrangement in terminal_nodes
            if arrangement.value == terminal_nodes[0].value
        ]
    )
    time_end = time.perf_counter()
    value = {
        "optimal": optimal_nodes,
        "terminal": terminal_nodes,
        "feasible": feasible_nodes,
        "all": nodes,
    }
    statistics = SolutionStatistics(
        time=time_end - time_start, n_solutions=len(nodes)
    )
    return Solution(
        value=value, type=SolutionType.TRAVERSAL, statistics=statistics
    )
