Solving a Knapsack Instance
----------------------------------------

Once initialised, you can solve the knapsack instance using the ``solve`` method, which finds the optimal arrangement of items.

.. code-block:: python

   # Solve for the optimal solution
   knapsack.solve()

   # Print the optimal solution's value
   print("Optimal solution value:", knapsack.optimal_nodes[0].value)


The ``solve()`` method accepts an optional ``method`` parameter to specify the solver used to solve the instance. Some of these solvers are heuristic solvers, and others are exact solvers.
By default, the solver is set to ``branch_and_bound``. The full list of available solvers can be found in :doc:`/reference/generated/pykp.solvers`

.. note::
	Depending on the size of the instance, specifying certain solvers can be computationally expensive.