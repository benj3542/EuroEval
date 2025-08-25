#!/usr/bin/env bash
set -euo pipefail

IMAGE="${1:-euroeval-runner:latest}"

docker run --rm -it \
  --gpus all \
  -v "$(pwd)/results:/workspace/results" \
  -e EUROEVAL_LANGS="da,en" \
  -e EUROEVAL_TASKS="sentiment-classification" \
  "$IMAGE"
