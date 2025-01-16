from typing import Callable

import numpy as np
import pandas as pd
from tqdm import tqdm

from pykp import solvers
from pykp.knapsack._item import Item

SOLVERS = ["branch_and_bound", "minizinc"]


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
    num_items: int,
    samples: int,
    solver: tuple[Callable, dict],
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
    num_items : int
        Number of items to generate for each sample.
    samples : int
        Number of sampled instances in the given cell.
    solver : tuple[Callable, dict]
        A tuple of a solver function, and a dictionary of keyword arguments to
        provide to that function.
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
    total_solved = 0
    solver, solver_kwargs = solver
    for _ in range(samples):
        norm_c_draw = rng.uniform(norm_c_range[0], norm_c_range[1])
        norm_p_draw = rng.uniform(norm_p_range[0], norm_p_range[1])

        items, capacity, target_profit = _sample_instance(
            num_items=num_items,
            norm_c=norm_c_draw,
            norm_p=norm_p_draw,
            rng=rng,
        )
        result = solver(
            items=items,
            capacity=capacity,
            target=target_profit,
            **solver_kwargs,
        )

        total_solved += int(result.value)
        progress.update(1)

    return (total_solved / samples, result.statistics.time / samples)


def _save_phase_transition(
    solvability: np.ndarray,
    time: np.ndarray,
    outcome: str,
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
    outcome : str
        The outcome to save to the CSV file. One of "solvability", "time", or
        "both".
    path : str
        The path (including filename) for the output CSV file.

    """
    data = {
        "nc_lower": grid[0].flatten(),
        "nc_upper": grid[0].flatten() + 1 / len(grid[0][0]),
        "np_lower": grid[1].flatten(),
        "np_upper": grid[1].flatten() + 1 / len(grid[1][0]),
    }

    if outcome == "solvability":
        data["solvability"] = solvability.flatten()
    elif outcome == "time":
        data["time"] = time.flatten()
    else:
        data["solvability"] = solvability.flatten()
        data["time"] = time.flatten()
    df = pd.DataFrame(data)
    df.to_csv(path, index=False, float_format="%.6f")


def phase_transition(
    num_items: int,
    samples: int = 100,
    outcome: str = "both",
    solver: str = "branch_and_bound",
    minizinc_solver: str = "coinbc",
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
    outcome : str, optional
        The outcome to measure in each cell. One or of "solvability" "time"
        or "both". If "solvability" is specified, the phase transition matrix
        represents the proprotion of instances that are satisfiable in each
        cell. If "time" is specified, the phase transition matrix represents
        the average time taken to solve instances in each cell. If "both" is
        specified, the returned phase transition is a tuple with the
        the solvability matrix as the first element, and the time matrix as the
        second element. Default is "both".

    Returns
    -------
        coordinate_matrices : tuple of np.ndarray
            The coordinate matrices for normalised capacities and normalised
            profits. The first matrix corresponds to normalised capacities,
            and the second to normalised profits.
        phase_transition : np.ndarray
            If ``outcome="solvability"``, a 2D matrix where each cell
            represents the proportion of instances that are satisfiable. If
            ``outcome="time"``, a 2D matrix where each cell represents the
            average time taken to solve instances. If ``outcome="both``, a
            tuple containing both matrices.

    Other Parameters
    ----------------
    solver : str, optional
        Which solver to use for evaluating each instance. Default is
        "branch_and_bound".
    minizinc_solver: str, optional
        If ``solver="minizinc"``, this argument specifies which minizinc solver
        to use. Default is "coinbc".
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
    >>> grid, (solvability, time) = phase_transition(
    >>>     num_items=12,
    >>>     samples=1000,
    >>>     outcome="both",
    >>>     solver="branch_and_bound",
    >>>     resolution = (20, 20),
    >>> )
    >>> grid[0].shape, grid[1].shape, solvability.shape, time.shape
    ((20, 20), (20, 20), (20, 20), (20, 20))

    Visualise the phase transition matrices using matplotlib:

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

    .. image:: /_static/plots/phase_transition_solvability.png
        :alt: Phase transition solvability matrix

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

    .. image:: /_static/plots/phase_transition_time.png
        :alt: Phase transition time matrix

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
    if outcome not in ["solvability", "time", "both"]:
        raise ValueError(
            "`outcome` must one of 'solvability', 'time', or 'both'."
        )

    match solver:
        case "branch_and_bound":
            solver = (solvers._branch_and_bound_decision_variant, {})
        case "minizinc":
            solver = (
                solvers._minizinc_decision_variant,
                {"solver": minizinc_solver},
            )
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

    phase_transition_solvability = []
    phase_transition_time = []
    with tqdm(total=samples * len(points)) as progress:
        for norm_c_range, norm_p_range in points:
            solvability, time = _simulate_cell_solvability(
                norm_c_range=norm_c_range,
                norm_p_range=norm_p_range,
                num_items=num_items,
                samples=samples,
                solver=solver,
                progress=progress,
                rng=rng,
            )
            phase_transition_solvability.append(solvability)
            phase_transition_time.append(time)

    phase_transition_solvability = np.array(
        phase_transition_solvability
    ).reshape(resolution)
    phase_transition_time = np.array(phase_transition_time).reshape(resolution)

    if path:
        _save_phase_transition(
            solvability=phase_transition_solvability,
            time=phase_transition_time,
            outcome=outcome,
            grid=grid,
            path=path,
        )

    if outcome == "solvability":
        result = phase_transition_solvability
    elif outcome == "time":
        result = phase_transition_time
    else:
        result = (phase_transition_solvability, phase_transition_time)

    return grid, result
