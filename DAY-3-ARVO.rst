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
