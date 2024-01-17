#!/bin/sh
echo "Waiting for postgres..."

while ! nc -z db 5432; do
  sleep 0.1
done

echo "PostgreSQL started"


command=$(echo "$@" | awk '{print $1}')

if [ "$command" != "celery" ]; then
  echo "Applying migrations"
  alembic upgrade head
fi

echo "Waiting for rabbitmq..."

while ! nc -z rabbitmq 5672; do
  sleep 0.1
done

echo "RabbitMQ started"

exec "$@"