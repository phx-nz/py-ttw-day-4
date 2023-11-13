Day 3 Arvo: SQLAlchemy & Alembic
================================
This afternoon we're going to enhance the application further, by introducing a proper
PostgreSQL database, using `SQLAlchemy <https://www.sqlalchemy.org/>`_ as our ORM and
`Alembic <https://alembic.sqlalchemy.org/en/latest/>`_ for managing schema migrations.

Setup
-----
To get things working, you'll need to do a few things:

#. Stop the application server if it is currently running::

      pipenv run docker-stop

#. Install a few more dependency packages::

      pipenv install --dev

#. Rebuild the application and start the servers::

      pipenv run docker-start

   Note that this time Docker starts two containers — an application server and a
   database server.

#. Run the first database migration::

      pipenv run alembic upgrade head

#. Lastly, seed your new database with some new profiles::

      pipenv run app-cli generate profiles

And you should be good to go!  Try sending a request to
`http://localhost:8000 <http://localhost:8000>`_ to make sure the application server is
running.

.. tip::

   Just like how you can connect to the application server using your browser or API
   development tool, you can also connect to the database server using a DB browser
   (such as the databases tool window in your IDE).

   Look at `.env.development <./.env.development>`_ to see the connection details.

   Note that normally we would not commit ``.env.*`` files to the repository, but in
   this case we're making an exception so that we can dive into the workshop exercise
   more quickly.

Resetting the database
---------------------
The database server stores its data files in a
`Docker volume <https://docs.docker.com/storage/volumes/>`_, so that the data are
persisted even when the container isn't running.

If you want to reset the database and start over, do the following:

#. Stop the servers::

      pipenv run docker-stop

#. Reset the database::

      pipenv run docker-reset-db

#. Start the servers again::

      pipenv run docker-start

#. Re-run schema migrations::

      pipenv run alembic upgrade head

#. If desired, re-seed the database with some profiles::

      pipenv run app-cli generate profiles

Exercise instructions
=====================
The goal of this afternoon's exercise is to refactor your code to make it work with
SQLAlchemy.

.. tip::

   If you get stuck at any point, you can check the ``solution`` branch, which contains
   a completed solution for this exercise.

Step 1: Get profile by ID (HTTP interface)
------------------------------------------

Step 2: Get profile by ID (CLI interface)
-----------------------------------------

Step 3: Update profile by ID (HTTP interface)
---------------------------------------------

Step 4: Update profile by ID (CLI interface)
--------------------------------------------

Step 5: Stretch goals
---------------------
This step is optional.  If you're feeling confident and want to tackle some extra
challenges, give these a try 😺
