"""
This module contains implementations of various solvers for the knapsack
problem.
"""

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

from collections import defaultdict
from dataclasses import dataclass, field
from queue import PriorityQueue

import nest_asyncio
import numpy as np
from minizinc import Instance, Model, Solver

from .arrangement import Arrangement
from .item import Item


@dataclass(order=True, frozen=True)
class Node:
    """
    Represents a node in the branch-and-bound tree.

    Attributes:
        priority (float): The priority of the node.
        upper_bound (float): The upper bound of the node.
        items (np.ndarray[Item]): Items that can be included in the knapsack.
        value (int): The total value of items in the node.
        weight (int): The total weight of items in the node.
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
    """
    Calculates the upper bound of the supplied branch.

    Args:
        items (np.ndarray[Item]): Items that can be included in the knapsack.
        capacity (int): Maximum weight capacity of the knapsack.
        included_items (np.ndarray[Item]): Items included by all nodes within
            the branch.
        excluded_items (np.ndarray[Item]): Items excluded by all nodes within
            the branch.

    Returns:
        float: Upper bound of the branch.
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
    """
    Expands a node in the branch-and-bound tree. Returns child nodes to
    explore.

    Args:
        node (Node): Node to expand.
        capacity (int): Maximum weight capacity of the knapsack.
        incumbent (flaot): The best value found so far.

    Returns:
        np.ndarray: The child nodes of the expanded node.
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


def _is_terminal_node(node: Node, capacity: int) -> bool:
    """
    Private method to determine whether subset of items is a terminal node.

    Args:
        node (Node): Node to check.
        capacity (int): Maximum weight capacity of the knapsack.

    Returns:
        bool: True if the node is terminal, otherwise False.
    """
    weight = sum([i.weight for i in node.included_items])
    balance = capacity - weight
    if balance < 0:
        return False
    remaining_items = (
        set(node.items) - set(node.included_items) - set(node.excluded_items)
    )
    for i in remaining_items:
        if i.weight <= balance:
            return False
    return len(remaining_items) == 0


def branch_and_bound(
    items: np.ndarray[Item],
    capacity: int,
    n=1,
) -> np.ndarray[Arrangement]:
    """
    Provides an implementation of branch and bound algorithm for
    solving the knapsack problem.

    Example:
        To solve a knapsack problem instance using the branch-and-bound
        algorithm, first create a list of items and then call the solver
        with the items and capacity::

            from pykp import Item, Solvers

            items = [
                Item(value=10, weight=5),
                Item(value=15, weight=10),
                Item(value=7, weight=3),
            ]
            capacity = 15
            optimal_nodes = solvers.branch_and_bound(items, capacity)
            print(optimal_nodes)

        Alternatively, construct an instance of the `Knapsack` class and
        call the `solve` method with "branch_and_bound" as the `method`
        argument::

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

        Use the optional `n` argument to return the n-best solutions found by
        the solver::

            optimal_nodes = solvers.branch_and_bound(items, capacity, n=5)
            print(optimal_nodes)

        .. note::
            The `n` argument is on solution values, not the number of
            solutions. If `n` is set to 1, the solver returns all solutions
            that achieve the distinct optimal value. More than one solution
            may be returned if there are multiple solutions with the same
            optimal value. Similarly, if `n` is set to n, the solver returns
            all solutions that achieve the n-highest possible values.

    Args:
        items (np.ndarray[Item]): Items that can be included in the knapsack.
        capacity (int): Maximum weight capacity of the knapsack.
        n (int, optional): The n-best solutions to return. If set to 1, the
            solver returns all solutions that achieve the distinct optimal
            value. If set to n, the solver returns the solutions that achieve
            the n-highest possible values. Defaults to 1.

    Returns:
        np.ndarray[Arrangement]: The optimal arrangements of items in the
            knapsack.
    """
    if len(items) == 0:
        return np.array([Arrangement(items=items, state=np.array([]))])

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
            if child.value >= incumbent and _is_terminal_node(child, capacity):
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
    result = np.array(result)

    return result


def mzn_gecode(items: np.ndarray[Item], capacity: int) -> Arrangement:
    """
    Provides an implementation of the MiniZinc and Gecode solver for
    solving the knapsack problem. You should have MiniZinc 2.5.0 (or higher)
    installed on your system to use this solver. Note that this solver is not
    robust to multiple solutions, and will report only the first optimal
    solution found. If knowing all optimal solutions is important, consider
    using the branch-and-bound solver.

    Example:
        To solve a knapsack problem instance using the MiniZinc Gecode solver,
        first create a list of items and then call the solver with the items
        and capacity::

            from pykp import Item, Solvers

            items = [
                Item(value=10, weight=5),
                Item(value=15, weight=10),
                Item(value=7, weight=3),
            ]
            capacity = 15
            optimal_node = solvers.mzn_gecode(items, capacity)
            print(optimal_node)

        Alternatively, construct an instance of the `Knapsack` class and call
        the `solve` method with "mzn_gecode" as the `method` argument::

            from pykp import Item, Knapsack

            items = [
                Item(value=10, weight=5),
                Item(value=15, weight=10),
                Item(value=7, weight=3),
            ]
            capacity = 15
            instance = Knapsack(items=items, capacity=capacity)
            optimal_node = instance.solve(method="mzn_gecode")
            print(optimal_node)

        Args:
            items (np.ndarray[Item]): Items that can be included in the
            knapsack. capacity (int): Maximum weight capacity of the knapsack.

        Returns:
            Arrangement: The optimal arrangement of items in the knapsack.
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
    gecode = Solver.lookup("gecode")

    instance = Instance(gecode, model)
    instance["n"] = len(items)
    instance["capacity"] = capacity
    instance["profit"] = [item.value for item in items]
    instance["size"] = [item.weight for item in items]

    result = instance.solve()

    return Arrangement(items=items, state=np.array(result["x"]))


def greedy(items: np.ndarray[Item], capacity: int) -> Arrangement:
    """
    Provides an implementation of the greedy algorithm for solving the
    knapsack problem.

    Example:
        Solve a knapsack problem using the greedy algorithm::

            import numpy as np
            from pykp import Item, solvers

            items = np.array([
                    Item(weight = 10, value = 60),
                    Item(weight = 20, value = 100),
                    Item(weight = 30, value = 120),
            ])
            capacity = 50
            arrangement = solvers.greedy(items, capacity
    """
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
        state[np.where(items == best_item)[0][0]] = 1
        balance -= best_item.weight
        weight += best_item.weight

    return Arrangement(items=items, state=state)
