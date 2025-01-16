"""Implementations of various solvers for the knapsack problem.

.. currentmodule:: pykp.solvers

PyKP ``solvers`` provides various solvers for knapsack problem. It provides
access to knapsack-specific branch-and-bound algorithms, as well as
well-known general-purpose constraint-modelling algorithms, like Gecode
and Coin-OR Branch-and-cut.

Common functions and objects, shared across different solvers, are:

.. autosummary::
   :toctree:

   Solution - Represents the solution to a knapsack problem instance.
   SolutionStatistics - Statistics about the solution returned by a solver.
   SolutionType - Types of solutions that can be returned by a solver.

Exact Algorithms
================

.. autosummary::
   :toctree:

   branch_and_bound - Branch-and-bound algorithm for the knapsack problem.
   minizinc - MiniZinc solver for the knapsack problem.

Approximation Algorithms
========================

.. autosummary::
   :toctree:

   greedy - Greedy algorithm for the knapsack problem.
"""

from ._branch_and_bound import (
    _branch_and_bound_decision_variant,
    branch_and_bound,
)
from ._brute_force import brute_force
from ._greedy import greedy
from ._minizinc import _minizinc_decision_variant, minizinc
from ._solution import *
