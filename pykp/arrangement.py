"""
This module provides an interface for defining arrangements of items.

Example:
    Define an arangement of items for the knapsack problem::

		from pykp import Arrangement, Item

		items = [
		   Item(value=10, weight=5),
		   Item(value=20, weight=10),
		   Item(value=30, weight=15),
		]
		state = [0, 1, 1]
		arrangement = Arrangement(items=items, state=state)
		print(arrangement)
    
"""

import numpy as np
from .item import Item

class Arrangement():
	"""
    Represents an arrangement of items for the knapsack problem.

    Attributes:
    	items (np.ndarray[Item]): An array of items for the knapsack problem.
    	state (np.ndarray[int]): Binary array indicating the inclusion/exclusion of items in the arrangement.
    	value (int): The total value of items in the arrangement.
    	weight (int): The total weight of items in the arrangement.
    """
	def __init__(
		self,
		items: np.ndarray[Item],
		state: np.ndarray[int], 
	):
		"""Initialises an Arrangement instance.

		Args:
        	items (np.ndarray[Item]): An array of items for the knapsack problem.
        	state (np.ndarray[int]): Binary array indicating the inclusion/exclusion of items in the arrangement.
        	capacity (int): The maximum weight capacity constraint for the arrangement.
		"""
		if not np.all(np.isin(state, [0, 1])):
			raise ValueError("Elements of `state` must be 0 or 1.")
		
		self.items = items
		self.state = state
		self.value = self.__calculate_value()
		self.weight = self.__calculate_weight()

	
	def __calculate_value(self):
		"""
        Calculates the total value of items currently in the knapsack.

        Returns:
        	float: The total value of items in the knapsack.
        """
		return sum([self.items[i].value for i, inside in enumerate(self.state) if bool(inside)])


	def __calculate_weight(self):
		"""
        Calculates the total weight of items currently in the knapsack.

        Returns:
        	float: The total weight of items in the knapsack.
        """
		return sum([self.items[i].weight for i, inside in enumerate(self.state) if bool(inside)])

	
	def __str__(self):
		state = int("".join(self.state.astype(int).astype(str)), 2)
		return f"(v: {self.value}, w: {self.weight}, s: {state})"
	 
	def __repr__(self):
		state = int("".join(self.state.astype(int).astype(str)), 2)
		return f"(v: {self.value}, w: {self.weight}, s: {state})"


