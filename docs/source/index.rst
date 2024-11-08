PyKP 
==================

.. rst-class:: lead

   Sample, solve, and analyse instances of the 0-1 Knapsack Problem.

**PyKP** (py·kay·pee) is a Python package for defining, solving, and analysing knapsack problem instances. 
This package provides tools to set up knapsacks, and generate useful metrics and visualisations. 
Additionally, it includes a sampling feature that generates knapsack instances based on defined distributions.


Features
------------

* Define knapsack problem instances.
* Solve knapsack problems efficiently.
* Analyse computational complexity metrics.
* Randomly sample knapsack instances based on distribution parameters.
* Visualise knapsack instances and solutions.

Quick Start
-----------

Here's a quick example to get started with PyKP:

.. code-block:: python

   from pykp import Knapsack
   from pykp import Item

   # Define knapsack items
   items = [
       Item(value=10, weight=5),
       Item(value=15, weight=10),
       Item(value=7, weight=3)
   ]

   # Initialise and solve a knapsack problem
   capacity = 15
   knapsack = Knapsack(items=items, capacity=capacity)
   knapsack.solve()

   # Print the optimal solution
   print("Optimal solution value:", knapsack.optimal_nodes[0].value)


Explore
---------

.. toctree::
   :maxdepth: 2
   :caption: Documentation

   about/index
   installation/index
   usage/index
   pykp/index
   contributing/index
   changelog
