#!/usr/bin/env bash
# See https://hub.docker.com/_/postgres/ ("Initialization scripts")
set -ev

echo "CREATE DATABASE $DB_DATABASE WITH ENCODING='UTF-8';" | psql -v ON_ERROR_STOP=1
echo "CREATE USER $DB_USER;" | psql -v ON_ERROR_STOP=1
echo "ALTER ROLE $DB_USER PASSWORD '$DB_PASSWORD';" | psql -v ON_ERROR_STOP=1

# IMPORTANT: Make sure this command references the correct database
# ``(-d "$DB_DATABASE")``, or else you'll get 'permission denied' when trying to run
# migrations!
#
# In Postgres v14 and earlier, the `CREATE` privilege was granted to `PUBLIC`
# automatically, but that was fixed in v15.
# :see: https://www.postgresql.org/docs/release/15.0/
echo "GRANT ALL PRIVILEGES ON SCHEMA \"public\" TO $DB_USER;" | psql -d "$DB_DATABASE" -v ON_ERROR_STOP=1
