Testing
^^^^^^^^^^^^

If you make a contribution to the code, please write a test for it. PyKP uses the `pytest`_ framework. Create new test files in the ``tests/`` directory, using the naming convention ``test_<feature>.py``. Use one of the existing tests as a guide.

Run the tests using the command below to ensure everything works as expected.

.. code-block:: bash

   pytest --cov=pykp

You should see a summary of the test results and code coverage. If any tests fail, you should try and fix the issues before submitting a Pull Request.

.. _`pytest`: https://docs.pytest.org/en/latest/
