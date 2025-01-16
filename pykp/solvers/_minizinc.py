import nest_asyncio
import numpy as np
from minizinc import Instance, Model, Solver

from pykp.knapsack._arrangement import Arrangement
from pykp.knapsack._item import Item

from ._solution import *


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
    Solution : Solution
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
