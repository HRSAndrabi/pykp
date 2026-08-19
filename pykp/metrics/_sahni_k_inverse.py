"""Compute the inverse Sahni-k metric."""

import itertools

from pykp.knapsack._arrangement import Arrangement


def sahni_k_inverse(
    arrangement: Arrangement,
    capacity: int,
) -> int:
    """Compute inverse Sahni-k for a given knapsack arrangement.

    Inverse Sahni-k is the minimum number of items outside a target
    arrangement that must be forbidden for deterministic density-greedy
    filling, starting from an empty knapsack, to reproduce the target.

    Parameters
    ----------
    arrangement : Arrangement
        The target knapsack arrangement.
    capacity : int
        The capacity constraint of the knapsack.

    Returns
    -------
    int
        The inverse Sahni-k value.

    Examples
    --------
    >>> from pykp.knapsack import Arrangement, Item
    >>> from pykp import metrics
    >>> items = [Item(60, 6), Item(49, 5), Item(49, 5)]
    >>> arrangement = Arrangement(items=items, state=[0, 1, 1])
    >>> metrics.sahni_k_inverse(arrangement, capacity=10)
    1

    """
    if not isinstance(arrangement, Arrangement):
        raise ValueError("`arrangement` must be of type `Arrangement`.")
    if arrangement.weight > capacity:
        raise ValueError(
            "The total weight of items included in the `Arrangement` "
            "exceeds the `capacity`."
        )

    items = arrangement.items
    target_indices = [
        index
        for index, element in enumerate(arrangement.state)
        if element == 1
    ]
    outside_indices = [
        index
        for index, element in enumerate(arrangement.state)
        if element == 0
    ]

    for subset_size in range(0, len(outside_indices) + 1):
        for forbidden_indices in itertools.combinations(
            outside_indices, subset_size
        ):
            selected_indices = []
            weight = 0

            while True:
                available_indices = [
                    index
                    for index, item in enumerate(items)
                    if index not in forbidden_indices
                    and index not in selected_indices
                    and weight + item.weight <= capacity
                ]

                if not available_indices:
                    break

                max_density_index = max(
                    available_indices,
                    key=lambda index: items[index].value / items[index].weight,
                )
                selected_indices.append(max_density_index)
                weight += items[max_density_index].weight

            if set(selected_indices) == set(target_indices):
                return subset_size
