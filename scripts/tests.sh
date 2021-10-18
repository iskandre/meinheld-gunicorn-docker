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
#poetry run find . -name '*.py' -exec pyupgrade --py36-plus {} +
#python -m black tests/
#python -m isort tests/
#python -m flake8 tests/ 
python -m pytest tests/