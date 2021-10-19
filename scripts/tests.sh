#! /bin/sh
set -e

if [ -f .env ]
then
  export $(cat .env | xargs)
fi
echo "env variables exported"
printenv

bash scripts/build.sh

alias python="poetry run python"

# The following tests can be added if needed
#python -m black tests/
#python -m isort tests/
#python -m flake8 tests/ 

python -m pytest -rx tests/