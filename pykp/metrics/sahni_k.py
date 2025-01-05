"""
This module provides an implementation of the Sahni-K metric for evaluating arrangements of items in the knapsack problem.

Example:
	To calculate the Sahni-k of the optimal solution to a knapsack problem instance, first solve the instance and then call the metric on the optimal arrangement::
    
		from pyinstance import Knapsack
		from pyinstance import Item
		import pyinstance.metrics as metrics

		items = [
		   Item(value=10, weight=5), 
		   Item(value=15, weight=10), 
		   Item(value=7, weight=3)
		]
		capacity = 15
		instance = Knapsack(items=items, capacity=capacity)
		await instance.solve()

		sahni_k = metrics.sahni_k(instance.optimal_nodes[0], capacity)
		print(sahni_k)
"""

import numpy as np
from ..arrangement import Arrangement
import itertools

def sahni_k(
	arrangement: Arrangement,
	capacity: int,
) -> int:
	"""
	Calculates the Sahni-k value for a given arrangement.

	Parameters:
		arrangement (Arrangement): The arrangement for which to calculate Sahni-k.
		capacity (int): The capacity of the knapsack.

	Returns:
		int: Sahni-k value.
	"""
	if not isinstance(arrangement, Arrangement):
		raise ValueError("`arrangement` must be of type `Arrangement`.")
	if arrangement.weight > capacity:
		raise ValueError("The total weight of items included in the `Arrangement` exceeds the `capacity`.")
	
	in_items = [arrangement.items[i] for i, element in enumerate(arrangement.state) if element == 1]
	for subset_size in range(0, len(arrangement.state)+1):
		for subset in itertools.combinations(in_items, subset_size):
			subset = list(subset)
			weight = sum([item.weight for item in subset])

			# Solve greedily
			while True:
				if len(subset) == len(arrangement.items):
					break
				
				# Check instance at capacity
				out_items = [
					item 
					for item in arrangement.items 
					if item not in subset
				]
				if min([
						weight + item.weight 
						for item in out_items
					]) > capacity:
					break

				densities = [item.value/item.weight for item in out_items]
				max_density_item = out_items[densities.index(max(densities))]
				subset.append(max_density_item)
				weight = sum([item.weight for item in subset])

			if set(subset) == set(in_items):
				return subset_size