from pykp.knapsack import Knapsack


def fbp(instance: Knapsack) -> float:
    r"""Compute the feasibility boundary proportion for a knapsack problem.

    The feasibility boundary proportion is the ratio of the number of edges
    between feasible and infeasible nodes in the search space to the total
    number of edges in the search space. This is a generalisation of the
    ratio of feasible boundary crossings (RFBx) fitness landscape metric. [#]_
    Feasibility is determined by the capacity constraint of the knapsack.

    .. math::

        FBP = \frac
        {\sum_{(u, v) \in E} \mathcal{I}_{f(u) \neq f(v)}}
        {|E|},

    where :math:`E` is the set of edges in the search space, :math:`f(u)` is
    the feasibility of node :math:`u`, and :math:`\mathcal{I}` is the
    indicator function.

    Parameters
    ----------
    instance : Knapsack
        A knapsack instance to evaluate.

    Returns
    -------
    float
        The feasibility boundary proportion of the knapsack instance.

    Examples
    --------
    Compute the feasibility boundary proportion for a knapsack instance:

    >>> from pykp.metrics import fbp
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
    >>> fbp(instance)
    0.75

    References
    ----------
    .. [#] Malan, Katherine M. "Landscape-Aware Constraint Handling Applied to
        Differential Evolution." International Conference on Theory and
        Practice of Natural Computing. 2018.
    """
    if not instance.graph:
        instance.initialise_graph()

    feasibility_boundary_crossings = [
        (u, v)
        for u, v in instance.graph.edges()
        if (u.weight > instance.capacity) != (v.weight > instance.capacity)
    ]

    return len(feasibility_boundary_crossings) / len(instance.graph.edges())
