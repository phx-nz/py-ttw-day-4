.. image:: https://github.com/phx-nz/py-ttw-day-2/actions/workflows/build.yml/badge.svg
   :target: https://github.com/phx-nz/py-ttw-day-2/actions/workflows/build.yml

Boilerplate
===========
Template for new projects.  Fill out this section with a description of the
purpose/function for your project.

Don't forget to update project details in ``pyproject.toml``, too 😇

Installation
------------
Install via pipenv::

   pipenv install --dev

Automatic code quality checks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
After installing dependencies, run the following command to install git hooks
to automatically check code quality before allowing commits::

   pipenv run autohooks activate --mode pipenv

Running the server
------------------
To start the server, run the following command::

   pipenv run dev

You can confirm the server is running by going to
`http://127.0.0.1:8000/v1 <http://127.0.0.1:8000/v1>`_ in your browser.

Checking code quality
---------------------
You can manually run code quality checks with the following commands::

   # Check formatting:
   pipenv run black [file ...]

   # Linting (run both for best coverage):
   pipenv run pylint [file ...]
   pipenv run ruff check --fix [file ...]

Running Unit Tests
------------------
Run tests with the ``tox`` command::

   tox -p

.. tip::

   `tox`_ installs your package in a separate virtualenv, to help you catch any
   issues with your project's packaging, as well as testing your code with
   different versions of Python.  The trade-off is that it takes a bit longer to
   run your tests.

   If you just want to run the tests in the current virtualenv, you can use this
   command instead to get faster feedback::

      pipenv run pytest

Documentation
-------------
This project uses `Sphinx`_ to build documentation files.  Source files are
located in the ``docs`` directory.

To build the documentation locally:

#. Switch to the ``docs`` directory::

      cd docs

#. Build the documentation::

      make html

Documentation will be built in ``docs/_build/html``.


.. _Sphinx: https://www.sphinx-doc.org
.. _tox: https://tox.readthedocs.io
.. _uvicorn: https://www.uvicorn.org/
