Defining a Knapsack Instance
----------------------------------------

To solve a knapsack problem, initialise a ``Knapsack`` instance with the items and the capacity of the knapsack.

.. code-block:: python

   	from pykp import Knapsack, Item

	# Define a list of items
	items = [
	   Item(value=10, weight=5),
	   Item(value=15, weight=10),
	   Item(value=7, weight=3)
	]

	# Define knapsack capacity
   	capacity = 15

	# Initialise the Knapsack instance
	knapsack = Knapsack(items=items, capacity=capacity)
