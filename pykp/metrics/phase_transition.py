"""
This module provides an implementation of the phase transition of the knapsack problem, based on the following paper:
Yadav, Nitin, et al. "Phase transition in the knapsack problem." arXiv preprint arXiv:1806.10244 (2018).

Example:
	Compute the phase transition of the knapsack problem::

		from pykp.metrics import phase_transition

		grid, solvability_matrix = phase_transition(
			num_items = 10, 
			samples = 100,
			resolution = (20, 20),
		)

	Save the phase transition to a CSV file by specifying an optional `path` argument ::
	
		phase_transition(
			num_items = 10, 
			samples = 100,
			resolution = (20, 20),
			path = "phase_transition.csv"
		)
"""

import numpy as np
from pykp.solvers import *
from pykp.item import Item
from tqdm import tqdm
import pandas as pd


SOLVERS = ["branch_and_bound", "mzn_gecode"]

def _initialise_grid(
	resolution: tuple[int, int]
) -> tuple[np.ndarray, np.ndarray]:
	"""
	Initialise a grid of normalised capacities and profits to sample from.

	Args:
		resolution (tuple[int, int]): The resolution of the grid.
	
	Returns:
		tuple[np.ndarry, np.ndarray]: The grid of normalised capacities and profits.
	"""
	norm_c_step_size = 1/resolution[0]
	norm_p_step_size = 1/resolution[1]

	grid = np.meshgrid(
		np.linspace(0, 1 - norm_c_step_size, resolution[0]), 
		np.linspace(1 - norm_p_step_size, 0, resolution[1])
	)

	return grid


def _sample_instance(
	num_items: int, 
	norm_c: float, 
	norm_p: float
) -> tuple[list[Item], float, float]:
	"""
	Sample an instance of the knapsack problem.

	Args:
		num_items (int): The number of items in the instance.
		norm_c (float): The normalised capacity of the knapsack.
		norm_p (float): The normalised target profit of the knapsack.

	Returns:
		tuple[list[Item], float, float]: A tuple containing the items, capacity, and target profit of the instance.
	"""
	weights = np.random.uniform(0, 1, num_items)
	profits = np.random.uniform(0, 1, num_items)

	capacity = sum(weights) * norm_c
	target_profit = sum(profits) * norm_p

	items = [
		Item(value=profits[i], weight=weights[i]) 
		for i in range(num_items)
	]
	return items, capacity, target_profit


def _simulate_cell_solvability(
	norm_c_range: tuple[float, float],
	norm_p_range: tuple[float, float],
	num_items: int,
	samples: int,
	solver: Solver,
	progress: tqdm
) -> float:
	"""
	Simulate the solvability of a cell in the phase transition grid.

	Args:
		norm_c_range (tuple[float, float]): The normalised capacity range of the cell.
		norm_p_range (tuple[float, float]): The normalised target profit range of the cell.
		num_items (int): The number of items in the instance.
		samples (int): The number of samples to take.
		solver (Solver): The solver to use.
		progress (tqdm): tqdm progress bar to increment.

	Returns:
		float: The proportion of instances that are solvable.
	"""
	score = 0
	for _ in range(samples):
		norm_c_draw = np.random.uniform(norm_c_range[0], norm_c_range[1])
		norm_p_draw = np.random.uniform(norm_p_range[0], norm_p_range[1])

		items, capacity, target_profit = _sample_instance(
			num_items = num_items,
			norm_c = norm_c_draw,
			norm_p = norm_p_draw
		)
		result = solver.solve(
			items = items,
			capacity = capacity
		)
		if isinstance(result, np.ndarray):
			optimal_node = result[0]
		else:
			optimal_node = result
		if optimal_node.value >= target_profit:
			score += 1
		progress.update(1)
			
	return score / samples


def _save(
	phase_transition: np.ndarray, 
	grid: np.ndarray,
	path: str
):
	"""
	Save the phase transition to a CSV file.

	Args:
		phase_transition (np.ndarray): The phase transition grid.
		grid (np.ndarray): The grid of normalised capacities and profits.
		path (str): The path to save the CSV file.
	"""
	df = pd.DataFrame(
		{
			"nc_lower": grid[0].flatten(),
			"nc_upper": grid[0].flatten() + 1 / len(grid[0][0]),
			"np_lower": grid[1].flatten(),
			"np_upper": grid[1].flatten() + 1 / len(grid[1][0]),
			"solvability": phase_transition.flatten(),
		},
	)
	df.to_csv(path, index=False, float_format="%.6f")

def phase_transition(
	num_items: int, 
	samples: int = 100,
	solver: str = "branch_and_bound",
	resolution: tuple[int, int] = (41, 41),
	path: str = None
) -> tuple[np.ndarray, np.ndarray]:
	"""

	Args:
		num_items (int): Number of items in the knapsack.
		samples (int, optional): Number of knapsack samples to produce for each grid cell. Defaults to 100.
		solver (str, optional): Solver to use. Defaults to "branch_and_bound".
		resolution (tuple[int, int], optional): Resolution of the normalised capacity-normalised profit grid. The first number corresponds to the resolution of normalised capacity, and the second to the resolution of normalised profit. Defaults to (41, 41).
		path (str, optional): Path to save the phase transition to. Defaults to None.

	Returns:
		tuple[np.ndarray, np.ndarray]: The grid of normalised capacities and profits, and the phase transition.
	"""
	match solver:
		case "branch_and_bound":
			solver = BranchAndBound()
		case "mzn_gecode":
			solver = MznGecode()
		case _:
			raise ValueError(f"`method` must be one of: {SOLVERS}.")
	
	grid = _initialise_grid(resolution)
	points = list(zip(
		[(p, p + 1/resolution[0]) for p in grid[0].flatten()], 
		[(p, p + 1/resolution[1]) for p in grid[1].flatten()]
	))

	phase_transition = []
	with tqdm(total = samples * len(points)) as progress:
		for norm_c_range, norm_p_range in points:
			solvability = _simulate_cell_solvability(
				norm_c_range = norm_c_range,
				norm_p_range = norm_p_range,
				num_items = num_items,
				samples = samples,
				solver = solver,
				progress = progress
			)
			phase_transition.append(solvability)
	
	phase_transition = np.array(phase_transition).reshape(
		(resolution[0], resolution[1])
	)

	if path:
		_save(phase_transition, grid, path)

	return grid, phase_transition

if __name__ == "__main__":
	phase_transition(
		num_items = 10, 
		samples = 1,
		resolution = (10, 10),
		path = "phase_transition.csv"
	)