"""Interface for defining instances of the 0-1 Knapsack Problem.

Knapsack instances are defined by a set of items, each with weights and values,
and a capacity constraint. The :class:`Knapsack` class provides methods to
solve instances using different algorithms, add or remove items, and visualise
the solution.

Examples
--------
To define a Knapsack instance, initialise the `Knapsack` class with `Items`
and a capacity constraint

>>> from pykp import Knapsack
>>> from pykp import Item
>>> items = [
...     Item(value=10, weight=5),
...     Item(value=15, weight=10),
...     Item(value=7, weight=3),
... ]
>>> capacity = 15
>>> knapsack = Knapsack(items=items, capacity=capacity)
>>> knapsack.solve()
>>> print(knapsack.optimal_nodes)
[(v: 25, w: 15, s: 3)]
"""

import json
from typing import Literal, Union
from warnings import warn

import matplotlib as mpl
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd

import pykp.solvers as solvers
from pykp.knapsack._arrangement import Arrangement
from pykp.knapsack._item import Item
from pykp.metrics._sahni_k import sahni_k

SOLVERS = ["branch_and_bound", "minizinc"]


class Knapsack:
    """Represents a knapsack problem solver.

    An instance is defined by a set of `items` and a `capacity` constraint.
    The `Knapsack` class provides methods to dynamically add or remove items,
    solve the knapsack problem using different algorithms, and visualise the
    solution.

    A knapsack instance can be initialised with a list of `Item` objects and a
    capacity constraint, or by providing a path to a valid JSON specification
    file.

    Parameters
    ----------
    items : list of Item, optional
        A list of `Item` objects, each representing a candidate for the
        knapsack with associated value and weight.
    capacity : float, optional
        The maximum total weight allowed in the knapsack.
    path : str, optional
        Path to a valid JSON specification file. Both `items` and `capacity`
        must be provided if `path` is not specified.

    Attributes
    ----------
    items : list of Item
        The items in the knapsack.
    capacity : float
        The capacity constraint of the knapsack.
    state : list of int
        A binary array indicating the inclusion/exclusion of items in the
        knapsack.
    value : float
        The total value of items currently in the knapsack.
    weight : float
        The total weight of items currently in the knapsack.
    is_feasible : bool
        Whether the knapsack is within its weight capacity.
    is_at_capacity : bool
        Whether the knapsack is at full capacity.
    optimal_nodes : list of Arrangement
        An array of optimal nodes in the knapsack. Optimal nodes are
        arrangements of items that maximise the total value of items in the
        knapsack, subject to the weight constraint. Optimal nodes are a subset
        of `terminal_nodes`. This attribute is populated after calling the
        `solve` method.
    terminal_nodes : list of Arrangement
        An array of terminal nodes in the knapsack. Terminal nodes are
        arrangements of items that are under the weight constraint, and at full
        capacity (no more items can be added without exceeding the capacity
        constraint). Terminal nodes are a subset of `feasible_nodes`. This
        attribute is populated after calling the `initialise_graph` method.
    feasible_nodes : list of Arrangement
        An array of feasible nodes in the knapsack. Feasible nodes are
        arrangements of items that are under the weight constraint. This
        attribute is populated after calling the `initialise_graph` method.
    nodes : list of Arrangement
        An array of all nodes in the knapsack. This attribute is populated
        after calling the `initialise_graph` method.
    graph : networkx.DiGraph
        A graph representation of the knapsack problem. This attribute is
        populated after calling the `initialise_graph` method.

    Examples
    --------
    Create a knapsack instance and solve using default settings:

    >>> from pykp import Knapsack
    >>> from pykp import Item
    >>> items = [
    ...     Item(value=10, weight=5),
    ...     Item(value=15, weight=10),
    ...     Item(value=7, weight=3),
    ... ]
    >>> capacity = 15
    >>> knapsack = Knapsack(items=items, capacity=capacity)
    >>> knapsack.solve()
    >>> print(knapsack.optimal_nodes)
    [(v: 25, w: 15, s: 3)]

    Solve the knapsack using the branch-and-bound method
    and explore the optimal nodes:

    >>> from knapsack_solver import Item, Knapsack
    >>> items = [
    ...     Item(value=10, weight=10),
    ...     Item(value=5, weight=5),
    ...     Item(value=5, weight=5),
    ... ]
    >>> knapsack = Knapsack(items=items, capacity=10)
    >>> knapsack.solve(method="branch_and_bound")
    >>> print(len(knapsack.optimal_nodes)
    2
    >>> for arrangement in knapsack.optimal_nodes:
    ...     print(
    ...         "Value:",
    ...         arrangement.value,
    ...         "Weight:",
    ...         arrangement.weight,
    ...         "State:",
    ...         arrangement.state,
    ...     )
    Value: 10 Weight: 10 State: [1.0 0.0 0.0]
    Value: 10 Weight: 10 State: [0.0 1.0 0.0]

    Save the knapsack instance to a JSON file:

    >>> knapsack.write_to_json("output.json")

    Load a knapsack instance from a JSON file:

    >>> knapsack = Knapsack(path="output.json")
    """

    def __init__(
        self,
        items: list[Item] = None,
        capacity: float = None,
        path: str = None,
    ):
        if path == None and (items is None or capacity is None):
            raise ValueError(
                "Either `items` and `capacity` must be provided, or `path`."
            )

        if path != None:
            with open(path) as f:
                spec = json.load(f)
                items = [
                    Item(item["value"], item["weight"])
                    for item in spec["items"]
                ]
                capacity = int(spec["capacity"])

        if len(items) == 0:
            raise ValueError("`items` must have length greater than 0.")
        if not np.all([isinstance(item, Item) for item in items]):
            raise ValueError("All elements in `items` must be of type `Item`.")
        if capacity < 0:
            raise ValueError("`capacity` must be non-negative.")
        if not isinstance(items, np.ndarray):
            items = np.array(items)

        self._items = np.array(
            sorted(
                items, key=lambda item: item.value / item.weight, reverse=True
            )
        )
        self._capacity = capacity
        self._state = np.zeros_like(items)
        self._value = 0
        self._weight = 0
        self._is_feasible = True
        self._is_at_capacity = False

        self.graph = None
        self._nodes = np.array([])
        self._feasible_nodes = np.array([])
        self._terminal_nodes = np.array([])
        self._optimal_nodes = np.array([])

    @property
    def items(self) -> list[Item]:
        return list(self._items)

    @property
    def capacity(self) -> float:
        return self._capacity

    @property
    def state(self) -> list[int]:
        return list(self._state)

    @state.setter
    def state(self, state: Union[list, np.ndarray]):
        if isinstance(state, list):
            state = np.array(state)
        self._state = state
        self.__update_state()

    @property
    def value(self) -> float:
        return self._value

    @property
    def weight(self) -> float:
        return self._weight

    @property
    def is_feasible(self) -> bool:
        return self._is_feasible

    @property
    def is_at_capacity(self) -> bool:
        return self._is_at_capacity

    @property
    def optimal_nodes(self) -> list[Arrangement]:
        return list(self._optimal_nodes)

    @property
    def terminal_nodes(self) -> list[Arrangement]:
        return list(self._terminal_nodes)

    @property
    def feasible_nodes(self) -> list[Arrangement]:
        return list(self._feasible_nodes)

    @property
    def nodes(self) -> list[Arrangement]:
        return list(self._nodes)

    def solve(
        self,
        method: Literal["branch_and_bound", "minizinc"] = "branch_and_bound",
        minizinc_solver: str = "coinbc",
    ):
        """Solves the knapsack problem to find optimal arrangements.

        Parameters
        ----------
        method : {"branch_and_bound", "minizinc"}, optional
            The algorithm to use for solving. Default is "branch_and_bound".

        Returns
        -------
        np.ndarray
            An array of `Arrangement` objects representing the optimal
            solutions.

        Other Parameters
        ----------------
        minizinc_solver: str, optional
            If ``method="minizinc"``, this argument specifies which minizinc
            solver to use. Default is "coinbc".

        Raises
        ------
        ValueError
            If the specified `method` is invalid.

        Examples
        --------
        >>> from pykp import Knapsack
        >>> from pykp import Item
        >>> items = [
        ...     Item(value=10, weight=5),
        ...     Item(value=15, weight=10),
        ...     Item(value=7, weight=3),
        ... ]
        >>> capacity = 15
        >>> knapsack = Knapsack(items=items, capacity=capacity)
        >>> knapsack.solve(method="branch_and_bound")
        >>> print(knapsack.optimal_nodes)
        [(v: 25, w: 15, s: 3)]
        """
        if method not in SOLVERS:
            raise ValueError(f"`method` must be one of: {SOLVERS}.")

        if method == "branch_and_bound":
            solution = solvers.branch_and_bound(
                items=self._items, capacity=self._capacity
            )

        if method == "minizinc":
            solution = solvers.minizinc(
                items=self._items,
                capacity=self._capacity,
                solver=minizinc_solver,
            )

        if isinstance(solution.value, list):
            self._optimal_nodes = solution.value
        else:
            self._optimal_nodes = [solution.value]

        return self.optimal_nodes

    def add(self, item: Item) -> list:
        """
        Includes a specific item in the knapsack.

        Parameters
        ----------
        item : Item
            The item to add. Must already exist among `self.items`.

        Returns
        -------
        list
            The updated binary state array after adding the item.

        Raises
        ------
        ValueError
            If `item` is not of type `Item` or if it is not present in
            `self.items`.

        Examples
        --------
        >>> items = [Item(10, 5), Item(15, 5)]
        >>> knapsack = Knapsack(
        >>>     items=items,
        ...     capacity=6
        ... )
        >>> knapsack.add(items[1])
        array([0, 1])
        >>> knapsack.value
        15
        >>> knapsack.weight
        5
        """
        if not isinstance(item, Item):
            raise ValueError("`item` must be of type `Item`.")
        if item not in self._items:
            raise ValueError(
                """`item` must be an existing `item` inside the `Knapsack`
                instance."""
            )
        self._state[np.where(self._items == item)[0][0]] = 1
        self.__update_state()
        return self.state

    def remove(self, item: Item) -> list:
        """
        Remove a specific item from the knapsack.

        Parameters
        ----------
        item : Item
            The item to remove. Must already exist among `self.items`.

        Returns
        -------
        list
            The updated binary state array after removing the item.

        Raises
        ------
        ValueError
            If `item` is not of type `Item` or if it is not present in
            `self.items`.

        Examples
        --------
        >>> items = [Item(10, 5), Item(15, 5)]
        >>> knapsack = Knapsack(
        >>>     items=items,
        ...     capacity=6
        ... )
        >>> knapsack.add(items[1])
        array([0, 1])
        >>> knapsack.remove(items[1])
        array([0, 0])
        >>> knapsack.value
        0
        >>> knapsack.weight
        0
        """
        if not isinstance(item, Item):
            raise ValueError("`item` must be of type `Item`.")
        if item not in self._items:
            raise ValueError(
                """`item` must be an existing `item` inside the `Knapsack`
                instance."""
            )

        self._state[np.where(self._items == item)] = 0
        self.__update_state()
        return self.state

    def empty(self):
        """Remove all items from the knapsack.

        Returns
        -------
        list
            The updated binary state array, all set to 0.

        Examples
        --------
        >>> knapsack = Knapsack(items=[Item(10, 2), Item(15, 4)], capacity=6)
        >>> knapsack.add(knapsack.items[0])
        array([1, 0])
        >>> knapsack.empty()
        array([0, 0])
        """
        self._state = np.zeros_like(self._items)
        self.__update_state()
        return self.state

    def __update_state(self):
        """Update the internal state of the knapsack."""
        self._value = self.__calculate_value()
        self._weight = self.__calculate_weight()
        self._is_feasible = self._capacity >= self._weight
        out_items = [
            self._items[i]
            for i, element in enumerate(self._state)
            if element == 0
        ]
        if sum(self._state) == len(self._state):
            self._is_at_capacity = True
        else:
            self._is_at_capacity = (
                min([self._weight + item.weight for item in out_items])
                > self._capacity
            )

    def __calculate_value(self) -> float:
        """Calculate the total value of items included in the current state.

        Returns
        -------
        float
            Sum of the values of included items.
        """
        mask = np.ma.make_mask(self._state, shrink=False)
        return sum([item.value for item in self._items[mask]])

    def __calculate_weight(self):
        """Calculate the total weight of items included in the current state.

        Returns
        -------
        float
            Sum of the weights of included items.
        """
        mask = np.ma.make_mask(self._state, shrink=False)
        return sum([item.weight for item in self._items[mask]])

    def initialise_graph(self):
        """Construct a graph representation of the knapsack problem.

        Each node in the graph represents a unique arrangement of items inside
        the knapsack. An edge represents an elementary operation of adding or
        removing a single item from the knapsack. Edges connect nodes whose
        differs by exactly one item.

        Returns
        -------
        networkx.DiGraph
            The graph representation of the knapsack problem.

        Examples
        --------
        >>> from pykp import Knapsack, Item
        >>> items = [Item(10, 5), Item(15, 10), Item(7, 3)]
        >>> knapsack = Knapsack(items=items, capacity=15)
        >>> knapsack.initialise_graph()
        <networkx.classes.digraph.DiGraph object at 0x...>
        """
        if len(self._items) > 15:
            warn(
                message="Brute force is infeasible for large instances.",
                category=RuntimeWarning,
                stacklevel=2,
            )

        solution = solvers.brute_force(
            items=self._items, capacity=self._capacity
        )
        self._optimal_nodes = solution.value["optimal"]
        self._terminal_nodes = solution.value["terminal"]
        self._feasible_nodes = solution.value["feasible"]
        self._nodes = solution.value["all"]

        graph = graph = nx.DiGraph()
        for arrangement in self._nodes:
            neighbours = [
                alt_arrangement
                for alt_arrangement in self._nodes
                if np.sum(
                    np.abs(
                        np.subtract(alt_arrangement.state, arrangement.state)
                    )
                )
                == 1
            ]

            graph.add_node(
                arrangement,
            )
            graph.add_edges_from(
                [
                    (arrangement, alt_arrangement)
                    for alt_arrangement in neighbours
                ]
            )

        self.graph = graph
        return graph

    def plot_terminal_node_hist(
        self, ax: plt.Axes = None
    ) -> tuple[plt.Figure, plt.Axes]:
        """Plot a histogram of terminal node values.

        All nodes are enumerated to find terminal nodes, and then plotted
        as a histogram. Terminal nodes are arrangements of items that are
        under the weight constraint, and at full capacity––that is, no more
        items can be added without exceeding the capacity constraint. Terminal
        nodes are a subset of ``feasible_nodes``.

        If the terminal nodes have not been enumerated, this method will first
        call `solve` with the `brute_force` method to find the terminal nodes.
        Note that this is infeasible for large n.

        Parameters
        ----------
        ax : matplotlib.pyplot.Axes, optional
            The axes object to plot the histogram. Defaults to None.

        Returns
        -------
        tuple of (matplotlib.pyplot.Figure, matplotlib.pyplot.Axes)
            The figure and axes objects of the resulting histogram.

        Examples
        --------
        >>> from pykp.knapsack import Sampler
        >>> import matplotlib.pyplot as plt
        >>>
        >>> sampler = Sampler(num_items=10, normalised_capacity=0.6)
        >>> sample = sampler.sample(seed=42)
        >>> fig, ax = sample.plot_terminal_nodes_histogram()
        >>> plt.show()

        .. image:: /_static/plots/terminal_nodes_hist.png
            :alt: Histogram of terminal node values
        """
        if not self.graph:
            self.initialise_graph()

        if not ax:
            fig, ax = plt.subplots(nrows=1, ncols=1, constrained_layout=True)

        ax.hist(
            [arrangement.value for arrangement in self._terminal_nodes],
            bins=100,
            alpha=1,
        )
        ax.set_ylabel("Number of terminal nodes")
        ax.set_xlabel("Value")

        return fig, ax

    def __get_node_color(self, arrangement: Arrangement, colour_map: dict):
        """Get the colour of a node in the network plot."""
        # Optimal node
        if arrangement.value == self._optimal_nodes[0].value:
            return colour_map["optimal"]

        # Feasible nodes
        if arrangement.weight < self._capacity:
            return colour_map["feasible"]

        # Infeasible nodes
        return colour_map["infeasible"]

    def plot_graph(
        self,
        ax: plt.Axes = None,
        colour_map: dict = None,
        show_legend: bool = True,
    ) -> tuple[plt.Figure, plt.Axes]:
        """
        Visualises a graph representation of the knapsack problem.

        Each node in the graph represents a unqiue arrangement of items inside
        the knapsack. Edges connect nodes whose states differ by a single
        item,  and represent the elementary operations of adding or removing a
        single item from the knapsack.

        Parameters
        ----------
        ax : matplotlib.pyplot.Axes, optional
            An existing axes object to plot on. Defaults to None.

        Returns
        -------
        tuple of (matplotlib.pyplot.Figure, matplotlib.pyplot.Axes)
            The figure and axes of the created or updated plot.

        Other Parameters
        ----------------
        colour_map : dict, optional
            A dictionary mapping node types to colours. A valid colour map
            must contain keys "optimal", "feasible", and "infeasible". Default
            is None.
        show_legend : bool, optional
            Whether to display a legend on the plot. Default is True.

        Examples
        --------
        >>> from pykp.knapsack import Sampler
        >>> import matplotlib.pyplot as plt
        >>>
        >>> sampler = Sampler(num_items=6, normalised_capacity=0.6)
        >>> sample = sampler.sample(seed=42)
        >>> fig, ax = sample.plot_graph()
        >>> plt.show()

        .. image:: /_static/plots/graph.png
            :alt: Knapsack graph representation
        """
        if not self.graph:
            self.initialise_graph()

        if ax is None:
            fig, ax = plt.subplots(
                figsize=(4 * len(self._items) / 10, 4 * len(self._items) / 10),
                dpi=200,
                nrows=1,
                ncols=1,
                constrained_layout=True,
            )

        if colour_map:
            for key in ["optimal", "feasible", "infeasible"]:
                if key not in colour_map:
                    raise ValueError(
                        f"Colour map must contain a key '{key}' for "
                        "{key} nodes."
                    )
        else:
            colour_map = {
                "optimal": "#57ff29",
                "feasible": "#003CAB",
                "infeasible": "#FF2C00",
            }

        node_colors = [
            self.__get_node_color(arrangement, colour_map=colour_map)
            for arrangement in self.graph.nodes
        ]
        nx.draw_spring(
            self.graph,
            ax=ax,
            node_color=node_colors,
            node_size=2,
            width=0.05,
            arrowsize=0.01,
            with_labels=False,
        )
        if show_legend:
            fig.legend(
                handles=[
                    mpl.lines.Line2D(
                        [0],
                        [0],
                        markerfacecolor=colour_map[key],
                        label=key,
                        linestyle="",
                        marker="o",
                        markersize=5,
                        markeredgewidth=0,
                    )
                    for key in colour_map.keys()
                ],
                frameon=False,
                loc="lower center",
                ncol=3,
                fontsize="8",
            )

        return fig, ax

    def write_to_json(self, path: str):
        """Write the knapsack configuration to a JSON file.

        The output file can be used to initialise the knapsack instance.

        Parameters
        ----------
        path : str
            The file path for the output JSON file.

        Examples
        --------
        >>> knapsack = Knapsack(items=[Item(10, 2), Item(20, 4)], capacity=6)
        >>> knapsack.solve()
        >>> knapsack.write_to_json("output.json")
        """
        instance_spec = {
            "capacity": self._capacity,
            "items": [
                {
                    "value": item.value,
                    "weight": item.weight,
                }
                for item in self._items
            ],
        }

        with open(path, "w") as f:
            json.dump(instance_spec, f, indent=4, default=int)

    def summary(self):
        """Return a DataFrame summarising the knapsack instance.

        Returns
        -------
        pandas.DataFrame
            A summary table describing the knapsack instance.

        Examples
        --------
        >>> knapsack = Knapsack(items=[Item(10, 2), Item(20, 4)], capacity=6)
        >>> knapsack.solve(method="brute_force")
        >>> df = knapsack.summary()
        >>> print(df)
        """
        n_terminal = 2 ** len(self._items)
        n_optimal = len(self._optimal_nodes)

        header = [
            f"C = {self._capacity}",
            f"nC = {
                round(
                    self._capacity
                    / np.sum([item.weight for item in self._items]),
                    2,
                )
            }",
            f"nTerminal = {n_terminal}",
            f"nOptimal = {n_optimal}",
        ]

        if len(self._terminal_nodes) > len(self._optimal_nodes):
            best_inferior_solution = self._terminal_nodes[
                len(self._optimal_nodes)
            ]
            delta = self._optimal_nodes[0].value - best_inferior_solution.value
            delta_pct = delta / self._optimal_nodes[0].value
            header.append(f"Δ = {delta}")
            header.append(f"Δ% = {delta_pct:.3}")
        else:
            best_inferior_solution = None

        header = ", ".join(header)

        columns = pd.MultiIndex.from_arrays(
            [
                [header] * len(self._items),
                [i + 1 for i, item in enumerate(self._items)],
            ]
        )

        rows = [
            [item.value for item in self._items],
            [item.weight for item in self._items],
            [round(item.value / item.weight, 3) for item in self._items],
        ]
        rows.extend(
            [
                np.where(arrangement.state == 1, "IN", "OUT")
                for arrangement in self._optimal_nodes
            ]
        )

        index = ["v", "w", "density"]
        index.extend(
            [
                ", ".join(
                    [
                        f"solution (v = {arrangement.value}",
                        f"w = {arrangement.weight}",
                        f"k = {sahni_k(arrangement, self._capacity)})",
                    ]
                )
                for arrangement in self._optimal_nodes
            ]
        )
        if best_inferior_solution is not None:
            index.append(
                ", ".join(
                    [
                        f"best inferior (v = {best_inferior_solution.value}",
                        f"w = {best_inferior_solution.weight}",
                        f"k = {
                            sahni_k(best_inferior_solution, self._capacity)
                        })",
                    ]
                )
            )
            rows.append(
                np.where(best_inferior_solution.state == 1, "IN", "OUT")
            )

        return pd.DataFrame(rows, columns=columns, index=index, dtype="object")

    def __str__(self):
        return (
            f"Knapsack(values={
                [round(item.value.item(), 2) for item in self._items]
            }, "
            f"weights={
                [round(item.weight.item(), 2) for item in self._items]
            }, "
            f"capacity={self._capacity})"
        )

    def __repr__(self):
        return f"Knapsack(items={self.items}, capacity={self._capacity})"
