import unittest
import numpy as np
from pykp import Knapsack, Item, Sampler

class TestSampler(unittest.TestCase):

    def setUp(self):
        # Initialise parameters for sampler
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
        # Verify that the sampler initialises correctly with provided parameters
        self.assertEqual(self.sampler.num_items, self.num_items)
        self.assertEqual(self.sampler.normalised_capacity, self.normalised_capacity)
        self.assertEqual(self.sampler.density_range, self.density_range)
        self.assertEqual(self.sampler.solution_value_range, self.solution_value_range)

    def test_sample_items_count(self):
        # Verify that the sampled knapsack has the correct number of items
        for sample in self.samples:
            self.assertEqual(len(sample.items), self.num_items)

    def test_sampled_item_density_range(self):
        # Check that the density of each item falls within the specified density range
        for sample in self.samples:
            densities = [item.value / item.weight for item in sample.items]
            self.assertTrue(all(self.density_range[0] <= d <= self.density_range[1] for d in densities))

    def test_sample_capacity(self):
        # Verify that the sampled knapsack capacity is approximately equal to the specified normalized capacity
        for sample in self.samples:
            sum_weights = np.sum([item.weight for item in sample.items])
            self.assertAlmostEqual(sample.capacity / sum_weights, self.normalised_capacity, delta=0.05)

    def test_solution_value_within_range(self):
        # Ensure that the solution value of the knapsack is within the specified solution value range
        for sample in self.samples:
            solution_value = sample.optimal_nodes[0].value
            self.assertTrue(self.solution_value_range[0] <= solution_value <= self.solution_value_range[1])

if __name__ == '__main__':
    unittest.main()

