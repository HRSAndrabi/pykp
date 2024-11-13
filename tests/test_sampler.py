import unittest
import numpy as np
from pykp import Knapsack, Item, Sampler

class TestSampler(unittest.TestCase):

    def setUp(self):
        """
        Initialise the sampler with some parameters
        """
        self.epsilon = 0.025
        self.num_items = 7
        self.normalised_capacity = 0.6
        self.density_range = (0.5, 1.5)
        self.solution_value_range = (1000, 1700)
        self.sampler = Sampler(
            num_items=self.num_items,
            normalised_capacity=self.normalised_capacity,
            density_range=self.density_range,
            solution_value_range=self.solution_value_range,
        )
        self.samples = []
        for _ in range(50):
            self.samples.append(self.sampler.sample())

    def test_initialisation(self):
        """
        Test if the sampler initialises correctly
        """
        self.assertEqual(self.sampler.num_items, self.num_items)
        self.assertEqual(self.sampler.normalised_capacity, self.normalised_capacity)
        self.assertEqual(self.sampler.density_range, self.density_range)
        self.assertEqual(self.sampler.solution_value_range, self.solution_value_range)

    def test_sample_items_count(self):
        """
        Test if the sampled knapsack has the correct number of items
        """
        for sample in self.samples:
            self.assertEqual(len(sample.items), self.num_items)

    def test_sampled_item_density_range(self):
        """
        Test if the density of each item falls within the specified density range
        """
        lower_bound = self.density_range[0] * (1 - self.epsilon)
        upper_bound = self.density_range[1] * (1 + self.epsilon)
        for sample in self.samples:
            densities = [item.value / item.weight for item in sample.items]
            self.assertTrue(all(lower_bound <= d <= upper_bound for d in densities))

    def test_sample_capacity(self):
        """
        Verify that the sampled knapsack capacity is approximately equal to the specified normalized capacity
        """
        for sample in self.samples:
            sum_weights = np.sum([item.weight for item in sample.items])
            self.assertAlmostEqual(sample.capacity / sum_weights, self.normalised_capacity, delta=self.epsilon)

    def test_solution_value_within_range(self):
        """
        Ensure that the solution value of the knapsack is within the specified solution value range
        """
        lower_bound = self.solution_value_range[0] * (1 - self.epsilon)
        upper_bound = self.solution_value_range[1] * (1 + self.epsilon)
        for sample in self.samples:
            solution_value = sample.optimal_nodes[0].value
            self.assertTrue(lower_bound <= solution_value <= upper_bound)

if __name__ == '__main__':
    unittest.main()

