#!/bin/sh

until pg_isready -h postgres -U rocket_user -d rocket_db; do
  echo "Waiting for PostgreSQL to become available..."
  sleep 2
done
echo "PostgreSQL is ready!"