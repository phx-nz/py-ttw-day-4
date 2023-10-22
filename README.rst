.. image:: https://github.com/phx-nz/boilerplate/actions/workflows/build.yml/badge.svg
   :target: https://github.com/phx-nz/boilerplate/actions/workflows/build.yml

Boilerplate
===========
Template for new projects.  Fill out this section with a description of the
purpose/function for your project.

Don't forget to update project details in ``pyproject.toml``, too 😇

Installation
------------
Install via pipenv::

   pipenv install --dev


.. tip::

   The above command installs the project with additional dependencies for
   developing on your local system.  If you are installing the project onto a
   non-development environment, use the following command instead::

      pipenv install .

Automatic code quality checks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
After installing dependencies, run the following command to install git hooks
to automatically check code quality before allowing commits::

   pipenv run autohooks activate --mode pipenv

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
To run the unit tests:

#. Run tests with the ``tox`` command::

   tox -p

.. tip::

   `tox`_ installs your package in a separate virtualenv, to help you catch any
   issues with your project's packaging, as well as testing your code with
   different versions of Python.  The trade-off is that it takes a bit longer to
   run your tests.

   If you just want to run the tests in the current virtualenv, you can use this
   command instead to get faster feedback::

      python -m pytest

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

Releases
--------
Steps to build releases are based on `Packaging Python Projects Tutorial`_

.. important::

   Make sure to build releases off of the ``main`` branch, and check that all
   changes from ``develop`` have been merged before creating the release!

1. Build the project
~~~~~~~~~~~~~~~~~~~~
#. Delete artefacts from previous builds, if applicable::

    rm dist/*

#. Run the build::

    python -m build

#. The build artefacts will be located in the ``dist`` directory at the top
   level of the project.

2. Upload to PyPI
~~~~~~~~~~~~~~~~~
#. `Create a PyPI API token`_ (you only have to do this once).
#. Increment the version number in ``pyproject.toml``.
#. Check that the build artefacts are valid, and fix any errors that it finds::

    python -m twine check dist/*

#. Upload build artefacts to PyPI::

    python -m twine upload dist/*


3. Create GitHub release
~~~~~~~~~~~~~~~~~~~~~~~~
#. Create a tag and push to GitHub::

    git tag <version>
    git push <version>

   ``<version>`` must match the updated version number in ``pyproject.toml``.

#. Go to the ``Releases``.
#. Click ``Draft a new release``.
#. Select the tag that you created in step 1.
#. Specify the title of the release (e.g., ``KiaOraTeAo v1.2.3``).
#. Write a description for the release.  Make sure to include:
   - Credit for code contributed by community members.
   - Significant functionality that was added/changed/removed.
   - Any backwards-incompatible changes and/or migration instructions.
   - SHA256 hashes of the build artefacts.
#. GPG-sign the description for the release (ASCII-armoured).
#. Attach the build artefacts to the release.
#. Click ``Publish release``.

.. _Create a PyPI API token: https://pypi.org/manage/account/token
.. _Packaging Python Projects Tutorial: https://packaging.python.org/en/latest/tutorials/packaging-projects
.. _Sphinx: https://www.sphinx-doc.org
.. _tox: https://tox.readthedocs.io
