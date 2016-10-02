#!/usr/bin/env bash

set -e

cd ..

. ./VENV/bin/activate

cd kippo

cd $(dirname $0)

twistd --version

echo "Starting kippo in the background..."
twistd -y kippo.tac -l log/kippo.log --pidfile kippo.pid