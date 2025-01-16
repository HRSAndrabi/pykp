import itertools

from pykp.knapsack._arrangement import Arrangement


def sahni_k(
    arrangement: Arrangement,
    capacity: int,
) -> int:
    """Compute the Sahni-k metric for a given knapsack arrangement.

    The Sahni-k metric [1]_ [2]_ is defined as the smallest number of items
    (k) whose inclusion in the solution is necessary for the greedy algorithm
    (applied to the remaining items) to yield an optimal solution.

    If `k` equals zero, the Sahni-k algorithm coincides with the greedy
    algorithm. If k is equal to the number of items in the solution, the
    algorithm is similar to a brute-force search through the entire search
    space.

    Parameters
    ----------
    arrangement : Arrangement
        A knapsack arrangement (subset of items) for which to compute Sahni-k.
    capacity : int
        The capacity constraint of the knapsack.

    Returns
    -------
        int: Sahni-k value.

    Examples
    --------
    >>> from pykp import Arrangement
    >>> from pykp import Item
    >>> from pykp import metrics
    >>>
    >>> items = [Item(10, 5), Item(20, 8), Item(15, 7)]
    >>> arr = Arrangement(items=items, state=[1, 0, 1])
    >>> metrics.sahni_k(arr, capacity=15)
    2

    References
    ----------

        .. [1] Sahni, Sartaj. "Approximate algorithms for the 0/1 knapsack
           problem." Journal of the ACM (JACM) 22.1 (1975): 115-124.

        .. [2] Murawski, Carsten, and Peter Bossaerts. "How humans solve
           complex problems: The case of the knapsack problem." Scientific
           reports 6.1 (2016): 34851.

    """
    if not isinstance(arrangement, Arrangement):
        raise ValueError("`arrangement` must be of type `Arrangement`.")
    if arrangement.weight > capacity:
        raise ValueError(
            """The total weight of items included in the `Arrangement` exceeds 
            the `capacity`."""
        )

    in_items = [
        arrangement.items[i]
        for i, element in enumerate(arrangement.state)
        if element == 1
    ]
    for subset_size in range(0, len(arrangement.state) + 1):
        for subset in itertools.combinations(in_items, subset_size):
            subset = list(subset)
            weight = sum([item.weight for item in subset])

            # Solve greedily
            while True:
                if len(subset) == len(arrangement.items):
                    break

                # Check instance at capacity
                out_items = [
                    item for item in arrangement.items if item not in subset
                ]
                if (
                    min([weight + item.weight for item in out_items])
                    > capacity
                ):
                    break

                densities = [item.value / item.weight for item in out_items]
                max_density_item = out_items[densities.index(max(densities))]
                subset.append(max_density_item)
                weight = sum([item.weight for item in subset])

            if set(subset) == set(in_items):
                return subset_size
