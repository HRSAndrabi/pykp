# CHANGELOG


## v2.0.0 (2025-01-05)

### Breaking

* feat(solvers): add minizinc gecode solver.

Add minizinc gecode solver class.

BREAKING CHANGE: knapsack.solve() is now an async method in order
to inferface with minizinc. ([`3b4027b`](https://github.com/HRSAndrabi/pykp/commit/3b4027b9bc56047f65d7b5217bfd8ffdb1e9b58a))

* refactor(knapsack.solve()): clean up branch and bound.

Move branch and bound solver to own module. Make use of
queue.PriorityQueue. Add __eq__ and __hash__ methods to Arrangement
class.

BREAKING CHANGE: new branch and bound solver introduces a new
argument to knapsack.solve() method. This method should now be
called with a `method` parameter that specifies the solver to use. ([`94cf4e6`](https://github.com/HRSAndrabi/pykp/commit/94cf4e6ac1c13798ff01fa4adfa8e5e79faab4d9))

### Bug Fixes

* fix(solvers): make return types consistent with docs.

Branch and bound solver should return a numpy array of optimal
solutions, but was returning a list instead. Similarly, minizinc
gecode solver was returning an nparray, but should instead return
a single arrangement since it is not robust to multiple solutions. ([`954e3e6`](https://github.com/HRSAndrabi/pykp/commit/954e3e64038ac671e6747ac506826fd01e8cd3d1))

* fix(item): allow id-based hashing. ([`056a10e`](https://github.com/HRSAndrabi/pykp/commit/056a10e1b242865b7ab79d3833e529f4d65c7736))

* fix(knapsack): density sort items on initialisation.

Branch and bound requires items to be density sorted. This created
a discrepancy between the order of items in the KP instance, and
the order of the items in the optimal arangement returned by the
branch and bound solver (which is assuming items are density
sorted. ([`14e0260`](https://github.com/HRSAndrabi/pykp/commit/14e02607b53f55e257bcd205a2450da62188a794))

* fix(branch_and_bound): return list instead of set.

Optimal nodes were converted to a set to remove duplicates, but
this creates issues with indexing through the optimal nodes array
stored in the Knapsack instances. Now converts to a set and then a
list. ([`065ce39`](https://github.com/HRSAndrabi/pykp/commit/065ce39c33ca89cc01c4c64141a14341b1ab2f26))

### Documentation

* docs(solvers): update documentation. ([`4bb25ac`](https://github.com/HRSAndrabi/pykp/commit/4bb25acae6f256669792d85bf4e1fbc9fd621cab))

* docs(knapsack): simplify knapsack.summary() docstring. ([`fe0a0d6`](https://github.com/HRSAndrabi/pykp/commit/fe0a0d69fd4bc202b1b9930a1d51fee8badb00f1))

### Features

* feat: add greedy solver. ([`a9b4213`](https://github.com/HRSAndrabi/pykp/commit/a9b42134319906951f1a618449ef7409f389348b))

### Refactoring

* refactor(solvers): implement solver abstract class. ([`782e9b4`](https://github.com/HRSAndrabi/pykp/commit/782e9b41570f4678643e235c3b56f5ee9eb6f756))

* refactor(item): convert to dataclass. ([`bee732f`](https://github.com/HRSAndrabi/pykp/commit/bee732fe69c1c9ab7079910099dd33a1d7a04cbb))

### Unknown

* Merge pull request #1 from HRSAndrabi/chore/clean-up-branch-and-bound

Chore/clean up branch and bound

- Create module for solvers
- Convert Item to data class
- Add minizinc geocode solver
- Add greedy solver
- Clean up branch and bound and refactor to own solver ([`ac89a18`](https://github.com/HRSAndrabi/pykp/commit/ac89a184ee2a4b932e2c93ff90afcf3ce3b6fa16))


## v1.2.0 (2024-11-18)

### Bug Fixes

* fix(knapsack): fix incorrectly suppressed deprecation warnings. ([`ca56656`](https://github.com/HRSAndrabi/pykp/commit/ca56656b126d3e61f6f278d0c1104d2c3317077c))

### Documentation

* docs: remove v prefix from version numbers. ([`c894c22`](https://github.com/HRSAndrabi/pykp/commit/c894c22f09612066825abfc3d0e5592754a51a6f))

### Features

* feat(knapsack.plot_network): add fig/ax optional arguments. ([`8f74c81`](https://github.com/HRSAndrabi/pykp/commit/8f74c81bac3acd775b462d5998290c7ce53d2083))

### Refactoring

* refactor(knapsack): remove unused variables. ([`d1d13ec`](https://github.com/HRSAndrabi/pykp/commit/d1d13ec09608aa72638aea53795fd199e176d9cf))


## v1.1.0 (2024-11-14)

### Bug Fixes

* fix(knapsack): check relevant nodes are solved before plotting.

Previous implementation would try to produce plots even if the relevant nodes had not been populated. This fix populates the nodes (if they don't already exist) and then produces the plot. ([`5f16162`](https://github.com/HRSAndrabi/pykp/commit/5f161622a1b34d7bd54966ac667f819bf69a41ef))

* fix(knapsack): reset node attributes when solving all nodes.

Fixes an issue where nodes were being duplicated when calling self.solve_all_nodes() multiple times in a row, or after self.solve(). ([`bfc7777`](https://github.com/HRSAndrabi/pykp/commit/bfc7777d974563e38db9c17ec7121400a8864ee6))

* fix(knapsack): removes scienceplots styling. ([`4851769`](https://github.com/HRSAndrabi/pykp/commit/485176904f14c47edba864eb5b3c84e92e7d0d07))

### Build System

* build: change version tag format to remove v prefix. ([`3f220a0`](https://github.com/HRSAndrabi/pykp/commit/3f220a06404f7d89b0295f8f65045c068ae5d6d4))

* build: delete unused workflow. ([`1e085ed`](https://github.com/HRSAndrabi/pykp/commit/1e085ed6de92b40135580b4ff260d236e6b139fa))

### Chores

* chore(knapsack): deletes unused variables. ([`9331641`](https://github.com/HRSAndrabi/pykp/commit/933164191b65f9300d3d5e354394aefcb4209d51))

### Documentation

* docs: import networkx. ([`eb634dc`](https://github.com/HRSAndrabi/pykp/commit/eb634dc0607f8371c3860be19ce54122b25a4f23))

### Features

* feat(knapsack): adds method for plotting network of knapsack instance. ([`7b4b7ea`](https://github.com/HRSAndrabi/pykp/commit/7b4b7eab6ebdbd2f48ac9efd98748df5bc924549))

### Performance Improvements

* perf(knapsack): move terminal/feasible node computation to solve_all_nodes().

Moved terminal and feasible node computation to `solve_all_nodes()`. Better for performance, as both methods applied brute-force and this now only happens once. Added deprecation warnings for `solve_terminal_nodes()` and `solve_feasible_nodes()`. ([`b590ef3`](https://github.com/HRSAndrabi/pykp/commit/b590ef3beb4b9034b93d91b5ab42ef82d13a44ab))

### Testing

* test(sampler): add tolerance for range checks.

Samples sometimes violated solution value/density ranges due to whole number rounding, causing tests to fail. This commit adds a tolerance parameter. Tests now ensure that the solution value/density is within the specified range + tolerance. ([`eb9b0ec`](https://github.com/HRSAndrabi/pykp/commit/eb9b0ec677e642d12ba2fede005fe975a92f17d4))

* test(knapsack): fix typo. ([`d89cf42`](https://github.com/HRSAndrabi/pykp/commit/d89cf422db70a6e3aa5c175625e7391359590e65))

* test(knapsack): remove np.array from initialisation. ([`7e2af96`](https://github.com/HRSAndrabi/pykp/commit/7e2af96a39dd7a6da16bc1f74f39f22e5e14640b))

* test(knapsack): check value of sahni-k in test. ([`b40fe8d`](https://github.com/HRSAndrabi/pykp/commit/b40fe8d7d2cd89aec3e46259a75457f98802575f))

* test(knapsack): fixed typo. ([`4b8e6c9`](https://github.com/HRSAndrabi/pykp/commit/4b8e6c963674fd6f8b6b72fe6173d6c59f54089d))

* test: added docstrings. ([`5f28e89`](https://github.com/HRSAndrabi/pykp/commit/5f28e897b7679d410ea1cca2fc7323e5db9e6915))


## v1.0.1 (2024-11-12)

### Bug Fixes

* fix(knapsack): don't solve second-best solution by default.

Fixed default argument `solve_second_best == False` to be consistent with the documentation. Refactored `summary()` to not try to print out second-best solution if it hasn't been generated. ([`94f72a2`](https://github.com/HRSAndrabi/pykp/commit/94f72a2723834cb8c931deb084fa9976ab15baf8))

### Build System

* build: update pyproject.toml for PSR. ([`648f124`](https://github.com/HRSAndrabi/pykp/commit/648f124ade38fb408abe6903588272131ea7397a))

* build: use latest version of pypi-publish. ([`ff651a0`](https://github.com/HRSAndrabi/pykp/commit/ff651a079db85ac0b43d0838446e0940647db4f5))

* build: add workflow for PSR.

Added workflow to bump version and create release on commit to main branch. ([`e6522ff`](https://github.com/HRSAndrabi/pykp/commit/e6522ff3760580b0fcaed5292c095b0593b2a517))

* build: add github-action to publish package. ([`85293f2`](https://github.com/HRSAndrabi/pykp/commit/85293f2fe0434c85360f1064e8d5cd6d3ca091a6))

### Unknown

* Relocate setup.py to pyproject.toml. ([`b611cc6`](https://github.com/HRSAndrabi/pykp/commit/b611cc612e303c4c2c1e288da4f8353cf19f5d59))

* Add pykp to requirements.txt. ([`22c2703`](https://github.com/HRSAndrabi/pykp/commit/22c27030c38316df7c36d1ad3276eb1e961ce730))

* Fix path to allow autodoc to work. ([`6d698af`](https://github.com/HRSAndrabi/pykp/commit/6d698afe34df43669b4206ad2912db0b7f655cb9))

* Fix typos. ([`2417fcf`](https://github.com/HRSAndrabi/pykp/commit/2417fcfe91a96b968c152c66fa46afcc9dc31439))

* Fix conf file path. ([`7208707`](https://github.com/HRSAndrabi/pykp/commit/7208707f883424da67e1b5c4ea94676e1a6bd3e1))

* Populate .readthedocs.yaml. ([`9f01ae4`](https://github.com/HRSAndrabi/pykp/commit/9f01ae476edfbd0d9c8a64609a0295084466340b))

* Add initial docs. ([`3928deb`](https://github.com/HRSAndrabi/pykp/commit/3928debaf40b6aa5f6cb9c96611baaf10cd36b63))

* Update doc-strings to confirm with Napolean (Google). ([`4a6e6a5`](https://github.com/HRSAndrabi/pykp/commit/4a6e6a5147887be87d67738f7a42ca5fe76a7bc2))

* Make docstrings comply to Google styleguide. ([`faea1bb`](https://github.com/HRSAndrabi/pykp/commit/faea1bb4f98ab1b327997418d590e1f6692ce1d1))

* Update readme.md. ([`7b8ff6c`](https://github.com/HRSAndrabi/pykp/commit/7b8ff6ce75cdf0321738aee2aae35dbda99354ed))

* Fix typo. ([`0083dc0`](https://github.com/HRSAndrabi/pykp/commit/0083dc02dd72c016a355afe367541fe09fad9b53))

* Add orcid. ([`1911531`](https://github.com/HRSAndrabi/pykp/commit/1911531779510994c462c4d86e23471f9148f26b))

* Update citation DOI. ([`f4f847f`](https://github.com/HRSAndrabi/pykp/commit/f4f847f5397e8238103cc46873fc01cf7ea72ff9))


## v1.0.0 (2024-11-07)

### Unknown

* Increment version 1.0.0. Add CITATION.cff. ([`0ae6939`](https://github.com/HRSAndrabi/pykp/commit/0ae693996d1da2ad450e97509558d5c9ec5b64fd))

* Increment version. ([`b8e4934`](https://github.com/HRSAndrabi/pykp/commit/b8e4934917d3e8b1e1130d9b9b4c2a6427ea0063))

* Remove unused class. ([`f92d66d`](https://github.com/HRSAndrabi/pykp/commit/f92d66d88a4ce8a3586d0ce6e00e3b6b32579ddd))

* Add docstring to __init__.py. ([`262730d`](https://github.com/HRSAndrabi/pykp/commit/262730d1becd5c778761cb424f1928d0ddc1b694))

* Add license. ([`0ddebab`](https://github.com/HRSAndrabi/pykp/commit/0ddebab21978579fa4bddc847e22ba8c19526b7e))

* Add docstring for  method. ([`ef92f00`](https://github.com/HRSAndrabi/pykp/commit/ef92f001f2ab258c1d28bef0e3661c6b3ea4b861))

* Update classifiers. ([`a0963f0`](https://github.com/HRSAndrabi/pykp/commit/a0963f02e929a2c14da54f5e508d23acbbe2bd2b))

* Increment version. ([`4b297b6`](https://github.com/HRSAndrabi/pykp/commit/4b297b6218b13c5513886f6b702f026cc50da95b))

* Change items to ndarray where list is given. ([`41a65de`](https://github.com/HRSAndrabi/pykp/commit/41a65ded73f00c36c38763bdb9990658cbae86c4))

* Increment version. ([`da7bf30`](https://github.com/HRSAndrabi/pykp/commit/da7bf308156e1d0d299a2b382a095860883fa77c))

* Delete test notebook. ([`7e31938`](https://github.com/HRSAndrabi/pykp/commit/7e31938a086a725b7eb6fd8e643f5882a486b481))

* Update README.md. ([`79a2126`](https://github.com/HRSAndrabi/pykp/commit/79a21269207abd3296e5e9dde88e3ed75ff9a1d3))

* Removed unused import. ([`46c5230`](https://github.com/HRSAndrabi/pykp/commit/46c52303910d5fc558f5138be113631fa9ae696d))

* Ensure package directory is correctly recognised. ([`f68cc71`](https://github.com/HRSAndrabi/pykp/commit/f68cc71b8d20a117839443ff4b6ec135fdd124db))

* Clean up knapsack and sampler classes.

- Removed redundant arguments.
- Removed redundant imports. ([`eb18095`](https://github.com/HRSAndrabi/pykp/commit/eb18095be018ef2a7d0d077a66aabb8cfdf5059d))

* Remove `optimise_solution_delta()`.

Removed algorithm to increase difference between optimal and second-best solution because it will probably never be used. ([`2f6e51f`](https://github.com/HRSAndrabi/pykp/commit/2f6e51f809d703d5880bfd7907471a8c7ca3b28a))

* Removed weight range from sampler. Wrote tests.

Removed `weight_range` parameter from sampler. Sampler now samples weights from U[100, 1000], and then scales to the drawn solution value. Implemented basic tests to cover sampler. ([`df2fa72`](https://github.com/HRSAndrabi/pykp/commit/df2fa727d2e6de4f4a080d364aa8b0538a34275e))

* Initial commit.

Intial commit to port over from KME24 project. ([`f4e8769`](https://github.com/HRSAndrabi/pykp/commit/f4e8769039d8139cccd2847e0e03eef15cdbc2fa))
