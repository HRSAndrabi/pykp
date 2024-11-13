"""
This module provides an interface for defining instances of the 0-1 Knapsack Problem.

Example:
	To define a Knapsack instance, initialise the `Knapsack` class with `Items` and a capacity constraint::
    
		from pykp import Knapsack
		from pykp import Item

		items = [
		   Item(value=10, weight=5), 
		   Item(value=15, weight=10), 
		   Item(value=7, weight=3)
		]
		capacity = 15
		knapsack = Knapsack(items=items, capacity=capacity)
		knapsack.solve()
		print(knapsack.optimal_nodes)
    
"""

import json
import numpy as np
from .item import Item
from .arrangement import Arrangement
import operator
import itertools
import pandas as pd
import matplotlib.pyplot as plt
from anytree import Node, PreOrderIter
import networkx as nx
from warnings import warn

class Knapsack:
	"""
    Represents a knapsack problem solver.

    Attributes:
    	items (np.ndarray[Item]): An array of items available for the knapsack problem.
    	capacity (int): The maximum weight capacity of the knapsack.
    	state (np.ndarray): Binary array indicating the inclusion/exclusion of items in the knapsack.
    	value (float): The total value of items currently in the knapsack.
    	weight (float): The total weight of items currently in the knapsack.
    	is_feasible (bool): Indicates if the knapsack is within its weight capacity.
    	is_at_capacity (bool): Indicates if the knapsack is at full capacity.
		terminal_nodes (np.ndarray[Arrangement]): An array of all possible arrangements of items that are under the weight constraint, and at full capacity
		optimal_nodes (np.ndarray[Arrangement]): An array of optimal solutions to the knapsack problem.
    """
	def __init__(
		self, 
		items: np.ndarray[Item], 
		capacity: int, 
		load_from_json: bool = False, 
		path_to_spec: str = None
	):
		"""
        Initialises a Knapsack instance.

        Parameters:
    		items (np.ndarray[Item]): An array of items for the knapsack problem.
    		capacity (int): The maximum weight capacity of the knapsack.
			load_from_json (bool, optional): Whether to load the instance from a .json spec. Default is False.
			path_to_spec (str, optional): Path to json spec file. Default is None.
        """

		if load_from_json:
			self.load_from_json(path_to_spec)
			return
		
		if len(items) == 0:
			raise ValueError("`items` must have length greater than 0.")
		if not np.all([isinstance(item, Item) for item in items]):
			raise ValueError("All elements in `items` must be of type `Item`.")
		if capacity < 0:
			raise ValueError("`capacity` must be non-negative.")
		if not isinstance(items, np.ndarray):
			items = np.array(items)
		
		self.items = items
		self.capacity = capacity
		self.state = np.zeros_like(items)
		self.value = 0
		self.weight = 0
		self.is_feasible = True
		self.is_at_capacity = False

		self.nodes = np.array([])
		self.feasible_nodes = np.array([])
		self.terminal_nodes = np.array([])
		self.optimal_nodes = np.array([])


	def solve(
		self, 
		solve_terminal_nodes: bool = False, 
		solve_feasible_nodes: bool = False,
		solve_all_nodes: bool = False,
		solve_second_best: bool = False
	):
		"""
		Solves the knapsack problem and returns optimal arrangements.

		Parameters:
			solve_terminal_nodes (bool, optional): Whether to find all terminal nodes. Default is False. This argument will be deprecated in future versions.
			solve_feasible_nodes (bool, optional): Whether to find all feasible nodes. Default is False. This argument will be deprecated in future versions.
			solve_all_nodes (bool, optional): Whether to find all nodes in the knapsack, including terminal nodes, and feasible nodes. Note, this method applies brute-force and may be infeasible for large instances. Default is False.
			solve_second_best (bool, optional): Whether to find the second best node. Default is False.

		Returns:
			np.ndarray: Optimal arrangements for the knapsack problem.
		"""
		# Remove in 2.0.0
		if solve_terminal_nodes:
			self.solve_terminal_nodes()

		# Remove in 2.0.0
		if solve_feasible_nodes:
			self.solve_feasible_nodes()

		if solve_all_nodes:
			self.solve_all_nodes()
		
		self.solve_branch_and_bound(solve_second_best = solve_second_best)
	

	def add(self, item: Item):
		"""
        Adds the specified item to the knapsack.

        Parameters:
        	item (Item): The item to be added to the knapsack.

        Returns:
        	np.ndarray: The updated knapsack state.
        """
		if not isinstance(item, Item):
			raise ValueError("`item` must be of type `Item`.")
		if not item in self.items:
			raise ValueError("`item` must be an existing `item` inside the `Knapsack` instance.")
		self.state[np.where(self.items == item)[0][0]] = 1
		self.__update_state()
		return self.state
	

	def remove(self, item: Item):
		"""
		Removes the specified item from the knapsack.

        Parameters:
        	item (Item): The item to be removed from the knapsack.

        Returns:
        	np.ndarray: The updated knapsack state.
		"""
		if not isinstance(item, Item):
			raise ValueError("`item` must be of type `Item`.")
		if not item in self.items:
			raise ValueError("`item` must be an existing `item` inside the `Knapsack` instance.")

		self.state[np.where(self.items == item)] = 0
		self.__update_state()
		return self.state
	
	
	def set_state(self, state: np.ndarray):
		"""
        Sets the knapsack state using the provided binary array.

        Parameters:
        	state (np.ndarray): Binary array indicating the inclusion/exclusion of items in the knapsack.

        Returns:
        	np.ndarray: The updated knapsack state.
        """
		self.state = state
		self.__update_state()
		return self.state
	
	
	def empty(self):
		"""
        Empties the knapsack by setting all items to be excluded.

        Returns:
        	np.ndarray: The updated knapsack state.
        """
		self.state = np.zeros_like(self.items)
		self.__update_state()
		return self.state


	def __update_state(self):
		"""
		Private method to update the knapsacks internal state.
		"""
		self.value = self.__calculate_value()
		self.weight = self.__calculate_weight()
		self.is_feasible = self.capacity >= self.weight
		out_items = [self.items[i] for i, element in enumerate(self.state) if element == 0]
		if sum(self.state) == len(self.state):
			self.is_at_capacity = True
		else:
			self.is_at_capacity = min([
				self.weight + item.weight 
				for item in out_items
			]) > self.capacity
	

	def __calculate_value(self):
		"""
        Calculates the total value of items currently in the knapsack.

        Returns:
        	float: The total value of items in the knapsack.
        """
		mask = np.ma.make_mask(self.state, shrink=False)
		return sum([item.value for item in self.items[mask]])


	def __calculate_weight(self):
		"""
        Calculates the total weight of items currently in the knapsack.

        Returns:
        	float: The total weight of items in the knapsack.
        """
		mask = np.ma.make_mask(self.state, shrink=False)
		return sum([item.weight for item in self.items[mask]])

	
	def __calculate_upper_bound(
		self, 
		included_items: np.ndarray[Item], 
		excluded_items: np.ndarray[Item]
	) -> float:
		"""
		Calculates the upper bound of the supplied branch. 

		Args:
			included_items (np.ndarray[Item]): Items included by all nodes within the branch.
			excluded_items (np.ndarray[Item]): Items excluded by all nodes within the branch.

		Returns:
			float: Upper bound of the branch.
		"""
		arrangement = Arrangement(
			items = self.items,
			state = np.array([int(item in included_items) for item in self.items])
		)
		candidate_items = np.array(sorted(
			set(self.items) - set(included_items) - set(excluded_items), 
			key = lambda item: item.value/item.weight, 
			reverse = True
		))
		balance = self.capacity - arrangement.weight

		if len(candidate_items) == 0:
			upper_bound = arrangement.value
		else:
			i = 0
			upper_bound = arrangement.value 
			while balance > 0 and i < len(candidate_items):
				item = candidate_items[i]	
				added_weight = min(balance, item.weight)
				upper_bound = upper_bound + added_weight * item.value / item.weight
				balance = balance - added_weight
				i += 1
		return upper_bound
	
	
	def __explore_node(
		self, 
		included_items: np.ndarray[Item], 
		excluded_items: np.ndarray[Item],
		parent: Node,
		upper_bound: float,
		solve_second_best: bool,
	):
		"""
		Determines weight/value of node and the upper bound of the branch containing the node. Prunes the branch if the upper bound is below the second-highest-valued terminal node discovered so far.

		Args:
			included_items (np.ndarray[Item]): Items included in the node.
			excluded_items (np.ndarray[Item]): Items excluded in the branch.
			parent (Node): Parent of the node.
			upper_bound (float): Upper bound of the node.
		"""
		arrangement = Arrangement(
			items = self.items,
			state = np.array([int(item in included_items) for item in self.items])
		)
		balance = self.capacity - arrangement.weight
		if balance < 0:
			return 
		
		if self.__is_subset_terminal(included_items):
			self.__bb_minimum_values = sorted(
				set([*self.__bb_minimum_values, arrangement.value])
			)[-1 * (1 + int(solve_second_best)):]
		
		node = Node(
			name = {"state": arrangement.state, "value": arrangement.value},
			items = arrangement.items,
			state = arrangement.state,
			value = arrangement.value,
			weight = arrangement.weight,
			upper_bound = upper_bound,
			parent = parent,
		)

		if len(excluded_items) + len(included_items) < len(self.items):
			next_item = self.items[len(excluded_items) + len(included_items)]

			upper_bound = self.__calculate_upper_bound(
				included_items = np.append(included_items, next_item), 
				excluded_items = excluded_items
			)
			if upper_bound > np.min(self.__bb_minimum_values):
				self.__bb_queue = np.append(
					self.__bb_queue, 
					{
						"included_items": np.append(included_items, next_item),
						"excluded_items": excluded_items,
						"parent": node,
						"upper_bound": upper_bound,
						"solve_second_best": solve_second_best,
					}
				)

			upper_bound = self.__calculate_upper_bound(
				included_items = included_items, 
				excluded_items = np.append(excluded_items, next_item)
			)
			if upper_bound > np.min(self.__bb_minimum_values):
				self.__bb_queue = np.append(
					self.__bb_queue, 
					{
						"included_items": included_items,
						"excluded_items": np.append(excluded_items, next_item),
						"parent": node,
						"upper_bound": upper_bound,
						"solve_second_best": solve_second_best,
					}
				)
			

	def solve_branch_and_bound(self, solve_second_best: bool):
		"""
		Solves the optimal and second-best terminal nodes using best-first branch-and-bound.
		"""
		self.items = np.array(sorted(
			self.items, 
			key = lambda item: item.value/item.weight, 
			reverse = True
		))
		self.__bb_queue = np.array([])
		self.__bb_minimum_values = np.array([-1])
		initial_arrangement = Arrangement(
			items = self.items,
			state = np.zeros_like(self.items)
		)
		upper_bound = self.__calculate_upper_bound(
			included_items = np.array([]), 
			excluded_items = np.array([])
		)
		root = Node(
			name = {"state": initial_arrangement.state, "value": initial_arrangement.value},
			items = self.items,
			state = np.zeros_like(self.items),
			value = 0,
			weight = 0,
			upper_bound = upper_bound,
			parent = None,
		)

		self.__bb_queue = np.append(
			{
				"included_items": np.array([self.items[0]]),
				"excluded_items": np.array([]),
				"parent": root,
				"upper_bound": self.__calculate_upper_bound(
					included_items = np.array([self.items[0]]), 
					excluded_items = np.array([]),
				),
				"solve_second_best": solve_second_best,
			},
			self.__bb_queue,
		)
		self.__bb_queue = np.append(
			{
				"included_items": np.array([]),
				"excluded_items": np.array([self.items[0]]),
				"parent": root,
				"upper_bound": self.__calculate_upper_bound(
					included_items = np.array([]), 
					excluded_items = np.array([self.items[0]]),
				),
				"solve_second_best": solve_second_best,
			},
			self.__bb_queue,
		)

		while len(self.__bb_queue) > 0:
			kwargs, self.__bb_queue = self.__bb_queue[0], self.__bb_queue[1:]
			self.__explore_node(**kwargs)

			self.__bb_queue = np.array(sorted(
				[item for item in self.__bb_queue if item["upper_bound"] > np.min(self.__bb_minimum_values)], 
				key = lambda x: x["upper_bound"],
				reverse = True
			))
	
		self.tree = root
		nodes = sorted(
			set([
				(tuple(node.state), node.value) 
				for node in PreOrderIter(root)
				if self.__is_subset_terminal(
					[self.items[i] for i, inside in enumerate(node.state) if bool(inside)]
				)
			]),
			key = lambda x: x[1],
			reverse = True
		)
		self.optimal_nodes = np.array([
			Arrangement(
				items = self.items,
				state = np.array(node[0])
			) for node
			in nodes
			if node[1] == nodes[0][1]
		])
		self.sahni_k = self.calculate_sahni_k(self.optimal_nodes[0])

		if solve_second_best:
			self.terminal_nodes = np.append(
				self.optimal_nodes,
				np.array(Arrangement(
					items = self.items,
					state = np.array(nodes[len(self.optimal_nodes)][0])
				) )
			) 
		

	def solve_terminal_nodes(self):
		"""
        Solves the knapsack problem and returns optimal arrangements. This method will be deprecated in future versions. Use `solve` with `solve_feasible_nodes=True` instead.

        Returns:
        	np.ndarray: Optimal arrangements for the knapsack problem.
        """
		warn("This method will be deprecated in future versions. Use `solve` with `solve_terminal_nodes=True` instead.", DeprecationWarning)
		self.solve_all_nodes()

		return self.terminal_nodes
	

	def solve_feasible_nodes(self) -> np.ndarray:
		"""
        Solves the knapsack problem and returns optimal arrangements. This method will be deprecated in future versions. Use `solve` with `solve_feasible_nodes=True` instead.

        Parameters:
    		verbose (bool, optional): If True, prints the string representation of the knapsack summary. Default is True.

        Returns:
        	np.ndarray: Optimal arrangements for the knapsack problem.
        """
		warn("This method will be deprecated in future versions. Use `solve` with `solve_terminal_nodes=True` instead.", DeprecationWarning)
		self.solve_all_nodes()

		return self.feasible_nodes


	def solve_all_nodes(self) -> np.ndarray:
		"""
        Computes all nodes in the knapsack problem. Populates attributes `nodes`, `feasible_nodes`, `terminal_nodes`, `optimal_nodes`.

		Returns:
			np.ndarray: All nodes in the knapsack problem.
        """
		self.nodes = np.array([])
		self.feasible_nodes = np.array([])
		self.terminal_nodes = np.array([])
		self.optimal_nodes = np.array([])

		for i in range(1, len(self.items) + 1):
			subsets = list(itertools.combinations(self.items, i))
			for subset in subsets:
				self.nodes = np.append(
					self.nodes, 
					Arrangement(
						items = self.items,
						state = np.array([int(item in subset) for item in self.items])
					)
				)	
				if self.__is_subset_feasible(subset):
					self.feasible_nodes = np.append(
						self.feasible_nodes, 
						Arrangement(
							items = self.items,
							state = np.array([int(item in subset) for item in self.items])
						)
					)	
				if self.__is_subset_terminal(subset):
					self.terminal_nodes = np.append(
						self.terminal_nodes, 
						Arrangement(
							items = self.items,
							state = np.array([int(item in subset) for item in self.items])
						)
					)	
		self.nodes = np.append(
			self.nodes,
			Arrangement(
				items = self.items,
				state = np.zeros(len(self.items), dtype = int)
			)
		)
		self.feasible_nodes = np.append(
			self.feasible_nodes,
			Arrangement(
				items = self.items,
				state = np.zeros(len(self.items), dtype = int)
			)
		)
		self.feasible_nodes = sorted(
			self.feasible_nodes, 
			key = operator.attrgetter("value"),
		) 	
		self.terminal_nodes = sorted(
			self.terminal_nodes, 
			key = operator.attrgetter("value"),
			reverse = True
		) 	
		self.optimal_nodes = np.array([
			arrangement for arrangement
			in self.terminal_nodes
			if arrangement.value == self.terminal_nodes[0].value
		])
		self.sahni_k = self.calculate_sahni_k(self.optimal_nodes[0])
		return self.nodes
	
	
	def __is_subset_feasible(self, subset: list[Item]) -> bool:
		"""Private method to determine whether subset of items is feasible (below capacity limit).

		Args:
			subset (list[Item]): Subset of items.

		Returns:
			bool: True if the node is terminal, otherwise False.
		"""
		weight = sum([i.weight for i in subset])
		balance = self.capacity - weight
		if balance < 0:
			return False
		return True
	

	def __is_subset_terminal(self, subset: list[Item]) -> bool:
		"""Private method to determine whether subset of items is a terminal node.

		Args:
			subset (list[Item]): Subset of items.

		Returns:
			bool: True if the node is terminal, otherwise False.
		"""
		weight = sum([i.weight for i in subset])
		balance = self.capacity - weight
		if balance < 0:
			return False
		remaining_items = set(self.items) - set(subset)
		for i in remaining_items:
			if i.weight <= balance:
				return False
		return True
		

	def calculate_sahni_k(self, arrangement: Arrangement):
		"""
        Calculates the Sahni-k value for a given arrangement.

        Parameters:
        	arrangement (Arrangement): The arrangement for which to calculate Sahni-k.

        Returns:
        	int: Sahni-k value.
        """
		if not isinstance(arrangement, Arrangement):
			raise ValueError("`arrangement` must be of type `Arrangement`.")

		for subset_size in range(0, len(arrangement.state)+1):
			in_indexes = [i for i, element in enumerate(arrangement.state) if element == 1]
			for subset in itertools.combinations(in_indexes, subset_size):
				initial_state = np.array([int(i in subset) for i in range(0, len(arrangement.state))])
				self.set_state(initial_state.copy())
				
				# Solve greedily
				while not self.is_at_capacity:
					out_items = [
						self.items[i] 
						for i, element 
						in enumerate(self.state) 
						if element == 0 and self.items[i].weight + self.weight <= self.capacity
					]
					densities = [item.value/item.weight for item in out_items]
					self.add(
						out_items[densities.index(max(densities))]
					)

				if np.array_equal(arrangement.state, self.state):
					return subset_size


	def plot_terminal_nodes_histogram(self) -> tuple[plt.Figure, plt.Axes]:
		"""
		Plots a histogram of values for possible at-capacity arrangements.

		Returns:
			tuple[plt.Figure, plt.Axes]: Figure and Axes objects.
		"""
		if not self.nodes.size == 2 ** len(self.items):
			self.solve_all_nodes()
			
		fig, axes = plt.subplots(
			figsize=(8, 3), 
			dpi=300, 
			nrows=1, 
			ncols=1,
			constrained_layout=True
		)

		axes.hist(
			[arrangement.value for arrangement in self.terminal_nodes],
			bins=100,
			color="#FF2C00",
			alpha=0.7,
		)
		axes.set_ylabel("Number of solutions")
		axes.set_xlabel("Solution value")
		plt.show()

		return fig, axes


	def __get_node_color(self, arrangement):
		# Optimal node
		if arrangement.value == self.optimal_nodes[0].value:
			return "#57ff29"
		
		# Feasible nodes
		if arrangement.weight < self.capacity:
			return "#003CAB"
			
		# Infeasible nodes
		return "#FF2C00"
		

	def plot_network(self) -> tuple[plt.Figure, plt.Axes]:
		"""
		Plots a network of knapsack nodes.

		Returns:
			tuple[plt.Figure, plt.Axes]: Figure and Axes objects.
		"""
		if not self.nodes.size == 2 ** len(self.items):
			self.solve_all_nodes()

		kp_network = kp_network = nx.DiGraph()

		for i, arrangement in enumerate(self.nodes):
			neighbours = [
				alt_arrangement for alt_arrangement in self.nodes
				if np.sum(np.abs(np.subtract(alt_arrangement.state, arrangement.state))) == 1
			]
			
			is_optimal = False
			if arrangement.value == self.optimal_nodes[0].value:
				is_optimal = True
				
			kp_network.add_node(
				arrangement,
			)
			kp_network.add_edges_from([
				(arrangement, alt_arrangement) 
				for alt_arrangement in neighbours
			])

		fig, axes = plt.subplots(
			figsize = (4 * len(self.items)/10, 4 * len(self.items)/10), 
			dpi = 1000, 
			nrows = 1, 
			ncols = 1,
			constrained_layout = True
		)

		node_colors = [self.__get_node_color(arrangement) for arrangement in kp_network.nodes]
		nx.draw_spring(
			kp_network, 
			ax = axes, 
			node_color = node_colors, 
			node_size = 2,
			width = 0.05, 
			arrowsize = 0.01,
			with_labels = False
		)
		plt.show()
		return fig, axes


	def write_to_json(self, path: str): 
		"""
		Writes the knapsack instance to .json.

		Args:
			path (str): Filepath to output file.
		"""
		if self.optimal_nodes.size == 0:
			self.solve(solve_second_best = False)

		instance_spec = {
			"capacity": self.capacity,
			"sahni_k": self.calculate_sahni_k(self.optimal_nodes[0]),
			"optimal_value": self.optimal_nodes[0].value,
			"items": [
				{
					"id": i,
					"value": item.value,
					"weight": item.weight,
				} for i, item in enumerate(self.items)
			]
		}

		with open(path, "w") as f:
			json.dump(instance_spec, f, indent = 4, default = int)
	

	def load_from_json(self, path: str): 
		"""
		Loads knapsack instance from a .json file.

		Args:
			path (str): Filepath to instance .json file.
		"""
		with open(path) as f:
			spec = json.load(f)
			self.__init__(
				items = np.array([Item(item["value"], item["weight"]) for item in spec["items"]]),
				capacity = int(spec["capacity"])
			)


	def summary(self):
		"""
        Generates a summary DataFrame containing information about the knapsack state and solutions.

        Returns:
        	pd.DataFrame: Summary DataFrame.
        """
		n_terminal = 2**len(self.items)
		n_optimal = len(self.optimal_nodes)
		
		header = [
			f"C = {self.capacity}",
			f"nC = {round(self.capacity / np.sum([item.weight for item in self.items]), 2)}",
			f"nTerminal = {n_terminal}",
			f"nOptimal = {n_optimal}",
		]

		if len(self.terminal_nodes) > len(self.optimal_nodes):
			best_inferior_solution = self.terminal_nodes[len(self.optimal_nodes)]
			delta = self.optimal_nodes[0].value - best_inferior_solution.value
			delta_pct = delta / self.optimal_nodes[0].value
			header.append(f"Δ = {delta}")
			header.append(f"Δ% = {delta_pct:.3}")
		else: 
			best_inferior_solution = None

		header = ", ".join(header)

		columns = pd.MultiIndex.from_arrays([
			[header] * len(self.items),
			[i+1 for i, item in enumerate(self.items)]
		])
			
		rows = [
			[item.value for item in self.items],
			[item.weight for item in self.items],
			[round(item.value / item.weight, 3) for item in self.items],
		]
		rows.extend([
			np.where(arrangement.state == 1, "IN", "OUT") 
			for arrangement in self.optimal_nodes
		])

		index = ["v", "w", "density"]
		index.extend([
			", ".join([
				f"solution (v = {arrangement.value}",
				f"w = {arrangement.weight}",
				f"k = {self.calculate_sahni_k(arrangement)})",
			])
			for arrangement in self.optimal_nodes
		])
		if best_inferior_solution is not None:
			index.append(", ".join([
				f"best inferior (v = {best_inferior_solution.value}",
				f"w = {best_inferior_solution.weight}",
				f"k = {self.calculate_sahni_k(best_inferior_solution)})",
			]))
			rows.append(np.where(best_inferior_solution.state == 1, "IN", "OUT") )

		return pd.DataFrame(rows, columns=columns, index=index, dtype="object")


	def __str__(self):
		return repr(self.summary())
		