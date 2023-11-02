.. image:: https://github.com/phx-nz/py-ttw-day-3/actions/workflows/build.yml/badge.svg
   :target: https://github.com/phx-nz/py-ttw-day-3/actions/workflows/build.yml

Workshop Day 3: SQLAlchemy
==========================
The goal of today's workshop is to augment the `FastAPI`_ application that you built
yesterday, replacing the file-based "database" with a proper Postgres server, and using
`SQLAlchemy`_ to interact with it.

The Postgres server has already been set up for you.  After pulling down the changes
from origin, re-run the command to start the server, and it will automatically start and
configure the Postgres server for you.  Check out the updated files in the
`docker folder <./docker>`_ for more information.


Installation
------------
Install via pipenv::

   pipenv install --dev

.. note:: To avoid conflicts, this project's distro is named ``py-ttw-day-2``.

Automatic code quality checks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
After installing dependencies, run the following command to install git hooks
to automatically check code quality before allowing commits::

   pipenv run autohooks activate --mode pipenv

Running the server
------------------
To start the server, run the following command, which will launch the app inside a
Docker container::

   pipenv run docker-start

This will start both the app server and the Postgres database server.

.. tip::

   When the Docker container runs, it will mount your local codebase as a volume, so
   that as you make changes to your code, the server will automatically reload 😎

   Note that if you make any changes that would require a rebuild (e.g., add
   dependencies to ``Pipfile``), then you'll need to stop and restart the container.

To stop the Docker containers, run the following command::

   pipenv run docker-stop

Database management
-------------------
You can connect to the database container using your IDE.  Use the following
configuration values:

- Hostname: ``localhost``
- Port:     5432
- Username: ``developer``
- Password: ``Bo5doh4oobaeGheeS6neeCoo4aicha9aishah6Chievieng6aethaebai8aimula``
- Database: ``app``
- Schema: ``public``

Resetting the database
~~~~~~~~~~~~~~~~~~~~~~
The database container stores its data in a volume, so that they are persisted when the
container is stopped.  If you want to restore the database to its initial (empty) state,
run the following commands::

   pipenv run docker-stop
   pipenv run docker-reset-db

The next time you start the Docker containers, the database will be re-initialised.

Checking code quality
---------------------
You can manually run code quality checks with the following commands::

   # Check formatting:
   pipenv run black [file ...]

   # Run linter
   pipenv run ruff check --fix [file ...]

Running Unit Tests
------------------
Run tests with the following command::

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

We'll talk more about building a CLI app during tomorrow's workshop 😎

Documentation
-------------
FastAPI automatically generates OpenAPI documentation for you.  Once you've started the
server, go to `http://localhost:8000/docs <http://localhost:8000/docs>`_ to see it.

Refer to `FastAPI documentation`_ for more information.

Exercise Instructions
=====================


.. _FastAPI: https://fastapi.tiangolo.com/
.. _FastAPI documentation: https://fastapi.tiangolo.com/tutorial/first-steps/#interactive-api-docs
.. _Random User Generator API: https://randomuser.me/documentation
.. _SQLAlchemy: https://www.sqlalchemy.org/
.. _uvicorn: https://www.uvicorn.org/
