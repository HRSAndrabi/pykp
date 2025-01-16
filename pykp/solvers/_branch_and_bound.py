import time
from dataclasses import dataclass, field
from queue import PriorityQueue

import numpy as np

from pykp.knapsack._arrangement import Arrangement
from pykp.knapsack._item import Item

from ._solution import *


@dataclass(order=True, frozen=True)
class Node:
    """Represents a node in the branch-and-bound tree.

    Parameters
    ----------
    priority : float
        The priority of the node.
    upper_bound : float
        The upper bound of the node.
    items : np.ndarray[Item]
        Items that can be included in the knapsack.
    value : int
        The total value of items in the node.
    weight : int
        The total weight of items in the node.
    included_items : np.ndarray[Item]
        Items included by this node.
    excluded_items : np.ndarray[Item]
        Items excluded by this node.
    """

    priority: float = field(compare=True)
    upper_bound: float = field(compare=False)
    items: np.ndarray[Item] = field(compare=False)
    value: int = field(compare=False)
    weight: int = field(compare=False)
    included_items: np.ndarray[Item] = field(compare=False)
    excluded_items: np.ndarray[Item] = field(compare=False)


def _calculate_upper_bound(
    items: np.ndarray[Item],
    capacity: int,
    included_items: np.ndarray[Item],
    excluded_items: np.ndarray[Item],
) -> float:
    """Calculate the upper bound of the supplied branch.

    The upper bound is calculated by filling the fractional knapsack with
    items in descending order of value-to-weight ratio.

    Parameters
    ----------
    items: np.ndarray[Item]
        Items that can be included in the knapsack.
    capacity: int
        Maximum weight capacity of the knapsack.
    included_items: np.ndarray[Item]
        Items included by all nodes within the branch.
    excluded_items: np.ndarray[Item]
        Items excluded by all nodes within the branch.

    Returns
    -------
    float
        Upper bound of the branch.
    """
    arrangement = Arrangement(
        items=items,
        state=np.array([int(item in included_items) for item in items]),
    )
    candidate_items = np.array(
        sorted(
            set(items) - set(included_items) - set(excluded_items),
            key=lambda item: item.value / item.weight,
            reverse=True,
        )
    )
    balance = capacity - arrangement.weight

    if balance < 0:
        return -1

    if len(candidate_items) == 0 or balance == 0:
        return arrangement.value

    i = 0
    upper_bound = arrangement.value
    while balance > 0 and i < len(candidate_items):
        item = candidate_items[i]
        added_weight = min(balance, item.weight)
        upper_bound = upper_bound + added_weight * item.value / item.weight
        balance = balance - added_weight
        i += 1
    return upper_bound


def _expand_node(
    node: Node,
    capacity: int,
    incumbent: float,
) -> np.ndarray:
    """Expand a node in the branch-and-bound tree.

    The node is expanded by generating two children nodes: one that includes
    the next item in the knapsack and one that excludes it. The children are
    only returned if the upper bound of the child is greater than or equal to
    the incumbent value.

    Parameters
    ----------
    node: Node
        Node to expand.
    capacity: int
        Maximum weight capacity of the knapsack.
    incumbent: float
        The best value found so far.

    Returns
    -------
    np.ndarray
        The child nodes of the expanded node.
    """
    arrangement = Arrangement(
        items=node.items,
        state=np.array(
            [int(item in node.included_items) for item in node.items]
        ),
    )
    if arrangement.weight > capacity:
        return []

    if len(node.included_items) + len(node.excluded_items) >= len(node.items):
        return []  # No further branching possible

    next_item = node.items[len(node.included_items) + len(node.excluded_items)]

    # Generate children (left-branch includes item, right-branch excludes item)
    # only return them if we do not prune by upper_bound.
    children = []

    for included in [True, False]:
        included_items = (
            np.append(node.included_items, next_item)
            if included
            else node.included_items
        )
        excluded_items = (
            np.append(node.excluded_items, next_item)
            if not included
            else node.excluded_items
        )
        upper_bound = _calculate_upper_bound(
            items=node.items,
            capacity=capacity,
            included_items=included_items,
            excluded_items=excluded_items,
        )
        child = Node(
            priority=-upper_bound,
            items=node.items,
            value=node.value + next_item.value * included,
            weight=node.weight + next_item.weight * included,
            included_items=included_items,
            excluded_items=excluded_items,
            upper_bound=upper_bound,
        )
        if child.upper_bound >= incumbent:
            children.append(child)

    return children


def _is_leaf_node(node: Node, capacity: int) -> bool:
    """Whether a provided node is a leaf node.

    A node is considered a leaf node if the balance is under capacity,
    and all items in the branch have been either included or excluded.

    Parameters
    ----------
    node: Node
        Node to check.
    capacity: int
        Maximum weight capacity of the knapsack.

    Returns
    -------
    bool
        Wheter the node is a leaf node.
    """
    weight = sum([i.weight for i in node.included_items])
    balance = capacity - weight
    if balance < 0:
        return False
    remaining_items = (
        set(node.items) - set(node.included_items) - set(node.excluded_items)
    )
    return len(remaining_items) == 0


def branch_and_bound(
    items: list[Item],
    capacity: float,
    n=1,
) -> Solution:
    """Solves the knapsack problem using the branch-and-bound algorithm.

    Parameters
    ----------
    items: list[Item]
        Items that can be included in the knapsack.
    capacity: float
        Maximum weight capacity of the knapsack.

    Other Parameters
    ----------------
    n: int, optional
        The n-best solutions to return. If set to 1, the solver returns all
        solutions that achieve the distinct optimal value. If set to n, the
        solver returns the solutions that achieve the n-highest possible
        values. Defaults to 1.

    Returns
    -------
    Solution : Solution
        If ``n = 1``, the optimal arrangements of items in the
        knapsack. If ``n > 1``, all arrangements that yield the ``n`` highest
        possible values in the knapsack.

    Examples
    --------
    Solve a knapsack problem using the branch-and-bound algorithm

    >>> from pykp import Item
    >>> from pykp import solvers
    >>>
    >>> items = [
    ...     Item(value=10, weight=5),
    ...     Item(value=15, weight=10),
    ...     Item(value=5, weight=5),
    >>> ]
    >>> capacity = 15
    >>> solvers.branch_and_bound(items, capacity)
    [(v: 25, w: 15, s: 6)]

    Alternatively, construct an instance of the ``Knapsack`` class and call the
    ``solve`` method with "branch_and_bound" as the ``method`` argument

    >>> from pykp import Item
    >>> from pykp import Knapsack
    >>>
    >>> items = [
    ...     Item(value=10, weight=5),
    ...     Item(value=15, weight=10),
    ...     Item(value=5, weight=5),
    ... ]
    >>> capacity = 15
    >>> instance = Knapsack(items=items, capacity=capacity)
    >>> instance.solve(method="branch_and_bound")
    >>> instance.optimal_nodes
    [(v: 25, w: 15, s: 6)]

    If there are multiple solutions with the same optimal value, all will be
    returned.

    >>> from pykp import Item
    >>> from pykp import Knapsack
    >>>
    >>> items = [
    ...     Item(value=10, weight=5),
    ...     Item(value=15, weight=10),
    ...     Item(value=4, weight=2),
    ...     Item(value=6, weight=3),
    ... ]
    >>> capacity = 15
    >>> instance = Knapsack(items=items, capacity=capacity)
    >>> instance.solve(method="branch_and_bound")
    >>> instance.optimal_nodes
    [(v: 25, w: 15, s: 9), (v: 25, w: 15, s: 7)]

    Use the optional ``n`` argument to return the n-best solutions found by
    the solver.

    >>> from pykp import Item
    >>> from pykp import Knapsack
    >>> from pykp import solvers
    >>>
    >>> items = [
    ...     Item(value=10, weight=5),
    ...     Item(value=15, weight=10),
    ...     Item(value=4, weight=2),
    ...     Item(value=6, weight=3),
    ... ]
    >>> capacity = 15
    >>> solvers.branch_and_bound(items, capacity, n=3)
    [(v: 25, w: 15, s: 9), (v: 25, w: 15, s: 7), (v: 21, w: 13, s: 3)]

    .. note::
        The ``n`` argument is on solution values, not the number of
        solutions. If ``n`` is set to 1, the solver returns all solutions
        that achieve the distinct optimal value. More than one solution
        may be returned if there are multiple solutions with the same
        optimal value. Similarly, if ``n`` is set to `n`, the solver returns
        all solutions that achieve the `n`-highest possible values.
    """
    time_start = time.perf_counter()

    if n == 1:
        type = SolutionType.MAXIMISE
    else:
        type = SolutionType.MAXIMISE_TOP_N

    if len(items) == 0:
        statistcs = SolutionStatistics(time=0, n_solutions=0)
        return Solution(
            value=[Arrangement(items=items, state=np.array([]))],
            type=type,
            statistics=statistcs,
        )

    items = np.array(
        sorted(items, key=lambda item: item.value / item.weight, reverse=True)
    )
    upper_bound = _calculate_upper_bound(
        items=items,
        capacity=capacity,
        included_items=np.array([]),
        excluded_items=np.array([]),
    )
    root = Node(
        priority=-sum([item.value for item in items]),
        items=items,
        value=0,
        weight=0,
        included_items=np.array([]),
        excluded_items=np.array([]),
        upper_bound=upper_bound,
    )
    queue = PriorityQueue()
    queue.put(root)
    incumbent = 0
    nodes = []
    n_best_values = [0]

    while not queue.empty():
        next = queue.get()
        children = _expand_node(next, capacity, incumbent)
        for child in children:
            if child.upper_bound < incumbent:
                continue

            queue.put(child)
            if child.value >= incumbent and _is_leaf_node(child, capacity):
                n_best_values.append(child.value)
                n_best_values = sorted(n_best_values, reverse=True)[:n]
                incumbent = n_best_values[-1]
                nodes.append(child)

    nodes = [node for node in nodes if node.value >= incumbent]
    result = [
        Arrangement(
            items=items,
            state=np.array(
                [int(item in node.included_items) for item in items]
            ),
        )
        for node in nodes
    ]
    time_end = time.perf_counter()

    statistics = SolutionStatistics(
        time=time_end - time_start,
        n_solutions=len(result),
    )

    return Solution(value=result, type=type, statistics=statistics)


def _branch_and_bound_decision_variant(
    items: list[Item], capacity: float, target: float
) -> Solution:
    """Solves the knapsack decision variant using branch-and-bound.

    Parameters
    ----------
    items : list[Item]
        Items that can be included in the knapsack.
    capacity : int
        Maximum weight capacity of the knapsack.
    target : float
        The target value to achieve.

    Returns
    -------
    Solution
        Whether the target value can be achieved.
    """
    time_start = time.perf_counter()

    if len(items) == 0:
        return False

    items = np.array(
        sorted(items, key=lambda item: item.value / item.weight, reverse=True)
    )
    upper_bound = _calculate_upper_bound(
        items=items,
        capacity=capacity,
        included_items=np.array([]),
        excluded_items=np.array([]),
    )
    root = Node(
        priority=-sum([item.value for item in items]),
        items=items,
        value=0,
        weight=0,
        included_items=np.array([]),
        excluded_items=np.array([]),
        upper_bound=upper_bound,
    )
    queue = PriorityQueue()
    queue.put(root)

    while not queue.empty():
        next = queue.get()
        children = _expand_node(next, capacity, target)
        for child in children:
            queue.put(child)
            if child.value >= target:
                time_end = time.perf_counter()
                return Solution(
                    value=True,
                    type=SolutionType.SATISFY,
                    statistics=SolutionStatistics(
                        time=time_end - time_start,
                        n_solutions=1,
                    ),
                )

    time_end = time.perf_counter()
    return Solution(
        value=False,
        type=SolutionType.SATISFY,
        statistics=SolutionStatistics(
            time=time_end - time_start,
            n_solutions=0,
        ),
    )
