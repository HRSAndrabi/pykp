from pykp.knapsack import Knapsack


def fsr(instance: Knapsack) -> float:
    r"""Compute the feasibility ratio for a given knapsack problem.

    The feasibility ratio is the ratio of the number of feasible nodes in the
    search space to the total number of nodes in the search
    space. [#]_ Feasibility is determined by the capacity constraint of the
    knapsack.

    .. math::

        FSR = \frac{\text{Number of feasible nodes}}
        {\text{Total number of nodes}}

    Parameters
    ----------
    instance : Knapsack
        A knapsack instance to evaluate.

    Returns
    -------
    float
        The feasibility ratio of the knapsack instance.

    Examples
    --------
    Compute the feasibility ratio for a knapsack instance:

    >>> from pykp.metrics import fsr
    >>> from pykp.knapsack import Item
    >>> from pykp.knapsack import Knapsack
    >>>
    >>> items = [
    ...     Item(value=1, weight=1),
    ...     Item(value=1, weight=1),
    ...     Item(value=1, weight=1),
    ... ]
    >>> capacity = 1
    >>> instance = Knapsack(items=items, capacity=capacity)
    >>> fsr(instance)
    0.5

    References
    ----------
    .. [#] Malan, Katherine M. "Landscape-Aware Constraint Handling Applied to
        Differential Evolution." International Conference on Theory and
        Practice of Natural Computing. 2018.
    """
    if not instance.graph:
        instance.initialise_graph()

    return len(instance.feasible_nodes) / len(instance.nodes)
