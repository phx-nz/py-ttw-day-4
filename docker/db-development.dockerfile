FROM public.ecr.aws/docker/library/postgres:16-alpine

# Specify a root DB password so that we can initialise the database.  Literally, it just
# has to be set to a non-empty value -- we don't have to do anything with it :shrug:
#
# Normally hard-coding credentials into a dockerfile would be a big no-no, but we're
# only running Postgres in a container for local development.  In production, we'll
# provision a managed database service, with credentials in a vault or other secure
# parameter store.
ENV POSTGRES_PASSWORD=pecu7kee3riSh2aeduojah1Ohbiunga2afe4eis5aiJohquaiwookoh2peeb3koo

# See https://hub.docker.com/_/postgres/ ("Initialization scripts")
COPY db-init /docker-entrypoint-initdb.d
