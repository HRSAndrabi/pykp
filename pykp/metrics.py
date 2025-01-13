"""Metrics for evaluating knapsack instance complexity.

This module provides metrics to evaluate the complexity and phase transition
properties of knapsack problem instances.
"""

import itertools
import time
from typing import Callable, Literal

import numpy as np
import pandas as pd
from tqdm import tqdm

from pykp.item import Item

from . import solvers
from .arrangement import Arrangement

SOLVERS = ["branch_and_bound", "mzn_gecode"]


def _initialise_grid(
    resolution: tuple[int, int],
) -> tuple[np.ndarray, np.ndarray]:
    """
    Create a 2D grid of normalised capacities and profits.

    This function sets up a mesh grid along the x-axis for normalised capacity
    and the y-axis for normalised profit.

    Parameters
    ----------
    resolution : tuple[int, int]
        The desired resolution of the grid in the form (num_capacities,
        num_profits).

    Returns
    -------
    grid : tuple[np.ndarray, np.ndarray]
        The mesh grid arrays representing normalised capacities and profits.
        The first array corresponds to normalised capacities, and the second
        to normalised profits.
    """
    norm_c_step_size = 1 / resolution[1]
    norm_p_step_size = 1 / resolution[0]

    grid = np.meshgrid(
        np.linspace(0, 1 - norm_c_step_size, resolution[1]),
        np.linspace(1 - norm_p_step_size, 0, resolution[0]),
    )

    return grid


def _sample_instance(
    num_items: int, norm_c: float, norm_p: float, rng: np.random.Generator
) -> tuple[list[Item], float, float]:
    """
    Sample a knapsack instance based on normalised capacity and profit targets.

    A set of `num_items` is generated with uniform random weights and values.
    The capacity is defined as the sum of all weights multiplied by `norm_c`,
    and the target profit is defined as the sum of all values multiplied by
    `norm_p`.

    Parameters
    ----------
    num_items : int
        Number of items to generate.
    norm_c : float
        Normalised capacity factor to scale the total weight.
    norm_p : float
        Normalised profit factor to scale the total value.
    rng : np.random.Generator
        Random number generator for sampling.

    Returns
    -------
    items : list[Item]
        The generated knapsack items with random weights and values.
    capacity : float
        The scaled capacity for the knapsack.
    target_profit : float
        The scaled target profit.
    """
    weights = rng.uniform(0.001, 1, num_items)
    profits = rng.uniform(0.001, 1, num_items)

    capacity = sum(weights) * norm_c
    target_profit = sum(profits) * norm_p

    items = [
        Item(value=profits[i], weight=weights[i]) for i in range(num_items)
    ]
    return items, capacity, target_profit


def _simulate_cell_solvability(
    norm_c_range: tuple[float, float],
    norm_p_range: tuple[float, float],
    outcome: Literal["solvability", "time"],
    num_items: int,
    samples: int,
    solver: Callable,
    rng: np.random.Generator,
    progress: tqdm,
) -> float:
    """Estimate the solvability of a grid cell.

    An instance is generated based on a random draw  within `norm_c_range` and
    `norm_p_range`. The instance is solved to check if the optimal solution
    meets or exceeds the target profit threshold. This process is repeated
    `samples` times to estimate the solvability of the cell.

    Parameters
    ----------
    norm_c_range : tuple[float, float]
        Lower and upper bound for the normalised capacity within the grid cell.
    norm_p_range : tuple[float, float]
        Lower and upper bound for the normalised profit within the grid cell.
    outcome : Literal["solvability", "time"], optional
        The outcome to measure in each cell.
    num_items : int
        Number of items to generate for each sample.
    samples : int
        Number of sampled instances in the given cell.
    solver : Callable
        A solver function that takes items and capacity as arguments and
        returns an optimal node or array of optimal nodes.
    rng : np.random.Generator
        Random number generator for sampling.
    progress : tqdm
        Progress bar for tracking iterations.

    Returns
    -------
    float
        The fraction of instances in the cell for which the solver found
        a solution that meets or exceeds the target profit.

    """
    score = 0
    for _ in range(samples):
        norm_c_draw = rng.uniform(norm_c_range[0], norm_c_range[1])
        norm_p_draw = rng.uniform(norm_p_range[0], norm_p_range[1])

        items, capacity, target_profit = _sample_instance(
            num_items=num_items,
            norm_c=norm_c_draw,
            norm_p=norm_p_draw,
            rng=rng,
        )
        start = time.perf_counter()
        result = solver(items=items, capacity=capacity, target=target_profit)
        end = time.perf_counter()

        if outcome == "time":
            score += end - start
        else:
            score += int(result)
        progress.update(1)

    return score / samples


def _save_phase_transition(
    phase_transition: np.ndarray,
    grid: tuple[np.ndarray, np.ndarray],
    path: str,
):
    """Save the phase transition matrix to a CSV file.

    Parameters
    ----------
    phase_transition : np.ndarray
        A 2D array representing the solvability at each grid cell.
    grid : tuple[np.ndarray, np.ndarray]
        The mesh grid of normalised capacities and profits. The first element
        should correspond to normalised capacities, and the second to
        normalised profits.
    path : str
        The path (including filename) for the output CSV file.

    """
    df = pd.DataFrame(
        {
            "nc_lower": grid[0].flatten(),
            "nc_upper": grid[0].flatten() + 1 / len(grid[0][0]),
            "np_lower": grid[1].flatten(),
            "np_upper": grid[1].flatten() + 1 / len(grid[1][0]),
            "solvability": phase_transition.flatten(),
        },
    )
    df.to_csv(path, index=False, float_format="%.6f")


def phase_transition(
    num_items: int,
    samples: int = 100,
    outcome: Literal["solvability", "time"] = "solvability",
    solver: str = "branch_and_bound",
    resolution: tuple[int, int] = (41, 41),
    seed: int | None = None,
    path: str = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Compute the phase transition matrix for knapsack instances.

    In computational problems, a phase transition refers to a phenomenon where
    the probability of finding a solution changes abruptly as some parameter
    crosses a critical threshold. This concept draws inspiration from physics,
    where phase transitions (e.g., water freezing) occur at critical
    thresholds. Such transitions have also been shown to arise in NP-complete
    problems, where the  likelihood of finding a solution changes
    abruptly as a key parameter crosses a critical value.

    For the knapsack problem, this phase transition manifests in terms of
    the relationship between the normalised capacity (`c`) and normalised
    profit (`p`) of an instance. The phase transition has been shown to occur
    when the ratio `r = c / p` is near 1. Instances with 0 < r < 1 are less
    expensive to solve as compred to instances with r ≈ 1.

    This function provide an implementation of the phase transition
    of the knapsack problem, based on Yadav, Nitin, et al. (2018).

    Parameters
    ----------
    num_items : int
        Number of items in each generated knapsack instance.
    samples : int, optional
        Number of instances to evaluate in each cell of the grid. Default is
        100.
    outcome : Literal["solvability", "time"], optional
        The outcome to measure in each cell. One of "solvability" or "time".
        If "solvability", the phase transition matrix will represent the
        the proprotion of isntances that are satisfiable in each cell. If
        "time", the phase transition matrix will represent the average time
        taken to solve isntances in each cell. Default is "solvability".

    Returns
    -------
        coordinate_matrices : tuple of np.ndarray
            The coordinate matrices for normalised capacities and normalised
            profits. The first matrix corresponds to normalised capacities,
            and the second to normalised profits.
        phase_transition : np.ndarray
            A 2D matrix of solvability (ranging from 0.0 to 1.0) corresponding
            to each cell in `grid`.

    Other Parameters
    ----------------
    solver : str, optional
        Which solver to use for evaluating each instance. Default is
        "branch_and_bound".
    resolution: tuple[int, int], optional
        Resolution of the normalised capacity-normalised profit grid.
        The first element corresponds to the resolution of normalised
        profit, and the second to the resolution of normalised capacity.
        Defaults to (41, 41).
    seed : int | None, optional
        Seed for sampling. Defaults to None.
    path str, optional:
        Path to save the phase transition to. Defaults
        to None.

    Examples
    --------
    >>> from pykp.metrics import phase_transition
    >>> grid, solvability_matrix = phase_transition(
    >>>     num_items=12,
    >>>     samples=1000,
    >>>     solver="branch_and_bound",
    >>>     resolution = (20, 20),
    >>> )
    >>> grid[0].shape, grid[1].shape, solvability_matrix.shape
    ((20, 20), (20, 20), (20, 20))

    >>> # Visualise the phase transition matrix
    >>> import matplotlib.pyplot as plt
    >>> fig, axes = plt.subplots(
    ...     nrows=1,
    ...     ncols=1,
    ...     dpi=200,
    ...     figsize=(4, 3),
    ...     tight_layout=True,
    ... )
    >>> image = axes.imshow(
    ...     phase_transition,
    ...     cmap="RdYlGn",
    ...     interpolation="nearest",
    ...     aspect="auto",
    ...     extent=(0, 1, 0, 1),
    ... )
    >>> axes.set(xlabel="nc", ylabel="np")
    >>> cbar = fig.colorbar(image, ax=axes)
    >>> cbar.ax.set_ylabel("solvability"
    >>> plt.show()

    .. image:: /_static/plots/phase_transition.png
        :alt: Phase transition matrix

    >>> # Optionally save results to file:
    >>> phase_transition(
    ...     num_items=10, samples=50, resolution=(5, 5), path="output.csv"
    ... )

    Notes
    -----
    The phase transition is typically applied with reference to the decision
    variant of the knapsack problem. To apply the phase transition to the
    optimisation variant, the target profit should be set to the optimal
    solution value of the instance. One can then compute the normalised
    profit based on the optimal solution, and observe where the instance
    lies in the phase transition matrix.

    References
    ----------

        .. [1] Yadav, Nitin, et al. "Phase transition in the knapsack problem."
           arXiv preprint arXiv:1806.10244 (2018).
    """
    match solver:
        case "branch_and_bound":
            solver = solvers._branch_and_bound_decision_variant
        case "mzn_gecode":
            solver = solvers._mzn_gecode_decision_variant
        case _:
            raise ValueError(f"`method` must be one of: {SOLVERS}.")

    grid = _initialise_grid(resolution)
    points = list(
        zip(
            [(p, p + 1 / resolution[0]) for p in grid[0].flatten()],
            [(p, p + 1 / resolution[1]) for p in grid[1].flatten()],
        )
    )
    rng = np.random.default_rng(seed)

    phase_transition = []
    with tqdm(total=samples * len(points)) as progress:
        for norm_c_range, norm_p_range in points:
            solvability = _simulate_cell_solvability(
                norm_c_range=norm_c_range,
                norm_p_range=norm_p_range,
                outcome=outcome,
                num_items=num_items,
                samples=samples,
                solver=solver,
                progress=progress,
                rng=rng,
            )
            phase_transition.append(solvability)

    phase_transition = np.array(phase_transition).reshape(resolution)

    if path:
        _save_phase_transition(phase_transition, grid, path)

    return grid, phase_transition


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
