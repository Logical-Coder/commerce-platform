#!/bin/sh
echo "Waiting for MySQL at ${DB_HOST:-mysql}:${DB_PORT:-3306}..."

while ! nc -z "${DB_HOST:-mysql}" "${DB_PORT:-3306}"; do
  sleep 1
done

echo "MySQL is ready!"