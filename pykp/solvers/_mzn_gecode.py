"""
This module provides an implementation of the minizinc and gecode solver for solving the knapsack problem.
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

	Example:
		Solve a knapsack problem using the minizinc and gecode solver::
		
			import numpy as np
			from pykp import Item, solvers

			items = np.array([
				Item(weight = 10, value = 60),
				Item(weight = 20, value = 100),
				Item(weight = 30, value = 120),
			])
			capacity = 50
			arrangement = await solvers.mzn_gecode(items, capacity)

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

		