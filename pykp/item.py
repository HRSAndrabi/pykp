"""
This module provides an interface for defining items inside a knapsack problem instance.

Example:
	Use the Item class to define items for the knapsack problem::

		from pykp import Item

		items = [
		   Item(value=10, weight=5),
		   Item(value=20, weight=10),
		   Item(value=30, weight=15),
		]
    
"""

from dataclasses import dataclass, field

@dataclass(frozen = True, eq = False)
class Item:
	"""
	Represents an item for the knapsack problem.

    Attributes:
    	value (int): The value of the item.
    	weight (int): The weight of the item.
	"""
	value: int = field(compare = False)
	weight: int = field(compare = False)