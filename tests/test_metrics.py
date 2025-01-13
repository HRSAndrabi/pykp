"""Tests for pykp.metrics module."""

import os
from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest

import pykp.metrics as metrics

SOLVERS = ["branch_and_bound"]


@pytest.mark.parametrize("outcome", ["solvability", "time", "both"])
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

    if outcome == "both":
        assert phase_transition[0].shape == resolution
        assert phase_transition[1].shape == resolution
    else:
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


@pytest.mark.parametrize("outcome", ["time", "solvability", "both"])
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
    elif outcome == "both":
        expected_columns.extend(["time", "solvability"])
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
