##
# Define our base image.  Note Python version and OS (alpine).
FROM public.ecr.aws/docker/library/python:3.12-alpine AS base

##
# Build dependencies in a Docker image, to avoid any potential incompatibilities with
# the host's OS.
FROM base as builder
WORKDIR /app

# Create a virtualenv so that it's easy to copy dependencies into the app image.
# Otherwise everything would get installed in `/usr/local`, which gets messy.
ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv $VIRTUAL_ENV
# https://pythonspeed.com/articles/activate-virtualenv-dockerfile/
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install dependencies into the virtualenv.
# Note that we pass the `--deploy` flag to abort if Pipfile.lock is out-of-date.
COPY ../Pipfile Pipfile.lock ./
RUN pip install pipenv && pipenv install --deploy

##
# Create the application image.
FROM base
WORKDIR /app

# Copy virtualenv files from the builder image.
# For consistency we'll use a virtualenv in the application image, too.
ENV VIRTUAL_ENV=/opt/venv
COPY --from=builder $VIRTUAL_ENV $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Instead of copying code files into the image, we'll define a volume that maps to the
# codebase in the host's filesystem.  That way, any changes to your code will
# automatically trigger uvicorn to restart.
VOLUME ["/app"]
ENV PYTHONPATH="/app/src:$PYTHONPATH"

# Prevent `pipenv run` from overwriting environment variables from `.env`.
# https://pipenv.pypa.io/en/latest/shell/#automatic-loading-of-env
ENV PIPENV_DONT_LOAD_ENV=1

# Configure the app for development mode.
# See `src/services/config.py` for more info.
ENV PY_ENV="development"

# Expose port 8000, so that uvicorn can receive external requests.
#
# On your development system, you can access the app at http://localhost:8000
#
# Note that when we deploy to the cloud we'll put a reverse proxy (e.g., load balancer)
# in front of the container, which will handle port forwarding, TLS, etc., so even in
# production we can keep the port number set to 8000 here.
EXPOSE 8000

# This is the command that will run the server (uvicorn) process when the container
# starts.
# Note that we also specify `--host 0.0.0.0` so that the process can listen for external
# traffic (you'll connect to the container via localhost, but from the container's point
# of view, your request is coming from an external system).
CMD ["pipenv", "run", "dev-server", "--host", "0.0.0.0"]
