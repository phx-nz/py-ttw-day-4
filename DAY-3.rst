Day 3: Docker and Typer
=======================
Today we're going to expand on the concepts explored during yesterday's workshop by
creating a CLI interface for our profile management services.

We will also get our application running inside a Docker container, in preparation for
this afternoon's workshop.

Running the server
------------------
Starting today we'll be using a different command to run the server::

   pipenv run docker-start

.. tip::

   When the Docker container runs, it will mount your local codebase as a volume, so
   that as you make changes to your code, the server will automatically reload 😎

   Note that if you make any changes that would require a rebuild (e.g., add
   dependencies to ``Pipfile``), then you'll need to stop and restart the container.

To stop the Docker container, run the following command::

   pipenv run docker-stop

Exercise instructions
=====================
The goal of this morning's exercise is to add two CLI commands to your FastAPI
application using `Typer`_.

.. tip::

   If you get stuck at any point, you can check the ``day-3-solution`` branch, which
   contains a completed solution for the exercise.

Step 1: Get profile by ID (happy path)
--------------------------------------
When you run the following CLI command, the app should output the details for the
specified profile in JSON format:

   pipenv run app-cli profiles get {profile_id}

#. Create a new file under `src/cli/commands <./src/cli/commands>`_ named
   ``profiles.py``.  This file will hold all the CLI commands that you create under the
   ``profiles`` namespace.

#. Look at `src/cli/commands/generate.py <./src/cli/commands/generate.py>`_ to see how
   to create a new command (using the ``Typer`` class) and a new subcommand (using the
   ``Typer.command`` decorator).

#. Based on what you saw in
   `src/cli/commands/generate.py <./src/cli/commands/generate.py>`_, create a new
   ``profiles`` command, and a ``get`` subcommand under it.

   Don't worry about fetching profile data yet.  Just have your function output
   something like "Kia ora te ao!" so that you can verify it's working.

   .. tip::

      Your ``profiles.py`` file should look something like this:

      .. code-block:: py

         __all__ = ["app"]

         import typer

         app = typer.Typer(name="profiles")

         @app.command("get")
         def get_profile():
             print("Kia ora te ao!")

#. Just like when you created a new FastAPI router, you'll need to register your new
   command before you can invoke it from the command line.

   Open `src/cli/main.py <./src/cli/main.py>`_ and add a call to ``app.add_typer()`` to
   register your new command.

#. Test that your command is registered correctly by running the following::

      pipenv run app-cli profiles get

#. Before continuing, let's scaffold the integration test for your new command.  Create
   a new file under `test/integration/cli <./test/integration/cli>`_ named
   ``test_profiles.py``.

   .. important::

      The filename must start with ``test_`` in order for pytest to find it.

#. Look at
   `test/integration/cli/test_generate.py <./test/integration/cli/test_generate.py>`_
   to see how to create an integration test for CLI commands.

#. Based on what you saw in
   `test/integration/cli/test_generate.py <./test/integration/cli/test_generate.py>`_,
   create an integration test that invokes your CLI command and verifies that it outputs
   without error.

   .. tip::

      Your integration test should look something like this:

      .. code-block:: py

         from click.testing import Result

         from cli.pytest_utils import TestCliRunner

         def test_get_profile_happy_path(runner: TestCliRunner):
             result: Result = runner.invoke(["profiles", "get"])
             assert result.exception is None
             assert result.stdout == "Kia ora te ao!"

#. In order to retrieve profile details, your command needs to accept a
   `command-line argument <https://typer.tiangolo.com/tutorial/first-steps/#add-a-cli-argument>`_.
   Update your command so that it requires a ``profile_id`` argument.

#. That change should make your integration test fail, so the next step is to update the
   test to include a profile ID when it invokes your CLI command.

   .. tip::

      If you get a ``TypeError("object of type 'int' has no len()")``, make sure to pass
      the profile ID as a string, not an int.

      CLI arguments are always passed as a string (Typer converts the argument to
      an int before passing it along to your CLI command function).

#. Update your command so that it fetches the profile with the matching ID and outputs
   the profile data in JSON format.

   .. tip::

      You can use `jsonable_encoder() <https://fastapi.tiangolo.com/tutorial/encoder/>`_
      here, too.

   .. tip::

      The end result should look something like this:

      .. code-block:: py

         @app.command("get")
         def get_profile(profile_id: int):
             """
             Retrieves the profile with the specified ID and outputs the details in JSON
             format.

             :raises: ValueError if no such profile exists.
             """
             # Find the profile with the matching ID.
             # We can leverage what we wrote during yesterday's exercise.
             # Reusability FTW!
             profile: Profile = ProfileService.get_profile_by_id(profile_id)

             # Convert the model instance into a value that can be JSON-encoded.
             encoded_profile = jsonable_encoder(profile)

             # Finally, output the value in JSON format.
             print(json.dumps(encoded_profile, indent=2))

#. Finally, update your integration test so that it passes a valid profile ID to the
   command and checks for the correct JSON in ``stdout``.

   .. tip::

      Remember that you can use the ``profiles`` fixture in any of your unit or
      integration tests.

   .. tip::

      The end result should look something like this:

      .. code-block:: py

         def test_get_profile_happy_path(profiles: list[Profile], runner: TestCliRunner):
             """
             Fetching data for a valid profile.
             """
             target_profile: Profile = profiles[0]

             result: Result = runner.invoke(["profiles", "get", str(target_profile.id)])

             # Verify that the command completed successfully.
             assert result.exception is None

             # Verify that the result is valid JSON with the correct values.
             # We don't need (nor want) to check how the JSON is formatted (e.g.,
             # indentation, ordering, etc.), as that's an implementation detail.
             assert json.loads(result.stdout) == jsonable_encoder(target_profile)

Step 2: Get profile by ID (nonexistent ID)
------------------------------------------
That's our happy path sorted.  Next we need to handle an error case, where the user
requests a profile ID that doesn't exist.

#. Try running ``pipenv run app-cli profiles get 999`` and note the error you get.

#. This time, let's try a TDD approach.  Write an integration test that invokes your CLI
   command with an invalid Profile ID and checks that the command raises a
   ``ValueError``.

#. Now that you've got a red bar again, it's time to update your CLI command to make
   your integration test pass.

   .. tip::

      If you get stuck, you can check the ``day-3-solution`` branch.

Step 3: Update profile by ID (happy path)
-----------------------------------------
Getting complicated yet...or not complicated enough?  Let's make things even more
interesting by adding a CLI command to update a profile.

Because specifying the updated profile JSON on the command-line would get cumbersome
super fast, we'll instead put the JSON in a file and provide the file path to the
CLI command.

The invocation will look something like this::

   pipenv run app-cli profiles update 42 /path/to/data.json

Here are some hints to help you:

- Create a JSON file in `test/integration/cli/data <./test/integration/cli/data>`_ so
  that you can also use it in your integration tests.
- During yesterday's exercise you wrote the code to edit a profile (for the
  ``PUT /v1/profile/{profile_id}`` API endpoint) that you can reuse.
- Make sure to put ``assert result.exception is None`` early in your test, so that
  pytest will tell you if your command raised an exception.

Step 4: Update profile by ID (nonexistent ID)
---------------------------------------------
Lastly, add an integration test and update your CLI command so that it raises a
``ValueError`` if the user tries to edit a profile that doesn't exist.

Here are some hints to help you:

- After invoking the CLI command in your test, can check the exception:

  - Check the exception type: ``assert isinstance(result.exception, ValueError)``
  - Check the exception message; ``assert "999" in str(result.exception)``

Step 5: Stretch goals
---------------------
This step is optional.  If you're feeling confident and want to tackle some extra
challenges, give these a try 😺

- Try adding a CLI command to create a new profile (e.g.,
  ``pipenv run app-cli profiles create /path/to/data.json``).
- Get the CLI commands to validate the JSON data using Pydantic.

  - Hint: you can reuse the Pydantic model you created for
    ``PUT /v1/profile/{profile_id}``.

.. _Typer: https://typer.tiangolo.com
