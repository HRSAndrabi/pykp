"""Implementations of various solvers for the knapsack problem."""

"""
Provides an implementation of branch and bound algorithm for
solving the knapsack problem.

Example:
    To solve a knapsack problem instance using the branch-and-bound algorithm,
    first create a list of items and then call the solver with the items and
    capacity::

        from pykp import Item, Solvers

        items = [
            Item(value=10, weight=5),
            Item(value=15, weight=10),
            Item(value=7, weight=3),
        ]
        capacity = 15
        optimal_nodes = solvers.branch_and_bound(items, capacity)
        print(optimal_nodes)

    Alternatively, construct an instance of the `Knapsack` class and call the
    `solve` method with "branch_and_bound" as the `method` argument::

        from pykp import Item, Knapsack

        items = [
            Item(value=10, weight=5),
            Item(value=15, weight=10),
            Item(value=7, weight=3),
        ]
        capacity = 15
        instance = Knapsack(items=items, capacity=capacity)
        optimal_nodes = instance.solve(method="branch_and_bound")
        print(optimal_nodes)
"""

import itertools
import operator
import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from queue import PriorityQueue
from typing import Literal, Tuple

import nest_asyncio
import numpy as np
from minizinc import Instance, Model, Solver

from .arrangement import Arrangement
from .item import Item


class SolutionType(Enum):
    """Types of solutions that can be returned by a solver."""

    MAXIMISE = "maximise"
    APPROXIMATE = "approximate"
    SATISFY = "satisfy"
    MAXIMISE_TOP_N = "maximise_top_n"
    TRAVERSAL = "traversal"


@dataclass(frozen=True)
class SolutionStatistics:
    """Statistics about the solution returned by a solver.

    Parameters
    ----------
    time : float
        Time taken by the solver to find the solution.
    n_solutions : int
        Number of solutions found by the solver.
    """

    time: float
    n_solutions: int


@dataclass(frozen=True)
class Solution:
    """Represents a solution returned by a solver.

    Parameters
    ----------
    value: bool | Arrangement | list[Arrangement]
        The arrangement of items in the solution.
    type: SolutionType
        The type of the solution.
    statistics: SolutionStatistics
        Statistics about the algorithm to obtain the solution.
    """

    value: bool | Arrangement | list[Arrangement]
    type: Literal[
        SolutionType.MAXIMISE,
        SolutionType.MAXIMISE_TOP_N,
        SolutionType.APPROXIMATE,
        SolutionType.SATISFY,
        SolutionType.TRAVERSAL,
    ]
    statistics: SolutionStatistics


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
    Solution
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


def minizinc(
    items: list[Item], capacity: float, solver: str = "coinbc"
) -> Solution:
    """Solves the knapsack problem using the MiniZinc.

    Parameters
    ----------
    items : list[Item]
        Array of items to consider for the knapsack.
    capacity : float
        Maximum weight capacity of the knapsack.
    solver: str, optional
        MiniZinc solver to use. Default is "coinbc".

    Returns
    -------
    Solution
        The optimal arrangement of items in the knapsack.

    Examples
    --------
    Solve a knapsack problem instance using MiniZinc and the COIN-OR
    Branch-and-Cut solver:

    >>> from pykp import Item, solvers
    >>> items = np.array(
    ...     [
    ...         Item(value=10, weight=5),
    ...         Item(value=15, weight=10),
    ...         Item(value=5, weight=5),
    ...     ]
    ... )
    >>> capacity = 15
    >>> solvers.minizinc(items, capacity, solver="coinbc")
    [(v: 25, w: 15, s: 6)]

    Alternatively, construct an instance of the ``Knapsack`` class and call the
    ``solve`` method with "minizinc" as the ``method`` argument

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
    >>> instance.solve(method="minizinc")
    >>> instance.optimal_nodes
    [(v: 25, w: 15, s: 6)]

    .. note::
        You should have MiniZinc 2.5.0 (or higher) installed on your system to
        use this solver. Refer to the `MiniZinc documentation
        <https://docs.minizinc.dev/en/stable/installation.html>`_
        for installation instructions.

    .. note::
        The MiniZinc Gecode solver is not robust to multiple solutions, and
        will report only the first optimal solution found. If knowing all
        optimal solutions is important, consider using the branch-and-bound
        solver.
    """
    nest_asyncio.apply()
    model = Model()
    model.add_string(
        """
		int: n; % number of objects
		set of int: OBJ = 1..n;
		float: capacity;
		array[OBJ] of float: profit;
		array[OBJ] of float: size;

		%var set of OBJ: x;
		array[OBJ] of var 0..1: x;
		var float: P=sum(i in OBJ)(profit[i]*x[i]);

		constraint sum(i in OBJ)(size[i]*x[i]) <= capacity;

		solve :: int_search(x, first_fail, indomain_max, complete) maximize P;
		"""
    )
    solver_instance = Solver.lookup(solver)

    instance = Instance(solver_instance, model)
    instance["n"] = len(items)
    instance["capacity"] = capacity
    instance["profit"] = [item.value for item in items]
    instance["size"] = [item.weight for item in items]

    result = instance.solve()
    statistics = SolutionStatistics(
        time=result.statistics["solveTime"], n_solutions=1
    )

    return Solution(
        value=Arrangement(items=items, state=np.array(result["x"])),
        type=SolutionType.MAXIMISE,
        statistics=statistics,
    )


def _minizinc_decision_variant(
    items: list[Item], capacity: float, target: float, solver: str = "coinbc"
) -> Solution:
    """Solves the knapsack decision variant using MiniZinc and Gecode.

    Parameters
    ----------
    items : list[Item]
        Array of items to consider for the knapsack.
    capacity : float
        Maximum weight capacity of the knapsack.
    target : float
        The target value to achieve.
    solver: str, optional
        MiniZinc solver to use. Default is "coinbc".

    Returns
    -------
    Solution
        Whether the target value can be achieved.
    """
    nest_asyncio.apply()
    model = Model()
    model.add_string(
        """
        int: n;
        float: capacity;
        float: target;
        array[1..n] of float: size;
        array[1..n] of float: profit;

        array[1..n] of var 0..1: x;

        constraint sum(i in 1..n)(size[i]*x[i]) <= capacity;
        constraint sum(i in 1..n)(profit[i]*x[i]) >= target;

        solve satisfy;
        """
    )
    solver_instance = Solver.lookup(solver)

    instance = Instance(solver_instance, model)
    instance["n"] = len(items)
    instance["capacity"] = capacity
    instance["profit"] = [item.value for item in items]
    instance["size"] = [item.weight for item in items]
    instance["target"] = target

    result = instance.solve()
    statistics = SolutionStatistics(
        time=result.statistics["solveTime"], n_solutions=1
    )

    return Solution(
        value=result.status.has_solution(),
        type=SolutionType.SATISFY,
        statistics=statistics,
    )


def greedy(items: list[Item], capacity: int) -> Solution:
    """Appy the greedy algorithm to a knapsack problem instance.

    Parameters
    ----------
    items : np.ndarray[Item]
        Array of items to consider for the knapsack.
    capacity : int
        Maximum weight capacity of the knapsack.

    Returns
    -------
    Solution
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
