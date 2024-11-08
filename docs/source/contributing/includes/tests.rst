Writing Tests
-------------

If you make a contribution to the code, please write a test for it. To add a test:

1. **Create a new test file**: Place new test files in the ``tests/`` directory, using the naming convention ``test_<feature>.py``.
2. **Use `unittest`**: PyKP uses the ``unittest`` framework. Use one of the existing tests as a guide.
3. **Run Tests**: Run the tests using the command below to ensure everything works as expected.

   .. code-block:: bash

      python -m unittest discover -s tests


