*******
About 
*******

.. rst-class:: lead

   Sample, solve, and analyse instances of the 0-1 Knapsack Problem.

**PyKP** (py·kay·pee) is a Python package for defining, solving, and analysing knapsack problem instances. 
The package provides tools to define (or randomly sample) knapsack instances, and generate useful metrics and visualisations. 

I created this package as part of a research project. You can learn about me and my other projects by visiting my `personal website`_.


Features
------------

* Define and solve knapsack problem instances.
* Analyse computational complexity metrics.
* Randomly sample knapsack instances based on distribution parameters.
* Visualise knapsack instances and solutions.

Quick Start
-----------

Here's a quick example to get started with PyKP:

.. code-block:: python

   from pykp.knapsack import Knapsack
   from pykp.knapsack import Item

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


Versioning 
----------
PyKP follows the `Semantic Versioning standard`_. 

License
-------

PyKP is open-source software, licensed under the MIT License. See the LICENSE file on `GitHub`_ for details.

.. _GitHub: https://github.com/HRSAndrabi/pykp
.. _knapsack problem: https://en.wikipedia.org/wiki/Knapsack_problem
.. _personal website: https://hassan.andra.bi
.. _Semantic Versioning standard: https://semver.org/