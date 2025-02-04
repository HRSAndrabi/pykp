Computational Complexity Metrics
--------------------------------

PyKP provides metrics to evaluate the computational complexity of a knapsack instance. These metrics can be used to approximate the performance of different algorithms across instances. The full list of available metrics can be found in :doc:`/reference/generated/pykp.metrics`.

Sahni-k
^^^^^^^

The Sahni-k metric is a measure of complexity based on the approximation algorithm proposed by Sahni et al. (1975),\ [#]_ and shown to predict human performance on the 0/1 knapsack problem [#]_.
The metric is defined as the smallest subset of `k` items that must be selected so that applying the greedy algorithm to the remaining items yields an optimal solution.

For a given set of items and capacity constraint, you can calculate the Sahni-k metric for a knapsack instance using the following code:

.. code-block:: python

	from pykp.knapsack import Items
	from pykp import metrics

	items = [
	    Item(value=10, weight=5),
	    Item(value=15, weight=10),
	    Item(value=7, weight=3)
	]
	capacity = 15

	# Calculate the Sahni-k metric
	k = metrics.sahni_k(items, capacity)
	print("Sahni-k:", k)