#!/usr/bin/env bash

set -euo pipefail
IFS=$'\n\t'

docker-compose build
docker-compose push
