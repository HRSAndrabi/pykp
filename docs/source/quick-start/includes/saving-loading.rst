Saving and Loading Configurations
---------------------------------

You can save and load knapsack configurations in JSON format.

.. code-block:: python

   	# Save the current knapsack configuration to a JSON file
   	knapsack.write_to_json("knapsack_config.json")

   	# Load a knapsack configuration from a JSON file
   	new_knapsack = Knapsack(
	   items=[], 
	   capacity=0, 
	   load_from_json=True, 
	   path_to_spec="knapsack_config.json"
  	)
