Commit Messages
^^^^^^^^^^^^^^^

PyKP uses the `Conventional Commits`_ specification for commit messages. This format helps automate the release process and generate changelogs. The format is as follows:

.. code-block:: bash

	<type>[optional scope]: <description>

	[optional body]

	[optional footer]


The `type` is one of the following:

- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation changes
- **style**: Changes that do not affect the meaning of the code (white-space, formatting, etc.)
- **refactor**: A code change that neither fixes a bug nor adds a feature
- **perf**: A code change that improves performance
- **test**: Adding missing tests
- **chore**: Changes to the build process or auxiliary tools and libraries

The `scope` is optional and can be anything specifying the location of the commit change.

The `description` should be a short, imperative sentence that describes the change.

The `body` is optional and should provide a more detailed description of the change. Use the body to explain what and why vs. how.

The `footer` is optional and can be used to reference issues or pull requests.

For example:

.. code-block:: bash

	feat(solvers): added XYZ solver

	A new solver based on the XYZ algorithm.


.. _`Conventional Commits`: https://www.conventionalcommits.org/en/v1.0.0/