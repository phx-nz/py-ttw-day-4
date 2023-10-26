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

   pipenv run dev-server

You can confirm the server is running by going to
`http://127.0.0.1:8000/v1 <http://127.0.0.1:8000/v1>`_ in your browser.

.. tip::

   You can find the command that pipenv runs under the hood in ``Pipfile`` under the
   ``[scripts]`` heading.

Running CLI commands
--------------------
This app also comes with a set of CLI commands that you can run.  Use the following
command to see what commands are available::

   pipenv run app-cli --help

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

Generating user profiles
------------------------
The project comes pre-loaded with set of randomised profiles, generated using the
`Random User Generator API`_.  If desired you can generate new profiles by running the
following command::

   pipenv run app-cli generate profiles

By default, this will generate 5 new profiles.  If desired you can specify a different
number as a command-line argument.  For example, to generate 25 new profiles::

   pipenv run app-cli generate profiles 25

Documentation
-------------
FastAPI automatically generates OpenAPI documentation for you.  Once you've started the
server, go to `http://127.0.0.1:8000/docs <http://127.0.0.1:8000/docs>` to see it.

Refer to `FastAPI documentation`_ for more information.


.. _FastAPI documentation: https://fastapi.tiangolo.com/tutorial/first-steps/#interactive-api-docs
.. _Random User Generator API: https://randomuser.me/documentation
.. _tox: https://tox.readthedocs.io
.. _uvicorn: https://www.uvicorn.org/
