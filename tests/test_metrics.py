"""Tests for pykp.metrics module."""

import os
from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest

import pykp.metrics as metrics

SOLVERS = ["branch_and_bound"]


@pytest.mark.parametrize("resolution", [(5, 5), (2, 3), (10, 10)])
def test_phase_transition_returns_correct_shape(resolution):
    """Test dimensions of grid and phase transition match resolution."""
    grid, solvability_matrix = metrics.phase_transition(
        num_items=5,
        samples=2,
        solver="branch_and_bound",
        resolution=resolution,
        path=None,
    )
    assert grid[0].shape == (resolution[1], resolution[0])
    assert grid[1].shape == (resolution[1], resolution[0])

    assert solvability_matrix.shape == resolution


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


def test_phase_transition_saves_csv(tmp_path):
    """Test saving .csv file."""
    output_path = tmp_path / "phase_transition_output.csv"
    resolution = (2, 2)

    grid, solvability_matrix = metrics.phase_transition(
        num_items=5,
        samples=2,
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
        "solvability",
    ]
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
        solver="branch_and_bound",
        resolution=resolution,
        path=None,
    )
    assert np.all(solvability_matrix >= 0.0) and np.all(
        solvability_matrix <= 1.0
    ), "Solvability values are not all within [0, 1]."
