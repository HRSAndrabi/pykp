class Item:
	"""
	Represents an item for the knapsack problem.

    Attributes:
    	value (int): The value of the item.
    	weight (int): The weight of the item.
	"""
	def __init__(self, value: int, weight: int):
		"""
		Initialises an Item instance.
		
		Args:
			value (int): The value of the item.
			weight (int): The weight of the item.
		"""
		self.weight = weight
		self.value = value
	
	def update_value(self, new_value: int):
		"""Updates the value of the item.

		Args:
			new_value (int): New value of the item. 
		"""
		self.value = new_value
	
	def update_weight(self, new_weight: int):
		"""Updates the weight of the item.

		Args:
			new_weight (int): New weight of the item. 
		"""
		self.weight = new_weight

	def __str__(self):
		return f"weight: {self.weight}; value: {self.value}"

	def __repr__(self):
		return str(self)