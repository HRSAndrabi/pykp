"""Tests for pykp.metrics module."""

import os
from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest

import pykp.metrics as metrics
from pykp.knapsack import Arrangement, Item, Knapsack

SOLVERS = ["branch_and_bound"]


@pytest.mark.parametrize("outcome", ["solvability", "time", "cost"])
@pytest.mark.parametrize("resolution", [(5, 5), (2, 3), (10, 10)])
def test_phase_transition_returns_correct_shape(resolution, outcome):
    """Test dimensions of grid and phase transition match resolution."""
    grid, phase_transition = metrics.phase_transition(
        num_items=5,
        samples=2,
        outcome=outcome,
        solver="branch_and_bound",
        resolution=resolution,
        path=None,
    )
    assert grid[0].shape == resolution
    assert grid[1].shape == resolution
    assert phase_transition.shape == resolution


@pytest.mark.parametrize("solver", SOLVERS)
def test_phase_transition_with_solvers(solver):
    """Test that all solvers do not raise an error."""
    try:
        metrics.phase_transition(
            num_items=5,
            samples=2,
            solver=solver,
            resolution=(2, 2),
            path=None,
        )
    except Exception as e:
        pytest.fail(f"Unexpected error occurred for solver: {e}")


def test_phase_transition_with_invalid_solver_raises():
    """Test that passing an invalid solver raises a ValueError."""
    with pytest.raises(ValueError):
        metrics.phase_transition(
            num_items=5, samples=2, solver="invalid_solver", resolution=(2, 2)
        )


@pytest.mark.parametrize("outcome", ["time", "solvability", "cost"])
def test_phase_transition_saves_csv(tmp_path, outcome):
    """Test saving .csv file."""
    output_path = tmp_path / "phase_transition_output.csv"
    resolution = (2, 2)

    grid, solvability_matrix = metrics.phase_transition(
        num_items=5,
        samples=2,
        outcome=outcome,
        solver="branch_and_bound",
        resolution=resolution,
        path=str(output_path),
    )

    assert output_path.exists(), "CSV file was not created."

    df = pd.read_csv(output_path)
    expected_columns = [
        "nc_lower",
        "nc_upper",
        "np_lower",
        "np_upper",
    ]
    if outcome == "time":
        expected_columns.append("time")
    elif outcome == "solvability":
        expected_columns.append("solvability")
    elif outcome == "cost":
        expected_columns.append("time")
    assert all(col in df.columns for col in expected_columns), (
        "Missing expected columns in CSV."
    )

    # Check row count = resolution[0] * resolution[1]
    assert len(df) == (resolution[0] * resolution[1]), (
        "CSV file has unexpected number of rows."
    )


def test_phase_transition_values_in_range():
    """Test that the values in the solvability matrix lie between 0 and 1."""
    resolution = (2, 2)
    grid, solvability_matrix = metrics.phase_transition(
        num_items=5,
        samples=2,
        outcome="solvability",
        solver="branch_and_bound",
        resolution=resolution,
        path=None,
    )
    assert np.all(solvability_matrix >= 0.0) and np.all(
        solvability_matrix <= 1.0
    ), "Solvability values are not all within [0, 1]."


@pytest.mark.parametrize("seed", [1, 2])
def test_phase_transition_reproducibility(seed):
    """Test that the phase transition is reproducible."""
    resolution = (2, 2)
    num_items = 5
    samples = 5
    grid, solvability_matrix = metrics.phase_transition(
        num_items=num_items,
        samples=samples,
        outcome="solvability",
        solver="branch_and_bound",
        resolution=resolution,
        path=None,
        seed=seed,
    )

    grid2, solvability_matrix2 = metrics.phase_transition(
        num_items=num_items,
        samples=samples,
        outcome="solvability",
        solver="branch_and_bound",
        resolution=resolution,
        path=None,
        seed=seed,
    )

    assert np.all(grid[0] == grid2[0]), "Inconsistent grid."
    assert np.all(grid[0] == grid2[0]), "Inconsistent grid."
    assert np.all(solvability_matrix == solvability_matrix2), (
        "Inconsistent solvability matrix."
    )


@pytest.mark.parametrize("capacity", [1, 2, 3])
def test_fsr_returns_correct_value(capacity):
    """Test that the feasibility ratio is calculated correctly."""
    items = [
        Item(value=1, weight=1),
        Item(value=1, weight=1),
        Item(value=1, weight=1),
    ]
    instance = Knapsack(items=items, capacity=capacity)
    fsr = metrics.fsr(instance)
    nodes = 2 ** len(items)

    expected_fsr = len(instance.feasible_nodes) / len(instance.nodes)
    assert fsr == expected_fsr, "Feasibility ratio is incorrect."


@pytest.mark.parametrize("capacity", [1, 2, 3])
def test_fbp_returns_correct_value(capacity):
    """Test that feasibility boundary proportion is calculated correctly."""
    items = [
        Item(value=1, weight=1),
        Item(value=1, weight=1),
        Item(value=1, weight=1),
    ]
    instance = Knapsack(items=items, capacity=capacity)
    fbp = metrics.fbp(instance)
    edges = 2 ** (len(items) - 1) * len(items)

    feasibility_boundary_crossings = [
        (u, v)
        for u, v in instance.graph.edges()
        if (u.weight > instance.capacity) != (v.weight > instance.capacity)
    ]
    expected_fbp = len(feasibility_boundary_crossings) / edges
    assert fbp == expected_fbp, "Feasibility boundary proportion is incorrect."


@pytest.mark.parametrize(
    "instance, expected_sahni_k",
    [
        (
            Knapsack(
                items=np.array(
                    [
                        Item(500, 750),
                        Item(350, 406),
                        Item(505, 564),
                        Item(505, 595),
                        Item(640, 803),
                        Item(435, 489),
                        Item(465, 641),
                        Item(50, 177),
                        Item(220, 330),
                        Item(170, 252),
                    ]
                ),
                capacity=1900,
            ),
            1,
        ),
        (
            Knapsack(
                items=np.array(
                    [
                        Item(300, 205),
                        Item(350, 252),
                        Item(400, 352),
                        Item(450, 447),
                        Item(47, 114),
                        Item(20, 50),
                        Item(8, 28),
                        Item(70, 251),
                        Item(5, 19),
                        Item(5, 20),
                    ]
                ),
                capacity=1044,
            ),
            3,
        ),
    ],
)
def test_sahni_k(instance, expected_sahni_k):
    """Test that the Sahni-k metric is calculated correctly."""
    instance.solve()
    result = metrics.sahni_k(instance.optimal_nodes[0], instance.capacity)
    assert result == expected_sahni_k, "Sahni-k value is incorrect."


@pytest.mark.parametrize(
    "arrangement, capacity, expected_sahni_k_inverse",
    [
        (
            Arrangement(
                items=[Item(60, 6), Item(49, 5)],
                state=[1, 0],
            ),
            6,
            0,
        ),
        (
            Arrangement(
                items=[Item(60, 6), Item(49, 5), Item(49, 5)],
                state=[0, 1, 1],
            ),
            10,
            1,
        ),
        (
            Arrangement(
                items=[
                    Item(60, 6),
                    Item(60, 6),
                    Item(49, 5),
                    Item(49, 5),
                ],
                state=[0, 0, 1, 1],
            ),
            10,
            2,
        ),
    ],
)
def test_sahni_k_inverse_returns_minimum_forbidden_item_count(
    arrangement,
    capacity,
    expected_sahni_k_inverse,
):
    """Test the minimum number of non-target items that must be forbidden."""
    result = metrics.sahni_k_inverse(arrangement, capacity)

    assert result == expected_sahni_k_inverse


def test_sahni_k_inverse_rejects_non_arrangement():
    """Test that the target must be an Arrangement."""
    with pytest.raises(ValueError):
        metrics.sahni_k_inverse([], capacity=10)


def test_sahni_k_inverse_rejects_target_over_capacity():
    """Test that an infeasible target arrangement is rejected."""
    arrangement = Arrangement(items=[Item(10, 11)], state=[1])

    with pytest.raises(ValueError):
        metrics.sahni_k_inverse(arrangement, capacity=10)


def test_sahni_k_inverse_breaks_density_ties_by_item_order():
    """Test that density ties preserve the arrangement's item order."""
    arrangement = Arrangement(
        items=[Item(60, 6), Item(50, 5), Item(50, 5)],
        state=[0, 1, 1],
    )

    result = metrics.sahni_k_inverse(arrangement, capacity=10)

    assert result == 1
