"""Random knapsack instance generator.

.. currentmodule:: pykp.sampling

The `sampling` namespace provides an interface to sample random knapsack
instances. The entry point is the :class:`Sampler` class, which allows users to
generate random knapsack instances based on specified distributions.

Classes
=======
.. autosummary::
   :toctree:

   Sampler - Generates random knapsack instances.
"""

from ._sampler import Sampler

__all__ = ["Sampler"]
