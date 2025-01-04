"""
This module provides an implementation of the minizinc and gecode solver for solving the knapsack problem.
"""

import numpy as np
from ..arrangement import Arrangement
from ..item import Item
from minizinc import Instance, Model, Solver


class MznGecode():
	"""
	Represents an implementation of the minizinc and gecode solver for solving the knapsack problem.
	"""
	
	@staticmethod
	async def solve(
		items: np.ndarray[Item],
		capacity: int
	) -> Arrangement:
		
		model = Model()
		model.add_string(
			"""
			int: n; % number of objects
			set of int: OBJ = 1..n;
			int: capacity;
			array[OBJ] of int: profit;
			array[OBJ] of int: size;

			%var set of OBJ: x;
			array[OBJ] of var 0..1: x;
			var int: TotalProfit=sum(i in OBJ)(profit[i]*x[i]);

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

		return np.array([Arrangement(
			items = items,
			state = np.array(result["x"])
		)])

		