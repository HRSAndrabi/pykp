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
from typing import Literal
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

    Attributes:
        items (np.ndarray[Item]): An array of items available for the knapsack
            problem.
        capacity (int): The maximum weight capacity of the knapsack.
        state (np.ndarray): Binary array indicating the inclusion/exclusion of
            items in the knapsack.
        value (float): The total value of items currently in the knapsack.
        weight (float): The total weight of items currently in the knapsack.
        is_feasible (bool): Indicates if the knapsack is within its weight
            capacity.
        is_at_capacity (bool): Indicates if the knapsack is at full capacity.
        terminal_nodes (np.ndarray[Arrangement]): An array of all possible
            arrangements of items that are under the weight constraint, and at
            full capacity
        optimal_nodes (np.ndarray[Arrangement]): An array of optimal solutions
            to the knapsack problem.
    """

    def __init__(
        self,
        items: np.ndarray[Item],
        capacity: int,
        load_from_json: bool = False,
        path_to_spec: str = None,
    ):
        """
        Initialises a Knapsack instance.

        Parameters:
            items (np.ndarray[Item]): An array of items for the knapsack
            problem.
            capacity (int): The maximum weight capacity of the knapsack.
            load_from_json (bool, optional): Whether to load the instance from
                a .json spec. Default is False.
            path_to_spec (str, optional): Path to json spec file. Default
                is None.
        """

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

        self.items = np.array(
            sorted(
                items, key=lambda item: item.value / item.weight, reverse=True
            )
        )
        self.capacity = capacity
        self.state = np.zeros_like(items)
        self.value = 0
        self.weight = 0
        self.is_feasible = True
        self.is_at_capacity = False

        self.nodes = np.array([])
        self.feasible_nodes = np.array([])
        self.terminal_nodes = np.array([])
        self.optimal_nodes = np.array([])

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
            self.optimal_nodes = branch_and_bound(
                items=self.items, capacity=self.capacity
            )

        if method == "mzn_gecode":
            result = mzn_gecode(items=self.items, capacity=self.capacity)
            self.optimal_nodes = np.array([result])

        if method == "brute_force":
            if len(self.items) > 15:
                warn(
                    message="Brute force is infeasible for large instances.",
                    category=RuntimeWarning,
                    stacklevel=2,
                )
            (
                self.optimal_nodes,
                self.terminal_nodes,
                self.feasible_nodes,
                self.nodes,
            ) = brute_force(items=self.items, capacity=self.capacity)

        return self.optimal_nodes

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
        if item not in self.items:
            raise ValueError(
                """`item` must be an existing `item` inside the `Knapsack`
                instance."""
            )
        self.state[np.where(self.items == item)[0][0]] = 1
        self.__update_state()
        return self.state

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
        if item not in self.items:
            raise ValueError(
                """`item` must be an existing `item` inside the `Knapsack`
                instance."""
            )

        self.state[np.where(self.items == item)] = 0
        self.__update_state()
        return self.state

    def set_state(self, state: np.ndarray):
        """
        Sets the knapsack state using the provided binary array.

        Parameters:
            state (np.ndarray): Binary array indicating the inclusion/exclusion
                of items in the knapsack.

        Returns:
            np.ndarray: The updated knapsack state.
        """
        self.state = state
        self.__update_state()
        return self.state

    def empty(self):
        """
        Empties the knapsack by setting all items to be excluded.

        Returns:
            np.ndarray: The updated knapsack state.
        """
        self.state = np.zeros_like(self.items)
        self.__update_state()
        return self.state

    def __update_state(self):
        """
        Private method to update the knapsacks internal state.
        """
        self.value = self.__calculate_value()
        self.weight = self.__calculate_weight()
        self.is_feasible = self.capacity >= self.weight
        out_items = [
            self.items[i]
            for i, element in enumerate(self.state)
            if element == 0
        ]
        if sum(self.state) == len(self.state):
            self.is_at_capacity = True
        else:
            self.is_at_capacity = (
                min([self.weight + item.weight for item in out_items])
                > self.capacity
            )

    def __calculate_value(self):
        """
        Calculates the total value of items currently in the knapsack.

        Returns:
            float: The total value of items in the knapsack.
        """
        mask = np.ma.make_mask(self.state, shrink=False)
        return sum([item.value for item in self.items[mask]])

    def __calculate_weight(self):
        """
        Calculates the total weight of items currently in the knapsack.

        Returns:
            float: The total weight of items in the knapsack.
        """
        mask = np.ma.make_mask(self.state, shrink=False)
        return sum([item.weight for item in self.items[mask]])

    def plot_terminal_nodes_histogram(self) -> tuple[plt.Figure, plt.Axes]:
        """
        Plots a histogram of values for possible at-capacity arrangements.

        Returns:
                tuple[plt.Figure, plt.Axes]: Figure and Axes objects.
        """
        if not self.nodes.size == 2 ** len(self.items):
            self.solve(method="brute_force")

        fig, axes = plt.subplots(
            figsize=(8, 3), dpi=300, nrows=1, ncols=1, constrained_layout=True
        )

        axes.hist(
            [arrangement.value for arrangement in self.terminal_nodes],
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
        if arrangement.value == self.optimal_nodes[0].value:
            return "#57ff29"

        # Feasible nodes
        if arrangement.weight < self.capacity:
            return "#003CAB"

        # Infeasible nodes
        return "#FF2C00"

    def plot_network(
        self,
        fig: plt.Figure = None,
        ax: plt.Axes = None,
        show: bool = False,
    ) -> tuple[plt.Figure, plt.Axes]:
        """
        Plots a network of knapsack nodes.

        Paramaters:
            fig (plt.Figure, optional): Figure object. Default is None.
            ax (plt.Axes, optional): Axes object. Default is None.
            show (bool, optional): Whether to display the plot. Default
                is False.

        Returns:
            tuple[plt.Figure, plt.Axes]: Figure and Axes objects.
        """
        if not self.nodes.size == 2 ** len(self.items):
            self.solve_all_nodes()

        kp_network = kp_network = nx.DiGraph()

        for arrangement in self.nodes:
            neighbours = [
                alt_arrangement
                for alt_arrangement in self.nodes
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
                figsize=(4 * len(self.items) / 10, 4 * len(self.items) / 10),
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
        if self.optimal_nodes.size == 0:
            self.solve()

        instance_spec = {
            "capacity": self.capacity,
            "sahni_k": sahni_k(self.optimal_nodes[0], self.capacity),
            "optimal_value": self.optimal_nodes[0].value,
            "items": [
                {
                    "id": i,
                    "value": item.value,
                    "weight": item.weight,
                }
                for i, item in enumerate(self.items)
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
        n_terminal = 2 ** len(self.items)
        n_optimal = len(self.optimal_nodes)

        header = [
            f"C = {self.capacity}",
            f"nC = {
                round(
                    self.capacity
                    / np.sum([item.weight for item in self.items]),
                    2,
                )
            }",
            f"nTerminal = {n_terminal}",
            f"nOptimal = {n_optimal}",
        ]

        if len(self.terminal_nodes) > len(self.optimal_nodes):
            best_inferior_solution = self.terminal_nodes[
                len(self.optimal_nodes)
            ]
            delta = self.optimal_nodes[0].value - best_inferior_solution.value
            delta_pct = delta / self.optimal_nodes[0].value
            header.append(f"Δ = {delta}")
            header.append(f"Δ% = {delta_pct:.3}")
        else:
            best_inferior_solution = None

        header = ", ".join(header)

        columns = pd.MultiIndex.from_arrays(
            [
                [header] * len(self.items),
                [i + 1 for i, item in enumerate(self.items)],
            ]
        )

        rows = [
            [item.value for item in self.items],
            [item.weight for item in self.items],
            [round(item.value / item.weight, 3) for item in self.items],
        ]
        rows.extend(
            [
                np.where(arrangement.state == 1, "IN", "OUT")
                for arrangement in self.optimal_nodes
            ]
        )

        index = ["v", "w", "density"]
        index.extend(
            [
                ", ".join(
                    [
                        f"solution (v = {arrangement.value}",
                        f"w = {arrangement.weight}",
                        f"k = {sahni_k(arrangement, self.capacity)})",
                    ]
                )
                for arrangement in self.optimal_nodes
            ]
        )
        if best_inferior_solution is not None:
            index.append(
                ", ".join(
                    [
                        f"best inferior (v = {best_inferior_solution.value}",
                        f"w = {best_inferior_solution.weight}",
                        f"k = {
                            sahni_k(best_inferior_solution, self.capacity)
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
