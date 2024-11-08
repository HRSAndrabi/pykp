"""
This module provides an interface for sampling knapsack instances.

Example:
	Randomly sample a large number of knapsack instances using the Sampler class::

		import numpy as np
		samples = []
		for _ in tqdm(range(10_000)):
		   sampler = Sampler(
			num_items = 10,
			normalised_capacity = 0.5,
			density_range = (0.1, 1.2),
			solution_value_range = (1_300, 1_700),
		   )
		   samples.append(Sampler.sample(sampler))
"""

import numpy as np
from .knapsack import Knapsack
from .item import Item
from typing import Tuple

class Sampler():
	def __init__(
		self, 
		num_items: int, 
		normalised_capacity: float,
		density_range: Tuple[float, float],
		solution_value_range: Tuple[int, int],
	):
		"""
		A class for sampling knapsack instances.

		Args:
			num_items (int): The number of items to sample.
			normalised_capacity (float): The normalised capacity of the knapsack 
			(sum of weights / capacity constraint).
			density_range (Tuple[float, float]): The range of item value densities 
			to sample from.
			solution_value_range (Tuple[int, int]): The range of solution values 
			for the knapsack.
		"""
		self.num_items = num_items
		self.normalised_capacity = normalised_capacity
		self.density_range = density_range
		self.solution_value_range = solution_value_range

	
	def sample(self) -> Knapsack:
		"""
		Samples a knapsack instance using the sampling criteria provided to
		the sampler.

		Returns:
			Knapsack: The sampled knapsack instance.
		"""
		weights = np.random.uniform(
			low = 100, 
			high = 1000,
			size = self.num_items,
		)
		densities = np.random.uniform(
			low = self.density_range[0], 
			high = self.density_range[1],
			size = self.num_items,
		)
		values = weights * densities
		items = np.array([Item(int(values[i]), int(weights[i])) for i in range(self.num_items)])	

		sum_weights = np.sum([item.weight for item in items])
		kp = Knapsack(
			items = items,
			capacity = int(self.normalised_capacity * sum_weights),
		)
		kp.solve()
		solution_value = np.random.uniform(self.solution_value_range[0], self.solution_value_range[1])
		scale_factor =  solution_value / kp.optimal_nodes[0].value
		scaled_items = np.array([
			Item(
				np.max([int(item.value * scale_factor), 1]), 
				np.max([int(item.weight * scale_factor), 1])
			)
			for item in items
		])
		scaled_items = np.array(
			sorted(scaled_items, key=lambda item: item.value/item.weight, reverse=True)
		)
		scaled_kp = Knapsack(
			items = scaled_items,
			capacity = int(kp.capacity * scale_factor),
		)
		scaled_kp.solve()
		return scaled_kp
