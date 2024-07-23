#!/usr/bin/env bash

set -euo pipefail
IFS=$'\n\t'

directory=${1:-./app}

printf '%*s\n' "${COLUMNS:-$(tput cols)}" '' | tr ' ' =
echo "Reformatting code with black"
printf '%*s\n' "${COLUMNS:-$(tput cols)}" '' | tr ' ' =

black "$directory"

#printf '%*s\n' "${COLUMNS:-$(tput cols)}" '' | tr ' ' =
#echo "Reordering imports with isort"
#printf '%*s\n' "${COLUMNS:-$(tput cols)}" '' | tr ' ' =
#
#isort "$directory"

printf '%*s\n' "${COLUMNS:-$(tput cols)}" '' | tr ' ' =
echo "Reviewing typing with mypy"
printf '%*s\n' "${COLUMNS:-$(tput cols)}" '' | tr ' ' =

mypy "$directory"

printf '%*s\n' "${COLUMNS:-$(tput cols)}" '' | tr ' ' =
echo "Reviewing code style with flake8"
printf '%*s\n' "${COLUMNS:-$(tput cols)}" '' | tr ' ' =

flake8 "$directory"