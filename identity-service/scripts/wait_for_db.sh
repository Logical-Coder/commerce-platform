#!/bin/sh

echo "⏳ Waiting for MySQL..."

# Loop until MySQL is reachable
while ! nc -z db 3306; do
  sleep 1
done

echo "✅ MySQL is ready!"