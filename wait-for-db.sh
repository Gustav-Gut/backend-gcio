#!/bin/sh
set -e

host="$1"
shift
cmd="$@"

echo "Esperando a que MariaDB esté disponible en $host:3306..."
while ! nc -z "$host" 3306; do
  sleep 1
done
echo "MariaDB ya está disponible en $host:3306, iniciando el comando..."
exec $cmd
