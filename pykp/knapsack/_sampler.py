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

from pykp.knapsack._item import Item
from pykp.knapsack._knapsack import Knapsack


class Sampler:
    """Generate random knapsack instances.

    Sample knapsack instances by specifying  the number of items, normalised
    capacity, and optionally custom distributions for weights and values.

    Parameters
    ----------
    num_items : int
        Number of items to include in each sampled knapsack instance.
    normalised_capacity : float | tuple[float, float]
        Normalised capacity of the knapsack, defined as the sum of item weights
        divided by the capacity constraint. Must be in the interval (0, 1). If
        a tuple is provided, the capacity will be sampled uniformly from the
        specified interval.

    Other Parameters
    ----------------
    weight_dist : str, optional
        Name of the distribution to sample item weights from. Defaults to
        uniform distribution over the half-open interval [0.001, 1).
    weight_dist_kwargs : dict, optional
        Additional keyword arguments to pass to the weight distribution
        function. Defaults to None.
    value_dist : str, optional
        Name of the distribution to sample item values from. Defaults to
        uniform distribution over the half-open interval [0.001, 1).
    value_dist_kwargs : dict, optional
        Additional keyword arguments to pass to the value distribution
        function. Defaults to None.

    .. note::
        Find a list of available distributions in the `numpy.random.Generator`
        documentation:
        https://numpy.org/doc/stable/reference/random/generator.html#distributions.

    Raises
    ------
    ValueError
        If `weight_dist` is specified without providing `weight_dist_kwargs`.
        If `value_dist` is specified without providing `value_dist_kwargs`.

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
        ...     normalised_capacity=(0.5, 0.8),
        ...     weight_dist="normal",
        ...     weight_dist_kwargs={"loc": 100, "scale": 10},
        ...     value_dist="normal",
        ...     value_dist_kwargs={"loc": 50, "scale": 5},
        ... )
        >>> knapsack = sampler.sample()
        >>> len(knapsack.items)
        5
    """

    def __init__(
        self,
        num_items: int,
        normalised_capacity: float | tuple[float, float],
        weight_dist: str = "uniform",
        value_dist: str = "uniform",
        weight_dist_kwargs: dict | None = None,
        value_dist_kwargs: dict | None = None,
    ):
        self.num_items = num_items

        if isinstance(normalised_capacity, (float, int)):
            if normalised_capacity <= 0 or normalised_capacity > 1:
                raise ValueError(
                    "`normalised_capacity` must be in the interval (0, 1)."
                )
        elif isinstance(normalised_capacity, tuple):
            if normalised_capacity[0] <= 0 or normalised_capacity[1] > 1:
                raise ValueError(
                    "`normalised_capacity` must be in the interval (0, 1)."
                )
        self.normalised_capacity = normalised_capacity

        if weight_dist != "uniform" and weight_dist_kwargs is None:
            raise ValueError(
                "`weight_dist_kwargs` must be provided "
                "if `weight_dist` is specified."
            )
        if value_dist != "uniform" and value_dist_kwargs is None:
            raise ValueError(
                "`value_dist_kwargs` must be provided "
                "if `value_dist` is specified."
            )
        self.weight_dist = weight_dist
        self.weight_dist_kwargs = weight_dist_kwargs or {
            "low": 0.001,
            "high": 1,
        }
        self.value_dist = value_dist
        self.value_dist_kwargs = value_dist_kwargs or {"low": 0.001, "high": 1}

    def _sample_dist(self, rng, dist_name, dist_kwargs, size):
        """Call desired distribution from the rng.

        Parameters
        ----------
        rng : np.random.Generator
        dist_name : str
            The name of the distribution to sample from.
        dist_kwargs : dict
            Additional kwargs to pass to the distribution.
        size : int
            Number of items to sample.

        Raises
        ------
        ValueError
            If the distribution name is not recognised.

        Returns
        -------
        np.ndarray
            Sampled array of shape (size,).
        """
        if isinstance(dist_name, str):
            # If it’s a recognized distribution name, call via getattr.
            # E.g. rng.uniform(**dist_kwargs, size=size)
            dist_func = getattr(rng, dist_name, None)
            if dist_func is None:
                raise ValueError(f"Unknown distribution name: {dist_name}")
            return dist_func(**{**dist_kwargs, "size": size})
        else:
            raise TypeError(
                "`weight_dist` and `value_dist` must be either a string "
                "or a callable that accepts (rng, size, **kwargs)."
            )

    def sample(self, seed: int = None) -> Knapsack:
        """Generate a random knapsack instance.

        Samples a knapsack instance using the sampling criteria provided to
        the sampler.

        Parameters
        ----------
        seed : int, optional
            Seed for the random sample. Defaults to None.

        Returns
        -------
        Knapsack
            A `Knapsack` object containing the sampled items and capacity

        Examples
        --------
        Sample a random knapsack instance:
            >>> from pykp.sampler import Sampler
            >>> sampler = Sampler(num_items=5, normalised_capacity=0.6)
            >>> sampler.sample()
            Knapsack(items=[...], capacity=...)

        Sample a random knapsack instance with a seed:
            >>> sampler = Sampler(num_items=5, normalised_capacity=0.6)
            >>> sampler.sample(seed=42)
            Knapsack(items=[...], capacity=1.2434165854867072)
            >>> sampler.sample(seed=42)
            Knapsack(items=[...], capacity=1.2434165854867072) # same result
        """
        rng = np.random.default_rng(seed)

        weights = self._sample_dist(
            rng, self.weight_dist, self.weight_dist_kwargs, self.num_items
        )
        profits = self._sample_dist(
            rng, self.value_dist, self.value_dist_kwargs, self.num_items
        )

        items = np.array(
            [Item(profits[i], weights[i]) for i in range(self.num_items)]
        )

        sum_weights = np.sum([item.weight for item in items])
        if isinstance(self.normalised_capacity, tuple):
            capacity = (
                rng.uniform(
                    low=self.normalised_capacity[0],
                    high=self.normalised_capacity[1],
                )
                * sum_weights
            )
        else:
            capacity = self.normalised_capacity * sum_weights

        if self.weight_dist == "integers":
            capacity = np.floor(capacity).astype(int)

        kp = Knapsack(
            items=items,
            capacity=capacity,
        )
        return kp
