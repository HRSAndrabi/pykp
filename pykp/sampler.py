"""Provides an interface for sampling knapsack instances.

Examples
--------
Sample a random knapsack instance by sampling from default distributions:
    >>> from pykp.sampler import Sampler
    >>> sampler = Sampler(num_items=5, normalised_capacity=0.6)
    >>> knapsack = sampler.sample()
    >>> len(knapsack.items)
    5

Create a sampler with custom distributions:
    >>> import numpy as np
    >>> sampler = Sampler(
    ...     num_items=5,
    ...     normalised_capacity=0.8,
    ...     weight_dist=(
    ...         np.random.default_rng().normal,
    ...         {"loc": 100, "scale": 10},
    ...     ),
    ...     value_dist=(
    ...         np.random.default_rng().normal,
    ...         {"loc": 50, "scale": 5},
    ...     ),
    ... )
    >>> knapsack = sampler.sample()
    >>> len(knapsack.items)
    5
"""

import numpy as np

from .item import Item
from .knapsack import Knapsack


class Sampler:
    """Generate random knapsack instances.

    Sample knapsack instances by specifying  the number of items, normalised
    capacity, and optionally custom distributions for weights and values.

    Parameters
    ----------
    num_items : int
        Number of items to include in each sampled knapsack instance.
    normalised_capacity : float
        Normalised capacity of the knapsack, defined as the sum of item weights
        divided by the capacity constraint.
    weight_dist : tuple of (np.random.Generator, dict), optional
        A tuple where the first element is the generator function for sampling
        item weights, and the second element is a dictionary containing keyword
        arguments for the generator. Defaults to uniform distribution over the
        interval (0.001, 1).
    value_dist : tuple of (np.random.Generator, dict), optional
        A tuple where the first element is the generator function for sampling
        item values, and the second element is a dictionary containing keyword
        arguments for the generator. Defaults to uniform distribution over the
        interval (0.001, 1).

    Examples
    --------
    Sample a random knapsack instance by sampling from default distributions:
        >>> from pykp.sampler import Sampler
        >>> sampler = Sampler(num_items=5, normalised_capacity=0.6)
        >>> knapsack = sampler.sample()
        >>> len(knapsack.items)
        5

    Create a sampler with custom distributions:
        >>> import numpy as np
        >>> sampler = Sampler(
        ...     num_items=5,
        ...     normalised_capacity=0.8,
        ...     weight_dist=(
        ...         np.random.default_rng().normal,
        ...         {"loc": 100, "scale": 10},
        ...     ),
        ...     value_dist=(
        ...         np.random.default_rng().normal,
        ...         {"loc": 50, "scale": 5},
        ...     ),
        ... )
        >>> knapsack = sampler.sample()
        >>> len(knapsack.items)
        5
    """

    def __init__(
        self,
        num_items: int,
        normalised_capacity: float,
        weight_dist: tuple[np.random.Generator, dict] = (
            np.random.default_rng().uniform,
            {"low": 0.001, "high": 1},
        ),
        value_dist: tuple[np.random.Generator, dict] = (
            np.random.default_rng().uniform,
            {"low": 0.001, "high": 1},
        ),
    ):
        self.num_items = num_items
        self.normalised_capacity = normalised_capacity
        self.weight_dist, self.weight_dist_kwargs = weight_dist
        self.value_dist, self.value_dist_kwargs = value_dist

    def sample(self) -> Knapsack:
        """Generate a random knapsack instance.

        Samples a knapsack instance using the sampling criteria provided to
        the sampler.

        Returns
        -------
        Knapsack
            A `Knapsack` object containing the sampled items and capacity
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
