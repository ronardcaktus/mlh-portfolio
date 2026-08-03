#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Find and run all tests.
if [ -n "${VIRTUAL_ENV:-}" ] && [ -x "$VIRTUAL_ENV/bin/python" ]; then
	PYTHON_BIN="$VIRTUAL_ENV/bin/python"
elif [ -x "$SCRIPT_DIR/python3-virtualenv/bin/python" ]; then
	PYTHON_BIN="$SCRIPT_DIR/python3-virtualenv/bin/python"
elif [ -x "$SCRIPT_DIR/.venv/bin/python" ]; then
	PYTHON_BIN="$SCRIPT_DIR/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
	PYTHON_BIN="$(command -v python3)"
else
	echo "Error: no Python 3 interpreter found."
	echo "Create a virtualenv (python3 -m venv python3-virtualenv) or install Python 3."
	exit 1
fi

"$PYTHON_BIN" -m unittest discover -s "$SCRIPT_DIR/tests" -p "test_*.py" -v