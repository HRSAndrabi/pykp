"""
This module provides an implementation of branch and bound algorithm for solving the knapsack problem.

Example:
	To solve a knapsack problem instance using the branch-and-bound algorithm, first create a list of items and then call the solver with the items and capacity::
	
		from pykp import Item, Solvers

		items = [
			Item(value=10, weight=5), 
			Item(value=15, weight=10), 
			Item(value=7, weight=3)
		]
		capacity = 15
		optimal_nodes = solvers.branch_and_bound(items, capacity)
		print(optimal_nodes)

	Alternatively, construct an instance of the `Knapsack` class and call the `solve` method with "branch_and_bound" as the `method` argument::

		from pykp import Item, Knapsack
		
		items = [
			Item(value=10, weight=5), 
			Item(value=15, weight=10), 
			Item(value=7, weight=3)
		]
		capacity = 15
		instance = Knapsack(items=items, capacity=capacity)
		optimal_nodes = instance.solve(method="branch_and_bound")
		print(optimal_nodes)
"""

import numpy as np
from queue import PriorityQueue
from dataclasses import dataclass, field
from ..arrangement import Arrangement
from ..item import Item

@dataclass(order=True, frozen=True)
class Node():
	"""
	Represents a node in the branch-and-bound tree.

	Attributes:
		priority (float): The priority of the node.
		upper_bound (float): The upper bound of the node.
		items (np.ndarray[Item]): Items that can be included in the knapsack.
		value (int): The total value of items in the node.
		weight (int): The total weight of items in the node.
	"""
	priority: float = field(compare = True)
	upper_bound: float = field(compare = False)
	items: np.ndarray[Item] = field(compare = False)
	value: int = field(compare = False)
	weight: int = field(compare = False)
	included_items: np.ndarray[Item] = field(compare = False)
	excluded_items: np.ndarray[Item] = field(compare = False)

def _calculate_upper_bound(
	items: np.ndarray[Item],
	capacity: int,
	included_items: np.ndarray[Item], 
	excluded_items: np.ndarray[Item]
) -> float:
	"""
	Calculates the upper bound of the supplied branch. 

	Args:
		items (np.ndarray[Item]): Items that can be included in the knapsack.
		capacity (int): Maximum weight capacity of the knapsack.
		included_items (np.ndarray[Item]): Items included by all nodes within the branch.
		excluded_items (np.ndarray[Item]): Items excluded by all nodes within the branch.

	Returns:
		float: Upper bound of the branch.
	"""
	arrangement = Arrangement(
		items = items,
		state = np.array([int(item in included_items) for item in items])
	)
	candidate_items = np.array(sorted(
		set(items) - set(included_items) - set(excluded_items), 
		key = lambda item: item.value/item.weight, 
		reverse = True
	))
	balance = capacity - arrangement.weight

	if balance < 0:
		return -1

	if len(candidate_items) == 0 or balance == 0:
		return arrangement.value

	i = 0
	upper_bound = arrangement.value 
	while balance > 0 and i < len(candidate_items):
		item = candidate_items[i]	
		added_weight = min(balance, item.weight)
		upper_bound = upper_bound + added_weight * item.value / item.weight
		balance = balance - added_weight
		i += 1
	return upper_bound


def _expand_node(
	node: Node,
	capacity: int,
	incumbent: Node,
) -> np.ndarray:
	"""
	Expands a node in the branch-and-bound tree. Returns child nodes to explore.

	Args:
		node (Node): Node to expand.
		capacity (int): Maximum weight capacity of the knapsack.
		incumbent (Node): The best node found so far.
	
	Returns:
		np.ndarray: The child nodes of the expanded node.
	"""
	arrangement = Arrangement(
		items = node.items,
		state = np.array([int(item in node.included_items) for item in node.items])
	)
	if arrangement.weight > capacity:
		return []  

	if len(node.included_items) + len(node.excluded_items) >= len(node.items):
		return []  # No further branching possible

	next_item = node.items[len(node.included_items) + len(node.excluded_items)]
	
	# Generate children (left-branch includes item, right-branch excludes item)
	# only return them if we do not prune by upper_bound.
	children = []

	for included in [True, False]:
		included_items = np.append(node.included_items, next_item) if included else node.included_items
		excluded_items = np.append(node.excluded_items, next_item) if not included else node.excluded_items
		upper_bound = _calculate_upper_bound(
			items = node.items,
			capacity = capacity,
			included_items = included_items,
			excluded_items = excluded_items
		)
		child = Node(
			priority = -upper_bound,
			items = node.items,
			value = node.value + next_item.value * included,
			weight = node.weight + next_item.weight * included,
			included_items = included_items,
			excluded_items = excluded_items,
			upper_bound = upper_bound
		)
		if child.upper_bound > incumbent.value:
			children.append(child)

	return children


def _is_terminal_node(node: Node, capacity: int) -> bool:
	"""Private method to determine whether subset of items is a terminal node.

	Args:
		node (Node): Node to check.
		capacity (int): Maximum weight capacity of the knapsack.

	Returns:
		bool: True if the node is terminal, otherwise False.
	"""
	weight = sum([i.weight for i in node.included_items])
	balance = capacity - weight
	if balance < 0:
		return False
	remaining_items = set(node.items) - set(node.included_items)
	for i in remaining_items:
		if i.weight <= balance:
			return False
	return True


def branch_and_bound(items: np.ndarray[Item], capacity: int) -> np.ndarray[Arrangement]:
	"""
	Solves the knapsack problem using the branch-and-bound algorithm. This solver is robust to multiple optimal solutions.

	Args:
		items (np.ndarray[Item]): Items that can be included in the knapsack.
		capacity (int): Maximum weight capacity of the knapsack.

	Returns:
		np.ndarray[Arrangement]: The optimal arrangements of items in the knapsack.
	"""
	items = np.array(sorted(
		items, 
		key = lambda item: item.value/item.weight, 
		reverse = True
	))
	upper_bound = _calculate_upper_bound(
		items = items,
		capacity = capacity,
		included_items = np.array([]),
		excluded_items = np.array([])
	)
	root = Node(
		priority = -sum([item.value for item in items]),
		items = items,
		value = 0,
		weight = 0,
		included_items = np.array([]),
		excluded_items = np.array([]),
		upper_bound = upper_bound
	)
	queue = PriorityQueue()
	queue.put(root)
	incumbent = root
	optimal_nodes = np.array([root])
	next = queue.get()

	while next.upper_bound >= incumbent.value:
		children = _expand_node(next, capacity, incumbent)
		for child in children:
			queue.put(child)
			if child.value > incumbent.value:
				incumbent = child
				if _is_terminal_node(
					node = child,
					capacity = capacity
				):
					optimal_nodes = np.array([child])
			elif _is_terminal_node(
				node = child,
				capacity = capacity
			) and child.value == incumbent.value:
				optimal_nodes = np.append(optimal_nodes, child)
	
		if queue.empty():
			break
		next = queue.get()

	result = np.array([Arrangement(
		items = items,
		state = np.array([int(item in node.included_items) for item in items])
	) for node in optimal_nodes])

	return np.array(list(set(result)))
