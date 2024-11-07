# PyKP

PyKP is a free and open-source library for sampling and solving instances of the knapsack problem. It provides tools to define knapsack instances, solve them eficiently, and analyse computational complexity metrics. You can also use `pykp` to randomly sample knapsack problem instances based on specified distributions.

## Features

- Define knapsack problem instances with custom items, weights, and values.
- Solve knapsack instances using branch-and-bound and other methods.
- Compute optimal and feasible solutions for different knapsack configurations.
- Analyse computational complexity metrics.
- Generate synthetic knapsack instances with custom weight, density, and solution value ranges.

## Installation

PyKP support Python version 3.12 and higher. To install PyKP, run

```
pip install pykp
```

## Usage

### Defining and Solving a Knapsack Problem

To start, define a knapsack problem with a set of items and solve it using the Knapsack class.

```python
import numpy as np
from pykp import Knapsack
from pykp import Item

# Define items for the knapsack
items = np.array([
    Item(value=10, weight=5),
    Item(value=15, weight=10),
    Item(value=7, weight=3)
])

# Initialise a Knapsack instance
capacity = 15
knapsack = Knapsack(items=items, capacity=capacity)
knapsack.solve()

# Display the optimal solution
print("Optimal Solution Value:", knapsack.optimal_nodes[0].value)
```

### Generating Knapsack Instances with Sampler

The `Sampler` class allows you to generate knapsack instances based on specific ranges for item densities (value/weight ratio) and optimal solution values.

```python
from pykp import Sampler

# Initialise a Sampler instance with desired ranges
sampler = Sampler(
    num_items=5,
    normalised_capacity=0.6,
    density_range=(0.5, 1.5),
    solution_value_range=(100, 200)
)

# Generate a sampled knapsack instance
sampled_knapsack = sampler.sample()
print("Sampled Knapsack Capacity:", sampled_knapsack.capacity)
```

### Analysing Knapsack Solutions

The package provides methods to analyse the optimal solutions and other feasible arrangements.

```python
# Display a summary of the knapsack solutions
print(sampled_knapsack.summary())
```

## License

This project is licensed under the MIT License.

## Contributing

Contributions are welcome. Please fork the repository and submit a pull request.

## Contact

For questions or feedback, please reach out at hrs.andrabi@gmail.com.
