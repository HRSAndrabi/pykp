# CHANGELOG


## v3.2.0 (2025-01-12)

### Chores

* chore: remove outdated comment. ([`6c8df81`](https://github.com/HRSAndrabi/pykp/commit/6c8df8120e0d9b5ff233b32f1843ea31ab0d4a0d))

### Features

* feat:  to accept random seed. ([`b43e5a6`](https://github.com/HRSAndrabi/pykp/commit/b43e5a67b754a9949fb61b119319a842f8865036))

### Testing

* test(phase_transition): check reproducibility. ([`247fe2a`](https://github.com/HRSAndrabi/pykp/commit/247fe2affa3e1e74b13bebb7a8da8c017cea329f))


## v3.1.3 (2025-01-12)

### Bug Fixes

* fix(phase_transition): dimensions back to front.

The final `phase_transition` array was being reshaped in a manner
that was inconsistent with the way in which  resolution was passed
to the function. The expected outcome should be to reshape the
phase transition in such a way that nc varies along the x-axis
(column-wise) and np along the y-axis (row-wise). ([`e8fbcfc`](https://github.com/HRSAndrabi/pykp/commit/e8fbcfc8ce83be33787b64a17321e637b3ba562d))


## v3.1.2 (2025-01-12)

### Bug Fixes

* fix: not converting type to list. ([`85d783a`](https://github.com/HRSAndrabi/pykp/commit/85d783a6e89ee4c4693fd3cfbf741e6c773d741c))

### Documentation

* docs: add test module docstrings. ([`c99e6e3`](https://github.com/HRSAndrabi/pykp/commit/c99e6e3153617c497ba9ce9302b7d8195e100063))

### Testing

* test: remove mzn_gecode test. ([`eee83d8`](https://github.com/HRSAndrabi/pykp/commit/eee83d848b0e9abf0c5c1b03d75fea02b0bbdd66))

* test(metrics.phase_transition): write tests. ([`71a8016`](https://github.com/HRSAndrabi/pykp/commit/71a80165cfb2fc5b50d025078c5598dc752e178b))


## v3.1.1 (2025-01-12)

### Bug Fixes

* fix: broken installation link. ([`020b86d`](https://github.com/HRSAndrabi/pykp/commit/020b86d8833f8bf08e239fd0f50270bbf3793e1d))

* fix: remove anytree dependency. ([`328e98b`](https://github.com/HRSAndrabi/pykp/commit/328e98bea9914167246dddad1dc306acc251974d))

### Chores

* chore: remove unused imports. ([`0251b89`](https://github.com/HRSAndrabi/pykp/commit/0251b89633b440d0d6757f24be5cc077cb26b895))

### Code Style

* style: consistent logo. ([`6bb266a`](https://github.com/HRSAndrabi/pykp/commit/6bb266a1156be2572ef855d7d811ce33b1808ca0))

### Documentation

* docs: update README.md. ([`62f7406`](https://github.com/HRSAndrabi/pykp/commit/62f74062de9ad239694585216c612858a5e3ed7a))

* docs: add matplotlib to dependencies. ([`a5d62d1`](https://github.com/HRSAndrabi/pykp/commit/a5d62d1b6d7b0c2741c779441acd7f218062b562))


## v3.1.0 (2025-01-12)

### Bug Fixes

* fix: remove reference to missing .size attribute. ([`a7f950d`](https://github.com/HRSAndrabi/pykp/commit/a7f950d93469cb6c562d5fc853085c081f21cc98))

* fix(Knapsack.plot_network): fix incorrect default for `ax`. ([`37b109f`](https://github.com/HRSAndrabi/pykp/commit/37b109f1a0d0e62d45e2a13ce4114d518576e4d5))

* fix: remove reference to missing .size attribute. ([`528868c`](https://github.com/HRSAndrabi/pykp/commit/528868c1d74b3837b549d5a31a3514622de33221))

* fix: store optimal nodes as list not np.ndarray. ([`dcff89f`](https://github.com/HRSAndrabi/pykp/commit/dcff89f2d0aa9b289792cbc27b99e255b7750e9e))

* fix(arrangement): internal state should be np.array. ([`1b932b2`](https://github.com/HRSAndrabi/pykp/commit/1b932b28509b01a05f7d9cd9b71687437f727033))

### Build System

* build: add matplotlib to doc. ([`e70c379`](https://github.com/HRSAndrabi/pykp/commit/e70c3795ba1b3f57532ac5d651e5f36794962ea0))

* build: add venv* pattern. ([`90d82be`](https://github.com/HRSAndrabi/pykp/commit/90d82be77888fd941df916c08ece0f80589be2d9))

* build: add missing docs dependency. ([`5572c4c`](https://github.com/HRSAndrabi/pykp/commit/5572c4c1bdf7bfd05faf1f1324b9e074b5ef68f3))

* build: add numpy and tqdm to doc deps.

These packages are imported in pykp, and thus required to render
documentation. The previous solution was to use `MagicMock` to do
a mock import, but this messed with the rendering of type hints
in the documentation. Listing numpy and tqdm as 'doc' dependencies
rectifies this issue. ([`d836764`](https://github.com/HRSAndrabi/pykp/commit/d836764c25b30ce6334b5d9c9baf0b02dd6a5fd2))

### Chores

* chore: remove redundant requirements.txt. ([`4c78cec`](https://github.com/HRSAndrabi/pykp/commit/4c78cecbb64f25a4bd1a7412c0517de811f23682))

* chore: clean up and comment sphinx conf. ([`a03e88c`](https://github.com/HRSAndrabi/pykp/commit/a03e88cf908626e18bc8fe07aee677dcfca710d0))

* chore: remove test notebook. ([`84b0ef8`](https://github.com/HRSAndrabi/pykp/commit/84b0ef8bb3e54093770ce5aed037497e3ef9591e))

### Code Style

* style: fix lint errors. ([`db90708`](https://github.com/HRSAndrabi/pykp/commit/db90708317fe7576e5294b485b1a0cbba4ead792))

* style: rename ambigious _save function. ([`e9bf8df`](https://github.com/HRSAndrabi/pykp/commit/e9bf8dfc6507d9c7a1f02338b3d9c47a1698e3a6))

### Continuous Integration

* ci: update doc requirements. ([`be932c6`](https://github.com/HRSAndrabi/pykp/commit/be932c6cad48c74f999369880a183f95103260cb))

* ci: docstring convention to numpy. ([`311d158`](https://github.com/HRSAndrabi/pykp/commit/311d158ce2ec18b089d1c317310d528f37a99920))

* ci: shorten workflow names. ([`c92708a`](https://github.com/HRSAndrabi/pykp/commit/c92708a39c07d0e75e88999b60c107cf11e8fffa))

* ci: clearer workflow names. ([`e9cf9a0`](https://github.com/HRSAndrabi/pykp/commit/e9cf9a02c91f3c738a6609fd91e30d30d95b58b5))

* ci: prevent redundant workflow runs.

Lint and test workflows were running two times.
(1) When a pull request was submitted, to verify that it was okay
to merge into main.
(2) After a pull request was merged, as a check before building
and releasing the next version of the package on PyPi.
The second run is unnecessary, as (1) ensures that (2) will always
pass. This commit removes (2). ([`b30f529`](https://github.com/HRSAndrabi/pykp/commit/b30f529323b1b33fa4a9914594bd9b2f5ce86a29))

* ci: start workflows on pull request. ([`d5bcb22`](https://github.com/HRSAndrabi/pykp/commit/d5bcb2260f00e321ae021b94a799e79f94e4d6f9))

### Documentation

* docs: add terminal nodes plot. ([`827e803`](https://github.com/HRSAndrabi/pykp/commit/827e803d651f3f38e0786a3c760bdd0718bc87c3))

* docs(tests): docstrings to numpydoc. ([`6eecbcc`](https://github.com/HRSAndrabi/pykp/commit/6eecbcc7db33797e5c128202080fd2157415f196))

* docs(pykp): docstrings to numpydoc. ([`298a945`](https://github.com/HRSAndrabi/pykp/commit/298a94591183641e91ec5e50c3d8ba330bd89ded))

* docs(solvers): docstrings to numpydoc. ([`008eafa`](https://github.com/HRSAndrabi/pykp/commit/008eafaa974147a52d4f19db0a69346869d1a910))

* docs(sampler): docstrings to numpydoc. ([`312dfb1`](https://github.com/HRSAndrabi/pykp/commit/312dfb184c069670a634a59e36c885f95f0c55c3))

* docs: add phase transition plot. ([`5c5a8df`](https://github.com/HRSAndrabi/pykp/commit/5c5a8df7d7585717751842119e7398b9bb5b43e7))

* docs(metrics): docstrings to numpydoc. ([`e0122cf`](https://github.com/HRSAndrabi/pykp/commit/e0122cfad3899532e31d2759f62fe278f5393f74))

* docs(knapsack): docstrings to numpydoc. ([`dc4353e`](https://github.com/HRSAndrabi/pykp/commit/dc4353e3cead439bda889b078bdb297ec03afb58))

* docs(item): docstrings to numpydoc. ([`60179a6`](https://github.com/HRSAndrabi/pykp/commit/60179a68d989ef24b3c696d2faf9bb6fe4cae392))

* docs(arrangement): docstrings to numpydoc. ([`9c9f50b`](https://github.com/HRSAndrabi/pykp/commit/9c9f50bf52abae7f8d5830df9c12b4cc80b77e45))

* docs: update templates to match scipy style. ([`39d5496`](https://github.com/HRSAndrabi/pykp/commit/39d54967fa84fcaea9cdfc5984378571f1d4c08a))

* docs: set groupwise autodoc. ([`afd68d3`](https://github.com/HRSAndrabi/pykp/commit/afd68d3c44fd56995ca83c674951fed0f0e04083))

* docs(knapsack): minor improvements for clarity. ([`45a4801`](https://github.com/HRSAndrabi/pykp/commit/45a48017bb2e0ecafe861528dbf1f090a7e9b875))

* docs(sampler): move init doc to class level. ([`6fc9a4d`](https://github.com/HRSAndrabi/pykp/commit/6fc9a4d15e704e473217ee1f532f5cc5861e46bf))

* docs(item): fix style errors. ([`da3a12a`](https://github.com/HRSAndrabi/pykp/commit/da3a12abb36a9a0ca8351e8906419f4e65684255))

* docs(knapsack): add property documentation. ([`4c2b2c6`](https://github.com/HRSAndrabi/pykp/commit/4c2b2c65b8f272e75678cc2f244804c5ad2d9f72))

* docs: minor improvements for clarity. ([`0e5fbc9`](https://github.com/HRSAndrabi/pykp/commit/0e5fbc929ea8dff3b63db335a12c434601233542))

* docs: clarify solver documentation. ([`c861f24`](https://github.com/HRSAndrabi/pykp/commit/c861f24fd3b0c09d04709a3ac6c05c8127c15459))

* docs(sahni-k): fix indendtation. ([`e3b34aa`](https://github.com/HRSAndrabi/pykp/commit/e3b34aa34fcfba48b34d9fe9e4899b1a49a2e820))

* docs: add complexity metrics to quick-start. ([`100a244`](https://github.com/HRSAndrabi/pykp/commit/100a2440d7bf0354c406e0c8ca5825cface00d4e))

* docs: remove references to missing images. ([`7da8d2f`](https://github.com/HRSAndrabi/pykp/commit/7da8d2fd680020776817b31bd663804d4f3df4d5))

* docs: update quick-start guide. ([`5c1d027`](https://github.com/HRSAndrabi/pykp/commit/5c1d0276c886287f5397cc006554030aff6ab0d2))

* docs: change order of nav items. ([`5f319d8`](https://github.com/HRSAndrabi/pykp/commit/5f319d8bc10ff301b62e6eda309e5a280b0d2910))

* docs: update contributer guide. ([`7e404e3`](https://github.com/HRSAndrabi/pykp/commit/7e404e3067b0e5250497bfd6a709909fd89d997d))

### Features

* feat(solvers): add brute force solver.

Add brute force solver to compute optimal, terminal, feasible, and
all possible nodes in the graph of a provided KP instance. Changed
the name of `_is_terminal_node()` method used by branch and bound
algorithm to `_is_leaf_node()`, to avoid confusion with the
`is_subset_terminal()` method used by the new brute force
algorithm. ([`8918eb1`](https://github.com/HRSAndrabi/pykp/commit/8918eb1989119aec7f67bf7e4b155bf6b40bbdb3))

* feat(branch_and_bound): add n-best functionality.

`pykp.solvers.branch_and_bound` now accepts an optional argument
`n`, which specifies the number of 'best' solutions to return.
The `n` argument is on solution values, not the number of
solutions. If `n` is set to 1, the solver returns all solutions
that achieve the distinct optimal value. More than one solution
may be returned if there are multiple solutions with the same
optimal value. Similarly, if `n` is set to n, the solver returns
all solutions that achieve the n-highest possible values. ([`574b509`](https://github.com/HRSAndrabi/pykp/commit/574b5099dcf15fff53deb4d9fea7d4e3ccd17cfa))

### Refactoring

* refactor(knapsack): don't save optimal to config. ([`464bce4`](https://github.com/HRSAndrabi/pykp/commit/464bce4619779b53c97dfd375f504ca361960bc1))

* refactor(arrangement): add @property decorators. ([`b63f6b5`](https://github.com/HRSAndrabi/pykp/commit/b63f6b5aa8be43bfc04d2c1c1cfbc1cc53a1b0f8))

* refactor(knapsack): implement brute_force solver.

Allow "brute_force" to specified as the `method` argument to
`Knapsack.solve()`. Remove methods in `Knapsack` that are now
redundant with the addition of a seperate brute-force solver. ([`fa81822`](https://github.com/HRSAndrabi/pykp/commit/fa81822f3a5a0c0adbb2459bce751fcb5567da67))

* refactor(solvers): move pacakge to module.

Refactored pykp.solvers pacakage to pykp.solvers module. This
makes auto generated documentation appear in a more sensible way.
Under the previous approach, documentation for functions inside
modules in the pykp.solvers package would not render, because these
functions shared the same name as the module. Including all
functions inside a single solvers.py module rectifies this problem. ([`f425dc4`](https://github.com/HRSAndrabi/pykp/commit/f425dc46c834a080a9e115c9ffb0489cbb7d194a))

* refactor: move metrics package to module. ([`47e2686`](https://github.com/HRSAndrabi/pykp/commit/47e2686bee73156d358b3bf8f400383ba52fa5bd))

### Testing

* test: ammend test for list solution type. ([`318f37d`](https://github.com/HRSAndrabi/pykp/commit/318f37d44af52d87559291a763c44e692b359c56))

### Unknown

* tests(knapsack): account for new state setter. ([`4c144e8`](https://github.com/HRSAndrabi/pykp/commit/4c144e874d6a6e958055c36fa11d17903f37e20b))


## v3.0.0 (2025-01-10)

### Breaking

* refactor(sampler): remove `*_range` args.

Removed `weight_range`, `solution_value_range` and `density_range`
arguments from `Sampler()`. `Sampler()` now works by sampling
weights and values based on a supplied distribution, which is
unifrom (0,1) by default.

BREAKING CHANGE: `weight_range`, `solution_value_range` and
`density_range` arguments to `pykp.Sampler()` no longer exist. ([`358c3a6`](https://github.com/HRSAndrabi/pykp/commit/358c3a66dfcfedfe6fcdf3d282a6c1b0c72f37e0))

### Bug Fixes

* fix(mzn_geocode): nest asynchronous loops.

MiniZinc raised an error when being called from a Jupyter notebook
because both MiniZinc's solve() method and Jupyter run their own
conflicting async loop. The issue is fixed by patching asyncio
using the nested_asyncio package.

See https://github.com/MiniZinc/minizinc-python/issues/38. ([`3a94ea4`](https://github.com/HRSAndrabi/pykp/commit/3a94ea4a1e249f3ce41094171430ba563f66ab72))

* fix(sampler): don't convert capacity to int. ([`a182e16`](https://github.com/HRSAndrabi/pykp/commit/a182e16857de6e5edc4af4552027bb1c8992b256))

* fix: remove unexpected argument from .solve().

The old .solve() method accepted an argument for
`solve_second_best`. This was removed in 2.0 with the addition of
a seperate package for solvers. ([`5754958`](https://github.com/HRSAndrabi/pykp/commit/5754958a8742c8159e01340314573f2687682309))

### Build System

* build: update requirements. ([`ce5db33`](https://github.com/HRSAndrabi/pykp/commit/ce5db33db8496e6dfa3d6b8c0c4ce7f5f84bbd8b))

* build: update dependencies. ([`7bf4110`](https://github.com/HRSAndrabi/pykp/commit/7bf4110823edb1c4efe4b2893a6b5b94bed14cc0))

### Chores

* chore: fix tab spacing. ([`28f511b`](https://github.com/HRSAndrabi/pykp/commit/28f511b309515d97694cbed875b54fab8f35caaf))

### Continuous Integration

* ci: create release workflow.

Refined version of the previous continuous-delivery workflow.
Lints and tests before publishing release on pushes to the main
branch. ([`4b1b9bc`](https://github.com/HRSAndrabi/pykp/commit/4b1b9bce43a391a611c0c82375a8caa851eb06b9))

* ci(lint): make callable. ([`bc69b09`](https://github.com/HRSAndrabi/pykp/commit/bc69b099060ddd2901557a0729701dd3f1aa3aa8))

* ci: add lint with Ruff workflow. ([`4a97d52`](https://github.com/HRSAndrabi/pykp/commit/4a97d5260736471762f0602c3793497f8019cf1f))

* ci: add test with pytest workflow. ([`1b78077`](https://github.com/HRSAndrabi/pykp/commit/1b780773c4c7ebaa5aea86a0cdd559f9638fe69d))

* ci: point to correct requirements. ([`c0b90df`](https://github.com/HRSAndrabi/pykp/commit/c0b90dfbf4c7ba6ebe022918487b7a3055daf097))

* ci: generate requirements from pyproject.toml

Add script to extract dependencies from pyproject.toml into
separate files. ([`a1f7555`](https://github.com/HRSAndrabi/pykp/commit/a1f75558e308ed75f4568de62f74044ecf1d9f6d))

* ci: mock dependancy imports. ([`240ec64`](https://github.com/HRSAndrabi/pykp/commit/240ec643c63fa6de2809ddd3df2023aec2c5dbf9))

* ci: add ruff action. ([`84254e8`](https://github.com/HRSAndrabi/pykp/commit/84254e87b0b4beebfb65db9b8b4b5c80e3c342bb))

### Documentation

* docs: remove 'await' from solve() calls. ([`a19520d`](https://github.com/HRSAndrabi/pykp/commit/a19520dff1b2eb502f3a26a219fecfab41d25a48))

* docs: shorten phrasing.

Global find and replace 'This module provides' -> 'Provides'. ([`7ce509e`](https://github.com/HRSAndrabi/pykp/commit/7ce509e853690d5f4c106f646754631aab05bdc7))

* docs(tests): add docstring for test. ([`4ddeb4d`](https://github.com/HRSAndrabi/pykp/commit/4ddeb4d166e64f0d2f860e335a483cb1d875a310))

* docs: add favicons. Fix wildcard warnings. ([`7a5d4df`](https://github.com/HRSAndrabi/pykp/commit/7a5d4dfc6249778bc26d4108d1e5cca5b1edbc47))

* docs: add 'edit page' button. ([`6125aae`](https://github.com/HRSAndrabi/pykp/commit/6125aae53343c0a392c4d14134630e26a77301be))

* docs: add PyPi icon. ([`242ff80`](https://github.com/HRSAndrabi/pykp/commit/242ff8052b93a9c7a7d47771fdc287bf9619ec0d))

* docs: show primary sidebar on reference. ([`7e80eec`](https://github.com/HRSAndrabi/pykp/commit/7e80eec59e50dcc80da795a53dfe253fad3a0a9a))

* docs: add logo. ([`28533b7`](https://github.com/HRSAndrabi/pykp/commit/28533b707435827b1a3da2b79d6e633def1d0337))

* docs: add missing imports. ([`4e9f272`](https://github.com/HRSAndrabi/pykp/commit/4e9f2723d09f0a5da8c266ed8ba89be478750f82))

### Testing

* test: remove solver.mzn_geocode tests.

Minizinc tests only work if the solver is installed on the machine.
It doesn't make sense to call these tests regularly. ([`dcfaf17`](https://github.com/HRSAndrabi/pykp/commit/dcfaf1713aa52f104df85224ac7e7c9376907e95))

* test: wrap assert in ([`c0dd273`](https://github.com/HRSAndrabi/pykp/commit/c0dd2738fb2736c8b9d017b0ed39f785c6ae79a6))

* test: remove incorrect int conversion. ([`3a1fcc8`](https://github.com/HRSAndrabi/pykp/commit/3a1fcc8155c944f56a24c00a509eb85d485db4a7))

* test: write tests for pykp.solvers. ([`2468af1`](https://github.com/HRSAndrabi/pykp/commit/2468af1d169453c16f1851c025626d98a94156c6))

* test: write tests for pykp.sampler. ([`f45c8bc`](https://github.com/HRSAndrabi/pykp/commit/f45c8bc553c92fcda5ebbf24da65ed8049596780))

* test: write tests for pykp.knapsack. ([`c9d3be0`](https://github.com/HRSAndrabi/pykp/commit/c9d3be0789b7f7782711a948086bb273bb11ca69))

### Unknown

* Apply ruff formatting. ([`77ea023`](https://github.com/HRSAndrabi/pykp/commit/77ea02399c99d69d224457de021df5dcb455b74a))


## v2.1.1 (2025-01-07)

### Bug Fixes

* fix: incorrect docs path. ([`80d357f`](https://github.com/HRSAndrabi/pykp/commit/80d357f42c0867db472f9dc1a9ad27cdbc2f4daa))

### Chores

* chore: remove underscores from filename. ([`fb687cd`](https://github.com/HRSAndrabi/pykp/commit/fb687cd069d52f38daa9d497dc1b9dcf7f3ad178))

* chore: remove Solver ABC. ([`0821748`](https://github.com/HRSAndrabi/pykp/commit/0821748a9a06ef9feb3e20286c99b0acb2d23773))

* chore: remove underscores from filename. ([`c982c2d`](https://github.com/HRSAndrabi/pykp/commit/c982c2d3d27dc1eb220c6342fadcbdaa97de8304))

* chore: remove Solver ABC. ([`99f57d6`](https://github.com/HRSAndrabi/pykp/commit/99f57d60a68e51fd7af91eeb6f0031852a6910e9))

### Documentation

* docs: add missing import. ([`c6b1f5c`](https://github.com/HRSAndrabi/pykp/commit/c6b1f5ca6a026413a885c235dac296fa0d9bd851))

* docs: add missing import. ([`f7049af`](https://github.com/HRSAndrabi/pykp/commit/f7049afb9c001a013685ee44ddcd6a0c8b652698))

* docs: integrate pydata and autosummary.

- Integrated pydata theme
- Integrated sphinx.ext.autosummary to recursively document all modules in pykp

Merge pull request #4 from HRSAndrabi/docs/clean-up ([`1657d5b`](https://github.com/HRSAndrabi/pykp/commit/1657d5bd8d32e42bd2c39e69f40d1db3e3d3481e))

* docs(solvers): move examples to module level. ([`59f9cdf`](https://github.com/HRSAndrabi/pykp/commit/59f9cdfec43c349331f393b1e57eb8dde4118fa5))

* docs(sampler): removed unintentional linebreaks. ([`8627520`](https://github.com/HRSAndrabi/pykp/commit/86275200c8176b4719b7b557f8a37ae3237220e0))

* docs: integrate pydata docs and autosummary.

Integrated pydata theme and autosummary to recursively generate
documentation for all modules in pykp. ([`0505a70`](https://github.com/HRSAndrabi/pykp/commit/0505a70533e303e9dd2a3fa5306b7bbdca5d6917))

* docs(solvers): move examples to module level. ([`9a183c4`](https://github.com/HRSAndrabi/pykp/commit/9a183c42672c7a709713c05fd4bf5274647ed9ff))

### Refactoring

* refactor(phase_transition): use refactored solvers. ([`89513be`](https://github.com/HRSAndrabi/pykp/commit/89513bee6d12cf3d2ebc2d4321d8c79aa82dd210))

* refactor(mzn_gecode): make functional. ([`6e1fe82`](https://github.com/HRSAndrabi/pykp/commit/6e1fe822107b2460c15df43a7d3a3985ba63eea4))

* refactor(greedy): make functional. ([`adbc5a0`](https://github.com/HRSAndrabi/pykp/commit/adbc5a0ea61fd27d26edf807fbbfc80ac73a2aed))

* refactor(branch_and_bound): make functional. ([`e2009ff`](https://github.com/HRSAndrabi/pykp/commit/e2009ff2a135ab2a5756881198ec7ff146fcede6))

* refactor(phase_transition): use refactored solvers. ([`156f3ec`](https://github.com/HRSAndrabi/pykp/commit/156f3ec48d0efb5ebadb3d0cc6c57e0559d6237e))

* refactor(mzn_gecode): make functional. ([`f987124`](https://github.com/HRSAndrabi/pykp/commit/f987124ea94109e0e1cdfcd33002737a434c98cd))

* refactor(greedy): make functional. ([`d3c14e9`](https://github.com/HRSAndrabi/pykp/commit/d3c14e95c3e5b5686095849e48f18c63472bf686))

* refactor(branch_and_bound): make functional. ([`3af1327`](https://github.com/HRSAndrabi/pykp/commit/3af1327a665cb733e9a951c8d104849e656631d0))

### Unknown

* Merge branch 'main' into docs/clean-up ([`10f11ce`](https://github.com/HRSAndrabi/pykp/commit/10f11cedac7a462a32c9bc238f419665b53adaa6))


## v2.1.0 (2025-01-05)

### Bug Fixes

* fix(mzn_geocode): change input type to allow floats.

Previous implementation only accepted knapsack instances with
integer weights/values/capacity. Now accepts floats. ([`9728808`](https://github.com/HRSAndrabi/pykp/commit/9728808e0d9954f5efb77054a3b5c89a0cb5aa11))

### Documentation

* docs(phase_transition): add module docs. ([`1da8756`](https://github.com/HRSAndrabi/pykp/commit/1da8756f125101dd704dbab9634d38db34e3ee27))

### Features

* feat(phase_transition): add save method. ([`04d46b4`](https://github.com/HRSAndrabi/pykp/commit/04d46b4ab111c323313603d8005c0163df4af8db))

* feat(metrics): add phase transition metric. ([`8dc3f19`](https://github.com/HRSAndrabi/pykp/commit/8dc3f1919cf5d8610a3545c8e978a63f7fa507ac))

* feat(metrics): add metrics package, add Sahni-k metric. ([`bc0e725`](https://github.com/HRSAndrabi/pykp/commit/bc0e725192d5667d9aa526e50f53cb904e444fe0))

### Refactoring

* refactor(knapsack): remove knapsack.calculate_sahni_k(). ([`a584dba`](https://github.com/HRSAndrabi/pykp/commit/a584dbad810f75f78b7aab0add127aea32d84efb))

* refactor(metrics.sahni_k): make independent of Knapsack class. ([`f3424aa`](https://github.com/HRSAndrabi/pykp/commit/f3424aaba17219f4022fc4cff12ea9cf5fc50303))

* refactor(metrics.sahni_k): take capacity as input.

Take capacity as input instead of the whole knapsack problem
instances. This makes calls to the metric cleaner. ([`9add168`](https://github.com/HRSAndrabi/pykp/commit/9add1682f869f4b4ff137852185dd620071409db))


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
