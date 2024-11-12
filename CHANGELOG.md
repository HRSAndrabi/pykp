# CHANGELOG


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


## v1.0.0 (2024-11-09)

### Unknown

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
