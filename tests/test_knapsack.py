import unittest
import numpy as np
from pykp import Item, Knapsack, Arrangement

# run all tests: python -m unittest -v

class TestKnapsack(unittest.TestCase):
    def setUp(self):
        """
        Initialise some items for testing
        """
        self.items = [
            Item(value=10, weight=5),
            Item(value=15, weight=10),
            Item(value=7, weight=3),
            Item(value=12, weight=7),
        ]
        self.capacity = 23
        self.knapsack = Knapsack(items=self.items, capacity=self.capacity)

    def test_initialisation(self):
        """
        Test if knapsack initialises correctly
        """
        self.assertEqual(self.knapsack.capacity, 23)
        self.assertTrue(np.array_equal(self.knapsack.state, np.zeros(len(self.items))))
        self.assertEqual(self.knapsack.value, 0)
        self.assertEqual(self.knapsack.weight, 0)
        self.assertTrue(self.knapsack.is_feasible)

    def test_invalid_initialisation(self):
        """
        Test if invalid initialisations raise appropriate errors
        """
        with self.assertRaises(ValueError):
            Knapsack(items=np.array([]), capacity=10)

        with self.assertRaises(ValueError):
            Knapsack(items="not an array", capacity=10)

        with self.assertRaises(ValueError):
            Knapsack(items=np.array([1, 2, 3]), capacity=-5)

    def test_add_item(self):
        """
        Add an item and check if state, value, and weight are updated
        """
        self.knapsack.empty()
        self.knapsack.add(self.knapsack.items[0])
        self.assertEqual(self.knapsack.value, 10)
        self.assertEqual(self.knapsack.weight, 5)
        self.assertTrue(self.knapsack.is_feasible)
        self.assertTrue(np.array_equal(self.knapsack.state, [1, 0, 0, 0]))

    def test_remove_item(self):
        """
        Remove an item and check if state, value, and weight are updated
        """
        self.knapsack.empty()
        self.knapsack.add(self.items[0])
        self.knapsack.remove(self.items[0])
        self.assertEqual(self.knapsack.value, 0)
        self.assertEqual(self.knapsack.weight, 0)
        self.assertTrue(np.array_equal(self.knapsack.state, [0, 0, 0, 0]))

    def test_set_state(self):
        """
        Set a custom state and verify the updates
        """
        self.knapsack.set_state(np.array([1, 1, 0, 0]))
        self.assertEqual(self.knapsack.value, 25)
        self.assertEqual(self.knapsack.weight, 15)
        self.assertTrue(self.knapsack.is_feasible)
        self.assertTrue(np.array_equal(self.knapsack.state, [1, 1, 0, 0]))

    def test_empty_knapsack(self):
        """
        Empty the knapsack and check the state
        """
        self.knapsack.add(self.items[0])
        self.knapsack.empty()
        self.assertEqual(self.knapsack.value, 0)
        self.assertEqual(self.knapsack.weight, 0)
        self.assertTrue(np.array_equal(self.knapsack.state, [0, 0, 0, 0]))

    def test_calculate_sahni_k(self):
        """
        Test Sahni-k calculation
        """
        self.knapsack.solve()
        optimal = self.knapsack.optimal_nodes[0]
        sahni_k = self.knapsack.calculate_sahni_k(optimal)
        self.assertIsInstance(sahni_k, int)
        self.assertEqual(sahni_k, 3)

    def test_load_from_json(self):
        """
        Test loading from a JSON file (assumes you have a sample file)
        """
        self.knapsack.write_to_json("./tests/scratch/test_knapsack.json")
        new_knapsack = Knapsack(
            items=self.items,
            capacity=self.capacity,
            load_from_json=True,
            path_to_spec="./tests/scratch/test_knapsack.json"
        )
        self.assertEqual(new_knapsack.capacity, self.capacity)
        self.assertEqual(len(new_knapsack.items), len(self.items))


if __name__ == '__main__':
    unittest.main()
