from numbers import Integral

import nest_asyncio
import numpy as np
from minizinc import Instance, Model, Solver

from pykp.knapsack._arrangement import Arrangement
from pykp.knapsack._item import Item

from ._solution import *


def _as_non_negative_int(value, name: str) -> int:
    """Validate and normalise an integer MiniZinc input."""
    if isinstance(value, bool) or not isinstance(value, Integral):
        raise TypeError(f"`{name}` must be an integer")
    if value < 0:
        raise ValueError(f"`{name}` must be non-negative")
    return int(value)


def minizinc(
    items: list[Item], capacity: int, solver: str = "coinbc"
) -> Solution:
    """Solves the knapsack problem using the MiniZinc.

    Parameters
    ----------
    items : list[Item]
        Array of items to consider for the knapsack.
    capacity : int
        Maximum weight capacity of the knapsack.
    solver: str, optional
        MiniZinc solver to use. Default is "coinbc".

    Returns
    -------
    Solution : Solution
        The optimal arrangement of items in the knapsack.

    Examples
    --------
    Solve a knapsack problem instance using MiniZinc and the COIN-OR
    Branch-and-Cut solver:

    >>> from pykp.knapsack import Item
    >>> from pykp import solvers
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

    >>> from pykp.knapsack import Item
    >>> from pykp.knapsack import Knapsack
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

    Raises
    ------
    TypeError
        If the capacity, an item value, or an item weight is not an integer.
    ValueError
        If the capacity, an item value, or an item weight is negative.
    """
    capacity = _as_non_negative_int(capacity, "capacity")
    profits = [
        _as_non_negative_int(item.value, f"items[{i}].value")
        for i, item in enumerate(items)
    ]
    sizes = [
        _as_non_negative_int(item.weight, f"items[{i}].weight")
        for i, item in enumerate(items)
    ]

    if len(items) == 0:
        return Solution(
            value=Arrangement(items=items, state=np.array([], dtype=int)),
            type=SolutionType.MAXIMISE,
            statistics=SolutionStatistics(
                time=0.0,
                n_solutions=1,
                cost=None,
            ),
        )

    nest_asyncio.apply()
    model = Model()
    model.add_string(
        """
        include "knapsack.mzn";

        int: n; % number of objects
        int: capacity; % capacity of knapsack

        int: totalProfit;
        int: totalCapacity;

        set of int: OBJ = 1..n;
        array[OBJ] of int: profit; % profits of the items
        array[OBJ] of int: size; % weights of the items

        % decisions to make (which item should be included)
        array[OBJ] of var 0..1: x;

        var 0..totalCapacity: W;
        var 0..totalProfit: P;

        constraint knapsack(size, profit, x, W, P);
        constraint W <= capacity;

        solve maximize P;

        output ["x = ", show(x), "\\n", "Solution=",show(P)];
        """
    )
    solver_instance = Solver.lookup(solver)

    instance = Instance(solver_instance, model)
    instance["n"] = len(items)
    instance["capacity"] = capacity
    instance["totalProfit"] = sum(profits)
    instance["totalCapacity"] = sum(sizes)
    instance["profit"] = profits
    instance["size"] = sizes

    result = instance.solve()
    propagations = (
        result.statistics["propagations"] if solver == "gecode" else None
    )
    statistics = SolutionStatistics(
        time=result.statistics["solveTime"],
        n_solutions=1,
        cost=propagations,
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
    propagations = (
        result.statistics["propagations"] if solver == "gecode" else None
    )
    statistics = SolutionStatistics(
        time=result.statistics["solveTime"],
        n_solutions=1,
        cost=propagations,
    )

    return Solution(
        value=result.status.has_solution(),
        type=SolutionType.SATISFY,
        statistics=statistics,
    )
