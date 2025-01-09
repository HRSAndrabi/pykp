"""
This module provides an interface for sampling knapsack instances.

Example:
    Randomly sample a large number of knapsack instances using the Sampler
    class::

        from pykp.sampler import Sampler

        samples = []
        for _ in tqdm(range(100)):
            sampler = Sampler(
                num_items=10,
                normalised_capacity=0.5,
            )
            samples.append(Sampler.sample(sampler))

    You can also specify the distribution to sample weights and values from::

        from pykp.sampler import Sampler

        samples = []
        for _ in tqdm(range(100)):
            sampler = Sampler(
                num_items=10,
                normalised_capacity=0.5,
                weight_dist=(
                    np.random.default_rng().normal,
                    {"loc": 100, "scale": 10},
                ),
                value_dist=(
                    np.random.default_rng().normal,
                    {"loc": 100, "scale": 10},
                ),
            )
"""

from typing import Tuple

import numpy as np

from .item import Item
from .knapsack import Knapsack


class Sampler:
    def __init__(
        self,
        num_items: int,
        normalised_capacity: float,
        weight_dist: Tuple[np.random.Generator, dict] = (
            np.random.default_rng().uniform,
            {"low": 0.001, "high": 1},
        ),
        value_dist: Tuple[np.random.Generator, dict] = (
            np.random.default_rng().uniform,
            {"low": 0.001, "high": 1},
        ),
    ):
        """
        A class for sampling knapsack instances.

        Args:
            num_items (int): The number of items to sample.
            normalised_capacity (float): The normalised capacity of the
                knapsack (sum of weights / capacity constraint).
            weight_dist (Tuple[np.random.Generator, dict], optional): The
                distribution to sample weights from. The argument should be a
                tuple where the first element is the generator function, and
                the second element is a dictionary of keyword arguments to the
                generator. Defaults to random uniform over open
                interval (0, 1).
            value_dist (Tuple[np.random.Generator, dict], optional): The
                distribution to sample weights from. The argument should be a
                tuple where the first element is the generator function, and
                the second element is a dictionary of keyword arguments to the
                generator. Defaults to random uniform over open
                interval (0, 1).
        """
        self.num_items = num_items
        self.normalised_capacity = normalised_capacity
        self.weight_dist, self.weight_dist_kwargs = weight_dist
        self.value_dist, self.value_dist_kwargs = value_dist

    def sample(self) -> Knapsack:
        """
        Samples a knapsack instance using the sampling criteria provided to
        the sampler.

        Returns:
            Knapsack: The sampled knapsack instance.
        """
        weights = self.weight_dist(
            **self.weight_dist_kwargs, size=self.num_items
        )
        profits = self.value_dist(
            **self.value_dist_kwargs, size=self.num_items
        )

        items = np.array(
            [Item(profits[i], weights[i]) for i in range(self.num_items)]
        )

        sum_weights = np.sum([item.weight for item in items])
        kp = Knapsack(
            items=items,
            capacity=self.normalised_capacity * sum_weights,
        )
        return kp
