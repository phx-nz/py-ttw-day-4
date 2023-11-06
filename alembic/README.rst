Alembic
=======
This directory contains files for managing and running database migrations using
`Alembic <https://alembic.sqlalchemy.org/en/latest/tutorial.html>`_.

Creating migrations
-------------------
To create a migration, run the following command in your terminal::

   pipenv run alembic revision -m "<description>" --autogenerate

Where ``<description>`` is a description of what the migration will do.  For example::

   pipenv run alembic revision -m "create account table" --autogenerate

Alembic will create a new Python file with empty ``upgrade()`` and ``downgrade()``
functions, which will contain the migration logic.

.. tip::

   The ``--autogenerate`` flag will activate Alembic's
   `autogeneration feature <https://alembic.sqlalchemy.org/en/latest/autogenerate.html>`_
   which will compare the database schema against your models and generate the logic for
   the ``upgrade()`` and ``downgrade()`` functions automatically.

   If you omit this flag, Alembic will generate the migration file with empty
   ``upgrade()`` and ``downgrade()`` functions instead.

Running migrations
------------------
Run migrations with the following command::

   pipenv run alembic upgrade head

Alembic will identify and run any migration files needed to bring your database schema
up-to-date.

``head`` is an alias for the latest migration (similar to git's ``HEAD`` alias).

Checking state
--------------
You can check the current state of the database schema with the following command::

   pipenv run alembic current

To see a history of the migrations that have been run, along with descriptions for each
migration::

   pipenv run alembic history --verbose

Downgrading to a previous migration
-----------------------------------
If necessary, you can downgrade to a previous migration by running the following
command::

   pipenv run alembic downgrade <revision>

Where ``<revision>`` is the revision of the migration you want to downgrade to.

Further reading
===============
There's a lot more you can do with Alembic.  Check out the
`Alembic docs <https://alembic.sqlalchemy.org/en/latest/index.html>`_ for more
information.
