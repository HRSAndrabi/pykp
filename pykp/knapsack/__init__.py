"""Core classes for the knapsack problem.

.. currentmodule:: pykp.knapsack

PyKP ``knapsack`` provides classes to represent the knapsack problem and its
solutions. It includes classes to represent the knapsack problem, the items
to be packed, and the arrangement of items in the knapsack. It also provides
a sampler to generate random knapsack instances.

Classes
=======
.. autosummary::
   :toctree:

   Arrangement - Represents the arrangement of items in the knapsack.
   Item - Represents an item to be packed in the knapsack.
   Knapsack - Represents the knapsack problem.
"""

from ._arrangement import Arrangement
from ._item import Item
from ._knapsack import Knapsack

__all__ = ["Arrangement", "Item", "Knapsack"]
