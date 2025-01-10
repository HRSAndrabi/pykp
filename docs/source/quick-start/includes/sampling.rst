Sampling Random Knapsack Instances
------------------------------------

PyKP includes a :doc:`Sampler </reference/generated/pykp.sampler.Sampler>` class to generate random knapsack problem instances. 

.. code-block:: python

   from pykp.sampler import Sampler

   # Define parameters for the sampler
   sampler = Sampler(
       num_items=5,
       normalised_capacity=0.6,
   )

   # Generate a sampled knapsack instance
   sampled_knapsack = sampler.sample()
   print("Sampled knapsack items:", sampled_knapsack.items)

Item weights and values are sampled from a uniform distribution by default, but you can customise these distributions by specifying optional parameters to the sampler. The example below defines normal distributions with mean 100 and standard deviation 10 for both weights and values:

.. code-block:: python

   # Define custom distribution parameters
    sampler = Sampler(
        num_items=10,
        normalised_capacity=0.5,
        weight_dist=(
            np.random.default_rng().normal,
            {"loc": 100, "scale": 10},
        ),
        value_dist=(
            np.random.default_rng().normal,
            {"loc": 100, "scale": 10},
        ),
    )

   # Generate a sampled knapsack instance
   sampled_knapsack = sampler.sample()
   print("Sampled knapsack items:", sampled_knapsack.items)

