Development Environment
--------------------------------------

1. **Fork the Repository**: Start by forking the PyKP repository on GitHub.

2. **Clone the Repository**: Clone your forked repository to your local machine.

   .. code-block:: bash

      git clone https://github.com/yourusername/pykp.git
      cd pykp

3. **Create a Virtual Environment**: Set up a virtual environment to manage dependencies.

   .. code-block:: bash

      python3 -m venv venv
      source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

4. **Install Dependencies**: Install the package dependencies in "editable" mode, including development dependencies.

   .. code-block:: bash

      pip install --editable .

5. **Run Tests**: Run the test suite to ensure the setup is working correctly.

   .. code-block:: bash

      python -m unittest discover -s tests
