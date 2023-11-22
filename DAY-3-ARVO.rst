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
   more quickly 😁

Resetting the database
----------------------
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
We'll start with the API endpoint to get details about a profile.

Integration test
~~~~~~~~~~~~~~~~
You probably don't need to make any changes to your integration test.  Testing
interfaces over implementation details FTW 😎

Unit tests
~~~~~~~~~~
If you've added a method to ``ProfileService`` to fetch a profile by ID, then you might
also have unit tests for this method...which you probably don't need to change either 😎

API endpoint
~~~~~~~~~~~~
* The app uses
  `SQLAlchemy's asyncio extension <https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html>`_
  to access the database, so you'll need to make your API endpoint function ``async``.

* Access the profile service using the new ``services.get_service()`` function, like
  this:

  .. code-block:: py

     from services import get_service
     from services.profile import ProfileService

     @router.get("/profile/{profile_id}")
     async def get_profile(profile_id: int) -> dict:
         profile_service: ProfileService = get_service(ProfileService)

  .. note::

     The redundant type hint is unfortunately necessary to make code completion work in
     JetBrains IDEs, for now (it should be fixed in the next release).  See
     `https://youtrack.jetbrains.com/issue/PY-60767/ <https://youtrack.jetbrains.com/issue/PY-60767/>`_
     for more information.

* Create a database session using ``profile_service.session()``, like this:

  .. code-block:: py

     async with profile_service.session() as session:
         ...

* Modify the code to get the profile so that it fetches the profile from the database
  instead of the JSON file.  You can use ``session.get()`` or ``session.scalar()`` for
  this.

* Remember that all code that uses database objects must be inside of a database session
  context (``async with profile_service.session() as session``).

.. tip::

   The end result should look something like this:

   .. code-block:: py

      # src/api/routers/v1.py
      from models.profile import Profile
      from services import get_service
      from services.profile import ProfileService

      @router.get("/profile/{profile_id}")
      async def get_profile(profile_id: int) -> Profile:
          profile_service: ProfileService = get_service(ProfileService)
          async with profile_service.session() as session:
              profile: Profile | None = await profile_service.get_by_id(
                  session, profile_id
              )

              if not profile:
                  raise HTTPException(status_code=404, detail="Profile not found")

              return profile

      # src/services/profile.py
      class ProfileService(BaseOrmService):
          @staticmethod
          async def get_by_id(session: AsyncSession, id: int) -> Profile | None:
              return await session.get(Profile, id)

              # Or:
              return await session.scalar(
                  select(Profile).where(Profile.id == id).limit(1)
              )


Step 2: Get profile by ID (CLI interface)
-----------------------------------------
Next up is the CLI interface for getting a profile by ID.

Integration test
~~~~~~~~~~~~~~~~
You probably won't need to make any changes to your CLI integration test, either 😎

CLI command
~~~~~~~~~~~
Once you've gotten your API endpoint function working with the database, it should be
straightforward to do the same for your CLI command function.

Tips:

* To work with the database, you'll need to make your CLI command function asynchronous,
  but there's a bit of a snag because Typer doesn't support asynchronous commands.  So,
  you'll need to add the ``@embed_event_loop`` decorator, like this:

  .. code-block:: py

     @app.command("get")
     @embed_event_loop
     async def get_profile(profile_id: int):

  .. important:: Make sure ``@embed_event_loop`` is **after** ``@app.command()``.

Step 3: Update profile by ID (HTTP interface)
---------------------------------------------
Next up is updating a profile by its ID.  As before, we'll start with the API endpoint
function.

Tips:

* If your integration test also checks that the profile was modified in the database,
  you may need to update your test.

* Similarly, you may need to update unit tests if you've added a method to
  ``ProfileService`` to update profiles.

* To update the profile, you can either modify the ``Profile`` object attributes, or you
  can use the ``sqlalchemy.update()`` function.

  .. important:: Don't forget to call ``session.commit()`` (or use ``session.begin()``
     to create an auto-committing transaction).

Step 4: Update profile by ID (CLI interface)
--------------------------------------------
Lastly, modify your CLI command function to work with the database.

Tips:

* Modifying the integration test will be a little tricky.  You won't be able to make
  your test function asynchronous because that will cause an error when you try to
  invoke your CLI command inside the test (``@embed_event_loop`` will try to spin up an
  event loop, and Python won't let you run multiple event loops concurrently).

  Instead, you'll need to wrap the asynchronous parts of your integration test inside a
  function that is also decorated with ``@embed_event_loop``).  It will look something
  like this:

  .. code-block:: py

     def test_update_profile_happy_path(
         data_filepath: str,
         profiles: list[Profile],
         runner: TestCliRunner,
     ):
         target_profile: Profile = profiles[0]

         result: Result = runner.invoke(
             ["profiles", "update", str(target_profile.id), data_filepath]
         )

         @embed_event_loop
         async def verify():
             profile_service: ProfileService = get_service(ProfileService)
             async with profile_service.session() as session:
                 ...

         verify()

Step 5: Stretch goals
---------------------
This step is optional.  If you're feeling confident and want to tackle some extra
challenges, give these a try 😺

* If you've also added an API endpoint and CLI command to create a profile from
  yesterday's stretch goals, update those functions to add new profiles to the database\
  instead of the JSON file (and if you haven't added these yet, try writing them 😁).

* Users want to be able to bestow awards on other their friends' profiles.  Add a new
  model ``Award`` with a relation to ``Profile``:

  #. Create a new standalone model ``Award``.  Don't worry about relating it to
     ``Profile`` yet.

  #. Look at `alembic/README.rst <./alembic/README.rst>`_ for instructions to create a
     new migration.

  #. Create and run a new migration, and verify that the ``awards`` table was created in
     your database.

  #. Next add the relation to ``Profile`` and ``Award``.  Refer to
     `SQLAlchemy ORM relationship patterns <https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html#one-to-many>`_
     for some ideas.

     .. tip::

        The end result should look something like this:

        .. code-block:: py

           # src/models/profile.py
           from sqlalchemy.orm import Mapped, mapped_column, relationship
           from models.award import Award
           from models.base import Base

           class Profile(Base):
               ...
               awards: Mapped[list[Award]] = relationship(
                   back_populates="profile",
                   default_factory=list,
                   lazy="joined",
               )

           # src/models/award.py
           from sqlalchemy import ForeignKey
           from sqlalchemy.orm import Mapped, mapped_column, relationship
           from typing import TYPE_CHECKING
           from models.base import Base

           # Make ``Profile`` a forward ref, to avoid circular imports.
           # :see: https://stackoverflow.com/a/39757388/5568265
           if TYPE_CHECKING:
               from models import Profile

           class Award(Base):
               ...
               profile: Mapped["Profile"] = relationship(
                   back_populates="awards",
                   lazy="joined",
               )
               profile_id: Mapped[int] = mapped_column(ForeignKey("profiles.id"))

  #. Create and run another alembic migration to add the new columns and the foreign
     key.

  #. This will likely make some unit and integration tests fail, as they will not be
     expecting ``awards`` to appear in API responses and CLI output.  You'll need to fix
     the tests and get back to a green bar again.

     .. note::

        If you get ``RecursionError: maximum recursion depth exceeded``, this is a known
        issue with ``jsonable_encoder()`` (see
        `GitHub discussion <https://github.com/tiangolo/fastapi/discussions/9026>`_).

        To work around the issue, use ``models.base.model_encoder`` instead of
        ``jsonable_encoder``.  This function strips out recursive many-to-one relations
        before passing the ORM object to ``jsonable_encoder``.

        Note that ``model_encoder`` doesn't handle one-to-one and many-to-many
        relationships...yet 🤔

  #. Add unit tests and a ``ProfileService`` method to add an award to a profile.

  #. Add integration tests and an API method to add an award to a profile.

  #. Lastly, add integration tests and a CLI command to add an award to a profile.
