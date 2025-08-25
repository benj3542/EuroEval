# euroeval-docker-runner

A tiny wrapper that builds a Docker image with [EuroEval] pre-installed and dataset
artifacts pre-cached. At runtime it asks for an **OpenAI-compatible API base URL**
(e.g., a Hugging Face router or self-hosted TGI Messages API), an **API key**, and a
**model id**, then kicks off EuroEval.

- EuroEval docs & CLI usage: see the official repo and docs. :contentReference[oaicite:0]{index=0}
- The `Benchmarker` supports `api_base` / `api_key`, so we can evaluate models served
  behind OpenAI-compatible endpoints. :contentReference[oaicite:1]{index=1}

## Quick start

```bash
# 1) Build (choose languages/tasks to pre-cache to control image size)
docker build \
  --build-arg EUROEVAL_LANGS="da,en" \
  --build-arg EUROEVAL_TASKS="sentiment-classification,topic-classification" \
  -t euroeval-runner:latest \
  -f docker/Dockerfile .

# 2) Run (interactive) – mounts ./results to collect outputs
docker run --rm -it \
  --gpus all \
  -e EUROEVAL_LANGS="da,en" \
  -e EUROEVAL_TASKS="sentiment-classification" \
  -v "$(pwd)/results:/workspace/results" \
  euroeval-runner:latest
