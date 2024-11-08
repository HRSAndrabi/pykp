Sampling Random Knapsack Instances
------------------------------------

PyKP includes a ``Sampler`` class to generate random knapsack problem instances based on defined ranges for densities (item value to weight ratios), and solution values. 

.. code-block:: python

   from pykp.sampler import Sampler

   # Define parameters for the sampler
   sampler = Sampler(
       num_items=5,
       normalised_capacity=0.6,
       density_range=(0.5, 1.5),
       solution_value_range=(100, 200)
   )

   # Generate a sampled knapsack instance
   sampled_knapsack = sampler.sample()
   print("Sampled knapsack capacity:", sampled_knapsack.capacity)
