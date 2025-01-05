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
from ..knapsack import Knapsack
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
	
	instance = Knapsack(items = arrangement.items, capacity = capacity)

	for subset_size in range(0, len(arrangement.state)+1):
		in_indexes = [i for i, element in enumerate(arrangement.state) if element == 1]
		for subset in itertools.combinations(in_indexes, subset_size):
			initial_state = np.array([int(i in subset) for i in range(0, len(arrangement.state))])
			instance.set_state(initial_state.copy())
			
			# Solve greedily
			while not instance.is_at_capacity:
				out_items = [
					instance.items[i] 
					for i, element 
					in enumerate(instance.state) 
					if element == 0 and instance.items[i].weight + instance.weight <= instance.capacity
				]
				densities = [item.value/item.weight for item in out_items]
				instance.add(
					out_items[densities.index(max(densities))]
				)
			# Check hamming distance between arrangement and current state
			hamming_distance = sum(np.absolute(np.subtract(arrangement.state, instance.state)))	
			if hamming_distance == 0:
				return subset_size