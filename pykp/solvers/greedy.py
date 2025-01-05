"""
This module provides an implementation of the greedy algorithm for solving the knapsack problem.
"""

import numpy as np
from .solver import Solver
from ..arrangement import Arrangement
from ..item import Item


class Greedy(Solver):
	"""
	Represents an implementation of the greedy algorithm for solving the knapsack problem.
    """
	
	@staticmethod
	async def solve(
		items: np.ndarray[Item],
		capacity: int
	) -> Arrangement:
		"""
		Solves the knapsack problem using the greedy algorithm.

		Args:
			items (np.ndarray[Item]): Items that can be included in the knapsack.
			capacity (int): Maximum weight capacity of the knapsack.

		Returns:
			Arrangement: The greedy arrangement of items in the knapsack.
		"""
		state = np.zeros(len(items))
		weight = 0
		balance = capacity
		while balance > 0:
			remaining_items = [
				items[i] 
				for i, element 
				in enumerate(state) 
				if element == 0 and items[i].weight + weight <= capacity
			]
			if len(remaining_items) == 0:
				break
			best_item = max(
				remaining_items,
				key = lambda item: item.value / item.weight
			)
			state[np.where(items == best_item)[0][0]] = 1
			balance -= best_item.weight
			weight += best_item.weight

		return Arrangement(
			items = items,
			state = state
		)

	
