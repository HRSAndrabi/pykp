
Install a local copy
-----------------------

To install the latest version of PyKP directly from GitHub, clone the repository and install it in "editable" mode. This allows you to make changes to the source code and see them immediately reflected.

#. Optional: `fork the repository`_ .

   If you don't want to merge your changes with the original repository,
   you can skip this step.

#. `Clone the repository`_:

   - If you forked the repository, run:

     .. code-block:: bash
        :emphasize-text: GITHUB_USERNAME

        git clone https://github.com/GITHUB_USERNAME/pykp.git

     Replace :samp:`{GITHUB_USERNAME}` with your GitHub username.

   - If you didn't fork the repository, clone the original repository:

     .. code-block:: bash

        git clone https://github.com/yourusername/pykp.git

#. **Install PyKP in editable mode:**

   .. code-block:: bash

      pip install --editable .

This will install PyKP along with all necessary dependencies.


.. _`fork the repository`: https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo
.. _`Clone the repository`: https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository
