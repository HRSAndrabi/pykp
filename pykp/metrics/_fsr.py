from pykp.knapsack import Knapsack


def fsr(instance: Knapsack) -> float:
    r"""Calculate the feasibility ratio of a knapsack instance.

    The feasibility ratio is the ratio of the number of feasible nodes in the
    search space to the total number of nodes in the search
    space. Feasibility is determined by the capacity constraint of the
    knapsack.

    .. math::

        FSR = \\frac{\\text{Number of feasible nodes}}
        {\\text{Total number of nodes}}

    Parameters
    ----------
    instance : Knapsack
        A knapsack instance to evaluate.
    """
    if not instance.graph:
        instance.initialise_graph()

    return len(instance.feasible_nodes) / len(instance.nodes)
