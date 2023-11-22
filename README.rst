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

Refer to `DAY-3-ARVO.rst <./DAY-3-ARVO.rst>`_ for exercise instructions.

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
`Random User Generator API <https://randomuser.me/documentation>`_.  If desired you can
generate new profiles by running the following command::

   pipenv run app-cli generate profiles

By default, this will generate 5 new profiles.  If desired you can specify a different
number as a command-line argument.  For example, to generate 25 new profiles::

   pipenv run app-cli generate profiles 25

We'll talk more about building a CLI app during tomorrow's workshop 😎

Documentation
-------------
FastAPI automatically generates OpenAPI documentation for you.  Once you've started the
server, go to `http://localhost:8000/docs <http://localhost:8000/docs>`_ to see it.

Refer to
`FastAPI documentation <https://fastapi.tiangolo.com/tutorial/first-steps/#interactive-api-docs>`_
for more information.

Exercise Instructions
=====================
The goal of today's exercise is to add two API endpoints to the application to retrieve
and edit user profiles, respectively.  To get you started, this project includes a
sample FastAPI application with a single API endpoint.

The project uses a JSON file as its "database", located at
`src/data/profiles.json <./src/data/profiles.json>`_.  Tomorrow we'll turn this into a
proper database 😇

There are also two methods in `src/services/profile.py <./src/services/profile.py>`_
that you can use to read and write profile data, respectively.

.. tip::

   If you get stuck at any point, you can check the ``solution`` branch, which contains
   a completed solution for the exercise.

Step 1: Get profile by ID (happy path)
--------------------------------------
When a client sends a GET request to ``http://localhost:8000/v1/profile/{profile_id}``
the app will respond with the details for the profile with the matching ID.  For
example, ``http://localhost:8000/v1/profile/3``, will respond with the details for
profile ID 3.

#. Add a new API endpoint ("path operation" in FastAPI parlance) to
   `src/api/routers/v1.py <./src/api/routers/v1.py>`_, and make it return some kind of
   value.  Don't worry about returning profile data yet; for now just have it return
   `something`, so that we can check that the endpoint is working.

   Once you've added the endpoint, verify that it works by going to
   `http://localhost:8000/v1/profile/1 <http://localhost:8000/v1/profile/1>`_ in your
   browser or API development tool.

   .. tip::

      You'll need to define a
      `path parameter <https://fastapi.tiangolo.com/tutorial/path-params/>`_ to make
      this work.

#. Before continuing, let's write a starter integration test, so that we can
   programmatically verify that our endpoint is working properly.

   Add a new file to `test/integration/v1 <./test/integration/v1>`_ that will hold the
   integration tests for your new API endpoint (for example, ``test_get_profile.py``).

   .. important::

      The filename must start with ``test_`` in order for pytest to find it.

   Write a simple test that checks for a 200 response from your API endpoint.  Don't
   worry about checking for profile data in the response body yet; we'll tackle that a
   bit later.

   .. tip::

      Look at ``test_index`` in
      `test/integration/v1/test_index.py <./test/integration/v1/test_index.py>`_ for an
      example.

      Note how it uses the ``client`` fixture.  You can find the definition for this
      fixture in
      `test/integration/api/conftest.py <./test/integration/api/conftest.py>`_.

#. Now let's switch back to the API endpoint and get it to load some actual profile
   data.

   In `src/services/profile.py <./src/services/profile.py>`_ you can find a method
   called ``ProfileService.load_profiles()`` which returns a list of all of the profiles
   in the database.  Your API endpoint will need to call this function and then find the
   profile with the matching ID in the list.

   Once your endpoint has found the correct profile, it should ``return`` the profile.

   .. tip::

      Your API endpoint should look something like this when you're done:

      .. code-block:: py

         from models.profile import Profile
         from services.profile import ProfileService.load_profiles

         @router.get("/profile/{profile_id}")
         def get_profile(profile_id: int) -> Profile:
             """
             Retrieves the profile with the specified ID.
             """
             # This is just one way to do it.
             # You might have used a different approach (:
             profile = next(
                 p for p in ProfileService.load_profiles() if p.id == profile_id
             )

             return profile

#. The final step is to modify your integration test so that it checks for actual
   profile data in the response.

   Normally this would be tricky, as you'd need to set up an ephemeral database for
   the test to use.  Fortunately, there is already a fixture defined that you can use to
   set this up for your tests, called ``profiles``.

   To use it, add it as an argument to your test function like this:

   .. code-block:: py

      from fastapi.testclient import TestClient
      from models.profile import Profile

      def test_get_profile(client: TestClient, profiles: list[Profile]):
         ...

   You can see what this fixture does by looking in
   `test/conftest.py <./test/conftest.py>`_

#. Now that your test is using the ``profiles`` fixture, you can add logic to inspect
   the body of the response.

   FastAPI returns responses in JSON format by default, so to decode the response body
   in your test, call ``response.json()``.  Something like this:

   .. code-block:: py

      response = client.get(...)
      assert response.status_code == 200
      assert response.json() == something

   Note that you can't directly compare ``response.json()`` with one of the ``Profile``
   objects in ``profiles`` because it won't have the same type (``response.json()``
   returns a ``dict``, not a ``Profile``).

   Fortunately, FastAPI has a solution for this:
   `jsonable_encoder() <https://fastapi.tiangolo.com/tutorial/encoder/>`_ converts the
   input value into a JSON-compatible type:

   .. code-block:: py

      from fastapi.encoders import jsonable_encoder

      response = client.get(...)
      assert response.status_code == 200
      assert response.json() == jsonable_encoder(profile)

   .. tip::

      Your integration should look something like this when you're done:

      .. code-block:: py

         from fastapi.encoders import jsonable_encoder
         from fastapi.testclient import TestClient

         from models.profile import Profile


         def test_happy_path(client: TestClient, profiles: list[Profile]):
             """
             Requesting a valid profile ID.
             """
             target_profile = profiles[0]

             response = client.get(f"/v1/profile/{target_profile.id}")

             assert response.status_code == 200
             assert response.json() == jsonable_encoder(target_profile)


Step 2: Get profile by ID (nonexistent ID)
------------------------------------------
That's our happy path sorted.  Next we need to handle an error case, where the user
requests a profile ID that doesn't exist.

#. Try going to
   `http://localhost:8000/v1/profile/999 <http://localhost:8000/v1/profile/999>`_ in
   your browser or API development tool and note the server error that you get.

#. This time, let's try a TDD approach.  Write an integration test that sends a request
   to get an invalid profile ID and checks that the response status code is 404.

   .. tip::

      If you get stuck, you can check the ``solution`` branch.

#. Now that you've got a red bar again, it's time to update your API endpoint to make
   your test pass.

   In order to send back a 404 response, your API endpoint will need to raise an
   `HTTPException <https://fastapi.tiangolo.com/tutorial/handling-errors/#use-httpexception>`_.

Step 3: Edit profile by ID (happy path)
---------------------------------------
Let's turn things up a notch by adding an API endpoint to allow editing profiles.  When
the client sends a PUT request to ``http://localhost:8000/v1/profile/{profile_id}`` and
specifies a replacement profile in the request body, the server will update the
corresponding profile in the database and respond with the modified profile.

Here are some hints to help you:

- Look at FastAPI's `Request Body <https://fastapi.tiangolo.com/tutorial/body/>`_
  documentation to see how to access and validate the request body in your API endpoint.
- In `src/services/profile.py <./src/services/profile.py>`_ there is a
  ``ProfileService.save_profiles()`` method that overwrites the profiles stored in the
  database.  Once your API endpoint has modified the profile, use this function to save
  the updated list of profiles.


Step 4: Edit profile by ID (nonexistent ID)
-------------------------------------------
Lastly, add an integration test and update your API endpoint so that a request to edit a
nonexistent profile will get a 404 response.

Step 5: Stretch Goals
---------------------
This step is optional.  If you're feeling confident and want to tackle some extra
challenges, give it a try 😺

- Try adding an API endpoint to create a new profile (e.g., ``POST /v1/profile``).
- Right now it's possible to update a profile to have an empty username, password, etc.
  Try using
  `Pydantic fields <https://docs.pydantic.dev/latest/concepts/fields/#string-constraints>`_
  to add some constraints to the request body for creating and editing profiles, so that
  those endpoints return a 400 response if the request body contains empty values.
- The built-in ``json`` library is a bit on the slow side.  Try using
  `orjson <https://pypi.org/project/orjson/>`_ instead.
