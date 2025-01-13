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
    assert sampler.weight_dist == "uniform"
    assert isinstance(sampler.weight_dist_kwargs, dict)
    assert "low" in sampler.weight_dist_kwargs
    assert "high" in sampler.weight_dist_kwargs

    assert sampler.value_dist == "uniform"
    assert isinstance(sampler.value_dist_kwargs, dict)
    assert "low" in sampler.value_dist_kwargs
    assert "high" in sampler.value_dist_kwargs


def test_sampler_init_with_custom_distributions():
    """Test Sampler initialisation with custom distributions."""
    custom_weight_dist = (
        "normal",
        {"loc": 10, "scale": 5},
    )
    custom_value_dist = (
        "normal",
        {"loc": 20, "scale": 2},
    )
    num_items = 10
    nc = 0.5

    sampler = Sampler(
        num_items=num_items,
        normalised_capacity=nc,
        weight_dist=custom_weight_dist[0],
        weight_dist_kwargs=custom_weight_dist[1],
        value_dist=custom_value_dist[0],
        value_dist_kwargs=custom_value_dist[1],
    )

    assert sampler.num_items == num_items
    assert sampler.normalised_capacity == nc

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
    sampler = Sampler(
        num_items=10,
        normalised_capacity=0.5,
        weight_dist="integers",
        weight_dist_kwargs={"low": 1, "high": 2},
        value_dist="integers",
        value_dist_kwargs={"low": 1, "high": 2},
    )
    knapsack = sampler.sample()
    knapsack.items

    assert knapsack.capacity == int(0.5 * 10)  # Should be 4


@pytest.mark.parametrize("normalised_capacity", [0.0, 0.1, 0.9, 1.5])
def test_sampler_different_normalised_capacities(normalised_capacity):
    """Test that the capacity of the knapsack is calculated correctly."""
    sampler = Sampler(num_items=3, normalised_capacity=normalised_capacity)
    knapsack = sampler.sample()
    total_weight = sum(item.weight for item in knapsack.items)
    expected_capacity = normalised_capacity * total_weight

    assert np.isclose(knapsack.capacity, expected_capacity)
    assert len(knapsack.items) == 3


@pytest.mark.parametrize("seed", [1, 2, 3, 4, 5])
def test_sample_reporducible(seed: int):
    """Test that the samples are reproducible."""
    sampler = Sampler(num_items=5, normalised_capacity=0.8)

    knapsack = sampler.sample(seed=seed)
    knapsack2 = sampler.sample(seed=seed)
    values = [item.value for item in knapsack.items]
    values2 = [item.value for item in knapsack2.items]
    weights = [item.weight for item in knapsack.items]
    weights2 = [item.weight for item in knapsack2.items]

    assert knapsack.capacity == knapsack2.capacity
    assert np.array_equal(values, values2)
    assert np.array_equal(weights, weights2)
    assert np.array_equal(knapsack.state, knapsack2.state)
