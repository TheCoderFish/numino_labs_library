#!/bin/bash
# Simple wrapper to run the seeder using the virtualenv Python
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
SCRIPT="$DIR/scripts/seed_db.py"

if [ ! -f "$SCRIPT" ]; then
  echo "Seeder script not found: $SCRIPT"
  exit 1
fi

if [ -f "$DIR/venv/bin/activate" ]; then
  source "$DIR/venv/bin/activate"
fi

python "$SCRIPT"
