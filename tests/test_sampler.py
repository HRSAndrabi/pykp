"""Tests for pykp.sampler module."""

from unittest.mock import MagicMock

import numpy as np
import pytest

from pykp.sampler import Sampler


def test_sampler_init_with_defaults():
    """Test Sampler initialisation with default distributions."""
    sampler = Sampler(num_items=5, normalised_capacity=0.5)
    assert sampler.num_items == 5
    assert sampler.normalised_capacity == 0.5
    assert callable(sampler.weight_dist)
    assert isinstance(sampler.weight_dist_kwargs, dict)
    assert "low" in sampler.weight_dist_kwargs
    assert "high" in sampler.weight_dist_kwargs

    assert callable(sampler.value_dist)
    assert isinstance(sampler.value_dist_kwargs, dict)
    assert "low" in sampler.value_dist_kwargs
    assert "high" in sampler.value_dist_kwargs


def test_sampler_init_with_custom_distributions():
    """Test Sampler initialisation with custom distributions."""
    custom_weight_dist = (
        np.random.default_rng().normal,
        {"loc": 10, "scale": 5},
    )
    custom_value_dist = (
        np.random.default_rng().normal,
        {"loc": 20, "scale": 2},
    )

    sampler = Sampler(
        num_items=10,
        normalised_capacity=0.3,
        weight_dist=custom_weight_dist,
        value_dist=custom_value_dist,
    )

    assert sampler.num_items == 10
    assert sampler.normalised_capacity == 0.3
    # Check references to the distributions
    assert sampler.weight_dist == custom_weight_dist[0]
    assert sampler.weight_dist_kwargs == custom_weight_dist[1]
    assert sampler.value_dist == custom_value_dist[0]
    assert sampler.value_dist_kwargs == custom_value_dist[1]


def test_sampler_sample_returns_knapsack():
    """Test that the `sample` method returns a Knapsack instance."""
    sampler = Sampler(num_items=5, normalised_capacity=0.8)
    knapsack = sampler.sample()

    # Check that `knapsack` has the attributes we expect
    # (depending on how your Knapsack class is implemented, these may differ).
    assert hasattr(knapsack, "items")
    assert hasattr(knapsack, "capacity")
    assert len(knapsack.items) == 5


def test_sampler_sample_capacity_calculation():
    """Test that the capacity of the knapsack is calculated correctly."""
    sampler = Sampler(num_items=4, normalised_capacity=0.5)

    # Mock the distributions to return a predictable weights array.
    # For example, all weights = 2 => sum_weights = 8 => capacity = 4
    # (with normalised_capacity = 0.5).
    sampler.weight_dist = MagicMock(return_value=np.array([2, 2, 2, 2]))
    sampler.value_dist = MagicMock(return_value=np.array([5, 5, 5, 5]))

    knapsack = sampler.sample()
    assert knapsack.capacity == int(0.5 * 8)  # Should be 4


@pytest.mark.parametrize("normalised_capacity", [0.0, 0.1, 0.9, 1.5])
def test_sampler_different_normalised_capacities(normalised_capacity):
    """Test that the capacity of the knapsack is calculated correctly."""
    sampler = Sampler(num_items=3, normalised_capacity=normalised_capacity)
    knapsack = sampler.sample()
    total_weight = sum(item.weight for item in knapsack.items)
    expected_capacity = normalised_capacity * total_weight

    assert np.isclose(knapsack.capacity, expected_capacity)
    assert len(knapsack.items) == 3
