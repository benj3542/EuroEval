#!/usr/bin/env bash
set -euo pipefail

# Ensure results dir exists and is writable
mkdir -p /workspace/results || true
chmod -R 777 /workspace/results || true

# If user passed a non-interactive command, run it
if [[ $# -gt 0 ]]; then
  exec "$@"
fi

# Otherwise, run the EuroEval runner CLI (interactive)
exec euroeval-runner run
