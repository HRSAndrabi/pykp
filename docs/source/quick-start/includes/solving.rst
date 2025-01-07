Solving a Knapsack Instance
----------------------------------------

Once initialised, you can solve the knapsack instance using the ``solve`` method, which finds the optimal arrangement of items.

.. code-block:: python

   # Solve for the optimal solution
   knapsack.solve()

   # Print the optimal solution's value
   print("Optimal solution value:", knapsack.optimal_nodes[0].value)


The `solve` method offers additional options to identify non-optimal nodes. 

* ``solve_terminal_nodes``: Set to ``true`` to compute all terminal nodes.
* ``solve_feasible_nodes``: Set to ``true`` to find all feasible nodes.
* ``solve_second_best``: Set to ``true`` to also find the second-best solution.

.. note::
	Depending on the size of the instance, specifying these options can be computationally expensive.

Example:

.. code-block:: python

   	# Solve with additional options
   	knapsack.solve(
	   solve_terminal_nodes=True, 
	   solve_feasible_nodes=True, 
	   solve_second_best=True
	)