"""
This module provides an implementation of the MiniZinc and Gecode solver for solving the knapsack problem. You should have MiniZinc 2.5.0 (or higher) installed on your system to use this solver. Note that this solver is not robust to multiple solutions, and will report only the first optimal solution found. If knowing all optimal solutions is important, consider using the branch-and-bound solver.

Example:
	To solve a knapsack problem instance using the MiniZinc Gecode solver, first create a list of items and then call the solver with the items and capacity::
	
		from pykp import Item, Solvers

		items = [
			Item(value=10, weight=5), 
			Item(value=15, weight=10), 
			Item(value=7, weight=3)
		]
		capacity = 15
		optimal_node = await solvers.mzn_gecode(items, capacity)
		print(optimal_node)

	Alternatively, construct an instance of the `Knapsack` class and call the `solve` method with "mzn_gecode" as the `method` argument::

		from pykp import Item, Knapsack
		
		items = [
			Item(value=10, weight=5), 
			Item(value=15, weight=10), 
			Item(value=7, weight=3)
		]
		capacity = 15
		instance = Knapsack(items=items, capacity=capacity)
		optimal_node = await instance.solve(method="mzn_gecode")
		print(optimal_node)
"""

import numpy as np
from ..arrangement import Arrangement
from ..item import Item
from minizinc import Instance, Model, Solver


async def mzn_gecode(
	items: np.ndarray[Item],
	capacity: int
) -> Arrangement:
	"""
	Solves the knapsack problem using the minizinc and gecode solver. This solver is not robust to multiple solutions.

	Args:
		items (np.ndarray[Item]): Items that can be included in the knapsack.
		capacity (int): Maximum weight capacity of the knapsack.

	Returns:
		Arrangement: The optimal arrangement of items in the knapsack.
	"""
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
		var float: TotalProfit=sum(i in OBJ)(profit[i]*x[i]);

		constraint sum(i in OBJ)(size[i]*x[i]) <= capacity;

		solve :: int_search(x, first_fail, indomain_max, complete) maximize TotalProfit;
		"""
	)
	gecode = Solver.lookup("gecode")

	instance = Instance(gecode, model)
	instance["n"] = len(items)
	instance["capacity"] = capacity
	instance["profit"] = [item.value for item in items]
	instance["size"] = [item.weight for item in items]

	result = await instance.solve_async()

	return Arrangement(
		items = items,
		state = np.array(result["x"])
	)

		