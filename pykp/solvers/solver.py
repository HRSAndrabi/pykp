"""
This module contains the abstract base class for solvers of the knapsack problem.
"""

from abc import ABC, abstractmethod
import numpy as np 
from ..arrangement import Arrangement
from ..item import Item

class Solver(ABC):
	"""
	Represents an abstract base class for solvers of the knapsack problem.
	"""

	@staticmethod
	@abstractmethod
	async def solve(
		self,
		items: np.ndarray[Item],
		capacity: int
	) -> Arrangement:
		pass