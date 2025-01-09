import pytest
import numpy as np
from unittest.mock import MagicMock
from pykp import Item, solvers
import json

HEURISTIC_SOLVERS = ["greedy"]
OPTIMAL_SOLVERS = ["branch_and_bound"]
ALL_SOLVERS = HEURISTIC_SOLVERS + OPTIMAL_SOLVERS

with open("tests/test_cases.json") as f:
	TEST_CASES = json.load(f)

@pytest.fixture
def solver(request):
	if request.param == "greedy":
		solver = solvers.greedy
	elif request.param == "branch_and_bound":
		solver = solvers.branch_and_bound
	
	return solver

@pytest.mark.parametrize("solver", ALL_SOLVERS, indirect=True)
def test_empty_items(solver):
	"""
	Test that branch_and_bound returns an empty arrangement when there are no items.
	"""
	items = np.array([])
	solutions = solver(items, 0)

	if not isinstance(solutions, np.ndarray):
		solutions = [solutions]
		
	assert len(solutions) == 1
	assert solutions[0].value == 0
	assert solutions[0].weight == 0

@pytest.mark.parametrize("solver", ALL_SOLVERS, indirect=True)
def test_single_item_fits(solver):
	"""
	Test a single item that fits in the knapsack.
	"""
	items = np.array([Item(value=10, weight=5)])
	capacity = 10
	solutions = solver(items, capacity)

	if not isinstance(solutions, np.ndarray):
		solutions = [solutions]
	
	assert len(solutions) == 1
	assert solutions[0].value == 10
	assert solutions[0].weight == 5

@pytest.mark.parametrize("solver", ALL_SOLVERS, indirect=True)
def test_single_item_does_not_fit(solver):
	"""
	Test a single item that does not fit in the knapsack.
	"""
	items = np.array([Item(value=10, weight=15)])
	capacity = 10
	solutions = solver(items, capacity)

	if not isinstance(solutions, np.ndarray):
		solutions = [solutions]
	
	assert len(solutions) == 1
	assert solutions[0].value == 0
	assert solutions[0].weight == 0

@pytest.mark.parametrize("solver", ALL_SOLVERS, indirect=True)
def test_all_items_fit(solver):
	"""
	Test scenario where all items fit in the knapsack.
	"""
	items = np.array([
		Item(value=10, weight=5),
		Item(value=20, weight=5),
		Item(value=30, weight=5)
	])
	capacity = 15
	solutions = solver(items, capacity)

	if not isinstance(solutions, np.ndarray):
		solutions = [solutions]
	
	assert len(solutions) == 1
	assert solutions[0].value == 60
	assert solutions[0].weight == 15

@pytest.mark.parametrize("solver", ALL_SOLVERS, indirect=True)
def test_all_items_do_not_fit(solver):
	"""
	Test scenario where no items fit in the knapsack.
	"""
	items = np.array([
		Item(value=10, weight=15),
		Item(value=20, weight=15),
		Item(value=30, weight=15)
	])
	capacity = 10
	solutions = solver(items, capacity)

	if not isinstance(solutions, np.ndarray):
		solutions = [solutions]
	
	assert len(solutions) == 1
	assert solutions[0].value == 0
	assert solutions[0].weight == 0
	assert np.array_equal(solutions[0].state, np.zeros(len(items)))

@pytest.mark.parametrize("solver", OPTIMAL_SOLVERS, indirect=True)
@pytest.mark.parametrize("case", TEST_CASES)
def test_correct_optimal_found(solver, case):
	"""
	Test that the correct optimal solution is found for a series of test cases.
	"""
	items = np.array([
		Item(value=case["values"][i], weight=case["weights"][i]) for i in range(len(case["values"]))
	])
	solution = solver(np.array(items), case["capacity"])
	if isinstance(solution, np.ndarray):
		solution = solution[0]

	assert np.isclose(solution.value, case["optimal_value"])


