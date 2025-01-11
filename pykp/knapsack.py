"""
Provides an interface for defining instances of the 0-1 Knapsack
Problem.

Example:
    To define a Knapsack instance, initialise the `Knapsack` class with `Items`
    and a capacity constraint::

        from pykp import Knapsack
        from pykp import Item

        items = [
            Item(value=10, weight=5),
            Item(value=15, weight=10),
            Item(value=7, weight=3),
        ]
        capacity = 15
        knapsack = Knapsack(items=items, capacity=capacity)
        knapsack.solve()
        print(knapsack.optimal_nodes)

"""

import itertools
import json
import operator
from typing import Literal, Union
from warnings import warn

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
from anytree import Node, PreOrderIter

from .arrangement import Arrangement
from .item import Item
from .metrics import sahni_k
from .solvers import branch_and_bound, brute_force, mzn_gecode

SOLVERS = ["branch_and_bound", "mzn_gecode", "brute_force"]


class Knapsack:
    """
    Represents a knapsack problem solver.

    Parameters:
        items (list[Item]): An array of items for the knapsack
        problem.
        capacity (float): The capacity constraint of the knapsack.
        load_from_json (bool, optional): Whether to load the instance from
            a .json spec. Default is False.
        path_to_spec (str, optional): Path to json spec file. Default
            is None.
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
        """
        Sets the knapsack state using the provided binary array.

        Parameters:
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
        """
        Whether the knapsack is at full capacity, i.e placing in any item
        from the current set of excluded items would exceed the capacity.
        """
        return self._is_at_capacity

    @property
    def optimal_nodes(self) -> list[Arrangement]:
        """
        An array of optimal nodes in the knapsack. Optimal nodes are
        arrangements of items that maximise the total value of items in the
        knapsack, subject to the weight constraint. Optimal nodes are a subset
        of ``terminal_nodes``.
        """
        return list(self._optimal_nodes)

    @property
    def terminal_nodes(self) -> list[Arrangement]:
        """
        An array of terminal nodes in the knapsack. Terminal nodes are
        arrangements of items that are under the weight constraint, and at
        full capacity (no more items can be added without exceeding the
        capacity constraint). Terminal nodes are a subset of
        ``feasible_nodes``.
        """
        return list(self._terminal_nodes)

    @property
    def feasible_nodes(self) -> list[Arrangement]:
        """
        An array of feasible nodes in the knapsack. Feasible nodes are
        arrangements of items that are under the weight constraint.
        """
        return list(self._feasible_nodes)

    @property
    def nodes(self) -> list[Arrangement]:
        """An array of all nodes in the knapsack."""
        return list(self._nodes)

    def solve(
        self,
        method: Literal[
            "branch_and_bound", "mzn_gecode", "brute_force"
        ] = "branch_and_bound",
        solve_all_nodes: bool = False,
    ):
        """
        Solves the knapsack problem and returns optimal arrangements.

        Parameters:
            method (Literal["branch_and_bound", "mzn_gecode", "brute_force"],
                optional): The method to use to solve the knapsack problem.
                Default is "branch_and_bound".
            solve_all_nodes (bool, optional): Whether to find all nodes in the
                knapsack, including terminal nodes, and feasible nodes. Note,
                this method applies brute-force and may be infeasible for large
                instances. Default is False.

        Returns:
            np.ndarray: Optimal arrangements for the knapsack problem.
        """
        if method not in SOLVERS:
            raise ValueError(f"`method` must be one of: {SOLVERS}.")

        if solve_all_nodes:
            self.solve_all_nodes()
            return

        if method == "branch_and_bound":
            self._optimal_nodes = branch_and_bound(
                items=self._items, capacity=self._capacity
            )

        if method == "mzn_gecode":
            result = mzn_gecode(items=self._items, capacity=self._capacity)
            self._optimal_nodes = np.array([result])

        if method == "brute_force":
            if len(self._items) > 15:
                warn(
                    message="Brute force is infeasible for large instances.",
                    category=RuntimeWarning,
                    stacklevel=2,
                )
            (
                self._optimal_nodes,
                self._terminal_nodes,
                self._feasible_nodes,
                self._nodes,
            ) = brute_force(items=self._items, capacity=self._capacity)

        return self._optimal_nodes

    def add(self, item: Item):
        """
        Adds the specified item to the knapsack.

        Parameters:
            item (Item): The item to be added to the knapsack.

        Returns:
            np.ndarray: The updated knapsack state.
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
        return self._state

    def remove(self, item: Item):
        """
        Removes the specified item from the knapsack.

        Parameters:
            item (Item): The item to be removed from the knapsack.

        Returns:
            np.ndarray: The updated knapsack state.
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
        return self._state

    def empty(self):
        """
        Empties the knapsack by setting all items to be excluded.

        Returns:
            np.ndarray: The updated knapsack state.
        """
        self._state = np.zeros_like(self._items)
        self.__update_state()
        return self._state

    def __update_state(self):
        """
        Private method to update the knapsacks internal state.
        """
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

    def __calculate_value(self):
        """
        Calculates the total value of items currently in the knapsack.

        Returns:
            float: The total value of items in the knapsack.
        """
        mask = np.ma.make_mask(self._state, shrink=False)
        return sum([item.value for item in self._items[mask]])

    def __calculate_weight(self):
        """
        Calculates the total weight of items currently in the knapsack.

        Returns:
            float: The total weight of items in the knapsack.
        """
        mask = np.ma.make_mask(self._state, shrink=False)
        return sum([item.weight for item in self._items[mask]])

    def plot_terminal_nodes_histogram(self):
        """
        Plots a histogram of values for possible at-capacity arrangements.

        Returns:
                tuple[plt.Figure, plt.Axes]: Figure and Axes objects.
        """
        if not self._nodes.size == 2 ** len(self._items):
            self.solve(method="brute_force")

        fig, axes = plt.subplots(
            figsize=(8, 3), dpi=300, nrows=1, ncols=1, constrained_layout=True
        )

        axes.hist(
            [arrangement.value for arrangement in self._terminal_nodes],
            bins=100,
            color="#FF2C00",
            alpha=0.7,
        )
        axes.set_ylabel("Number of solutions")
        axes.set_xlabel("Solution value")
        plt.show()

        return fig, axes

    def __get_node_color(self, arrangement):
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
        fig=None,
        ax=None,
        show: bool = True,
    ):
        """
        Plots a network of knapsack nodes.

        Args:
            fig (plt.Figure, optional): Figure object. Default is None.
            ax (plt.Axes, optional): Axes object. Default is None.
            show (bool, optional): Whether to display the plot. Default
                is True.

        Returns:
            tuple[plt.Figure, plt.Axes]: Figure and Axes objects.
        """
        if not self._nodes.size == 2 ** len(self._items):
            self.solve_all_nodes()

        kp_network = kp_network = nx.DiGraph()

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

            kp_network.add_node(
                arrangement,
            )
            kp_network.add_edges_from(
                [
                    (arrangement, alt_arrangement)
                    for alt_arrangement in neighbours
                ]
            )

        if fig is None or ax is None:
            fig, ax = plt.subplots(
                figsize=(4 * len(self._items) / 10, 4 * len(self._items) / 10),
                dpi=1000,
                nrows=1,
                ncols=1,
                constrained_layout=True,
            )

        node_colors = [
            self.__get_node_color(arrangement)
            for arrangement in kp_network.nodes
        ]
        nx.draw_spring(
            kp_network,
            ax=ax,
            node_color=node_colors,
            node_size=2,
            width=0.05,
            arrowsize=0.01,
            with_labels=False,
        )
        if show:
            plt.show()
        return fig, ax

    def write_to_json(self, path: str):
        """
        Writes the knapsack instance to .json.

        Args:
            path (str): Filepath to output file.
        """
        if self._optimal_nodes.size == 0:
            self.solve()

        instance_spec = {
            "capacity": self._capacity,
            "sahni_k": sahni_k(self._optimal_nodes[0], self._capacity),
            "optimal_value": self._optimal_nodes[0].value,
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
        """
        Loads knapsack instance from a .json file.

        Args:
            path (str): Filepath to instance .json file.
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
        """
        Generates a summary of the knapsack instance.

        Returns:
            pd.DataFrame: Summary DataFrame.
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
        return repr(self.summary())
