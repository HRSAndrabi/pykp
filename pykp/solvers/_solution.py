from dataclasses import dataclass
from enum import Enum

from pykp.knapsack._arrangement import Arrangement


class SolutionType(Enum):
    """Types of solutions that can be returned by a solver."""

    MAXIMISE = "maximise"
    APPROXIMATE = "approximate"
    SATISFY = "satisfy"
    MAXIMISE_TOP_N = "maximise_top_n"
    TRAVERSAL = "traversal"


@dataclass(frozen=True)
class SolutionStatistics:
    """Statistics about the solution returned by a solver.

    Parameters
    ----------
    time : float
        Time taken by the solver to find the solution.
    n_solutions : int
        Number of solutions found by the solver.
    """

    time: float
    n_solutions: int


@dataclass(frozen=True)
class Solution:
    """Represents a solution returned by a solver.

    Parameters
    ----------
    value: bool | Arrangement | list[Arrangement]
        The arrangement of items in the solution.
    type: SolutionType
        The type of the solution.
    statistics: SolutionStatistics
        Statistics about the algorithm to obtain the solution.

    See Also
    --------
    SolutionType : Types of solutions that can be returned by a solver.
    SolutionStatistics : Statistics about the solution returned by a solver.
    """

    value: bool | Arrangement | list[Arrangement]
    type: SolutionType
    statistics: SolutionStatistics
