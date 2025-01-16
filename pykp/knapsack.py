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

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd

from .arrangement import Arrangement
from .item import Item
from .metrics import sahni_k
from .solvers import branch_and_bound, brute_force, minizinc

SOLVERS = ["branch_and_bound", "minizinc"]


class Knapsack:
    """Represents a knapsack problem solver.

    An instance is defined by a set of `items` and a `capacity` constraint.
    The `Knapsack` class provides methods to dynamically add or remove items,
    solve the knapsack problem using different algorithms, and visualise the
    solution.

    Parameters
    ----------
    items : list of Item
        A list of `Item` objects, each representing a candidate for the
        knapsack with associated value and weight.
    capacity : float
        The maximum total weight allowed in the knapsack.
    load_from_json : bool, optional
        Whether to load the items and capacity from a JSON file. If set to
        True, `path_to_spec` must be provided. Default is False.
    path_to_spec : str, optional
        Path to the JSON specification file containing an array of items
        (`value`, `weight`) and the knapsack capacity. Only used if
        `load_from_json` is True. Default is None.

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

    See Also
    --------
    pykp.item : Represents an item with value and weight attributes.
    pykp.solvers : Module containing solvers for the knapsack problem.
    """

    def __init__(
        self,
        items: list[Item],
        capacity: float,
        load_from_json: bool = False,
        path_to_spec: str = None,
    ):
        if load_from_json:
            self.load_from_json(path_to_spec)
            return

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
        """The items in the knapsack."""
        return list(self._items)

    @property
    def capacity(self) -> float:
        """The capacity constraint of the knapsack."""
        return self._capacity

    @property
    def state(self) -> list[int]:
        """The binary array indicating the inclusion/exclusion of items."""
        return list(self._state)

    @state.setter
    def state(self, state: Union[list, np.ndarray]):
        """Set the knapsack state using the provided binary array.

        Parameters
        ----------
            state (list or np.ndarry): Binary array indicating the
                inclusion/exclusion of items in the knapsack.
        """
        if isinstance(state, list):
            state = np.array(state)
        self._state = state
        self.__update_state()

    @property
    def value(self) -> float:
        """The total value of items currently in the knapsack."""
        return self._value

    @property
    def weight(self) -> float:
        """The total weight of items currently in the knapsack."""
        return self._weight

    @property
    def is_feasible(self) -> bool:
        """Whether the knapsack is within its weight capacity."""
        return self._is_feasible

    @property
    def is_at_capacity(self) -> bool:
        """Whether the knapsack is at full capacity.

        A knapsack is at full capacity when placing in any item
        from the current set of excluded items would cause the sum of
        weights to exceed the capacity constraint.
        """
        return self._is_at_capacity

    @property
    def optimal_nodes(self) -> list[Arrangement]:
        """An array of optimal nodes in the knapsack.

        Optimal nodes are arrangements of items that maximise the total value
        of items in the knapsack, subject to the weight constraint.
        Optimal nodes are a subset of ``terminal_nodes``.
        """
        return list(self._optimal_nodes)

    @property
    def terminal_nodes(self) -> list[Arrangement]:
        """An array of terminal nodes in the knapsack.

        Terminal nodes are arrangements of items that are under the weight
        constraint, and at full capacity (no more items can be added without
        exceeding the capacity constraint). Terminal nodes are a subset of
        ``feasible_nodes``.
        """
        return list(self._terminal_nodes)

    @property
    def feasible_nodes(self) -> list[Arrangement]:
        """An array of feasible nodes in the knapsack.

        Feasible nodes are arrangements of items that are under the weight
        constraint.
        """
        return list(self._feasible_nodes)

    @property
    def nodes(self) -> list[Arrangement]:
        """An array of all nodes in the knapsack."""
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
            solution = branch_and_bound(
                items=self._items, capacity=self._capacity
            )

        if method == "minizinc":
            solution = minizinc(
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

        solution = brute_force(items=self._items, capacity=self._capacity)
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

    def plot_terminal_nodes_histogram(
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
        >>> import random
        >>> from pykp import Item, Knapsack
        >>> import matplotlib.pyplot as plt
        >>>
        >>> random.seed(42)
        >>> weights = [random.randint(1, 100) for _ in range(12)]
        >>> values = [random.randint(1, 100) for _ in range(12)]
        >>> items = [Item(v, w) for v, w in zip(values, weights)]
        >>> capacity = sum(weights) / 2
        >>> knapsack = Knapsack(items=items, capacity=capacity)
        >>> knapsack.solve(method="brute_force")
        [(v: 372, w: 300, s: 4000)]
        >>> fig, ax = knapsack.plot_terminal_nodes_histogram()
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

    def __get_node_color(self, arrangement):
        """Get the colour of a node in the network plot."""
        # Optimal node
        if arrangement.value == self._optimal_nodes[0].value:
            return "#57ff29"

        # Feasible nodes
        if arrangement.weight < self._capacity:
            return "#003CAB"

        # Infeasible nodes
        return "#FF2C00"

    def plot_network(
        self,
        ax: plt.Axes = None,
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

        Examples
        --------
        >>> import random
        >>> from pykp import Item, Knapsack
        >>> import matplotlib.pyplot as plt
        >>>
        >>> random.seed(42)
        >>> weights = [random.randint(1, 100) for _ in range(5)]
        >>> values = [random.randint(1, 100) for _ in range(5)]
        >>> items = [Item(v, w) for v, w in zip(values, weights)]
        >>> capacity = sum(weights) / 2
        >>> knapsack = Knapsack(items=items, capacity=capacity)
        >>> knapsack.solve(method="brute_force")
        [(v: 142, w: 114, s: 28)]
        >>> fig, ax = knapsack.plot_network()
        >>> plt.show()

        .. image:: /_static/plots/network.png
            :alt: Knapsack network representation
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

        node_colors = [
            self.__get_node_color(arrangement)
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

        return fig, ax

    def write_to_json(self, path: str):
        """Write the knapsack configuration to a JSON file.

        The output file can be used to load the knapsack instance at a later
        time using the `load_from_json` method.

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
                    "id": i,
                    "value": item.value,
                    "weight": item.weight,
                }
                for i, item in enumerate(self._items)
            ],
        }

        with open(path, "w") as f:
            json.dump(instance_spec, f, indent=4, default=int)

    def load_from_json(self, path: str):
        """Load a knapsack configuration from a JSON file.

        Parameters
        ----------
        path : str
            The file path of the JSON specification.

        Examples
        --------
        >>> knapsack = Knapsack(
        ...     items=[],
        ...     capacity=0,
        ...     load_from_json=True,
        ...     path_to_spec="knapsack_config.json",
        ... )
        """
        with open(path) as f:
            spec = json.load(f)
            self.__init__(
                items=np.array(
                    [
                        Item(item["value"], item["weight"])
                        for item in spec["items"]
                    ]
                ),
                capacity=int(spec["capacity"]),
            )

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
        """Return a string representation of the knapsack instance."""
        return repr(self.summary())
