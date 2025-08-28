# EuroEval Runner (Docker + OpenAI-compatible APIs)

Run the **EuroEval** LLM benchmark in a reproducible Docker image against any **OpenAI-compatible** endpoint (OpenAI, OpenRouter, Groq, Hugging Face Inference Endpoints, LM Studio local server, etc.).

- Works the same on macOS/Windows/Linux  
- Build in the cloud (GitHub Actions → GHCR) and just pull locally  
- Run interactively (prompts) or fully non-interactive (CLI flags)  
- Optional dataset preloading into the image at build time  
- Caches persist across runs via Docker volumes  

---

## Table of contents

- [Prerequisites](#prerequisites)  
- [Quick start (TL;DR)](#quick-start-tldr)  
- [Local build (optional)](#local-build-optional)  
- [Run the container](#run-the-container)  
  - [Interactive](#interactive)  
  - [Non-interactive](#non-interactive)  
  - [Persist caches between runs](#persist-caches-between-runs)  
  - [Apple Silicon (M1/M2/M3) note](#apple-silicon-m1m2m3-note)  
- [Choose an LLM endpoint](#choose-an-llm-endpoint)  
  - [OpenAI](#openai)   
- [Remote build in GitHub Actions → GHCR](#remote-build-in-github-actions--ghcr)  
  - [Pull the image (public vs private)](#pull-the-image-public-vs-private)  
- [Build-time dataset preloading (optional)](#buildtime-dataset-preloading-optional)  
- [Entrypoint, commands, and overrides](#entrypoint-commands-and-overrides)   

---

## Prerequisites

- **Docker Desktop** installed and running.  
- (For private images) a **GitHub Personal Access Token** (PAT) with `read:packages`.  
- An **OpenAI-compatible API** to call (see [Choose an LLM endpoint](#choose-an-llm-endpoint)).  

Repo layout (relevant bits):
- docker/Dockerfile
- scripts/entrypoint.sh
- src/euroeval_runner/...
- pyproject.toml

The contatiner exposes the CLI `euroeval-runner`. 

---

## Quick start (TL;DR)

**Pull the image built by CI** (example: repo `benj3542/euroeval`):

```bash
# If the package is private: log in to GHCR once
echo <YOUR_GHCR_PAT> | docker login ghcr.io -u <your-github-username> --password-stdin

# Apple Silicon? Pull the amd64 image (works via emulation)
docker pull --platform=linux/amd64 ghcr.io/benj3542/euroeval:latest

```

**Run it** (interactive prompts; results saved to `./results/`):

```bash
mkdir -p results
docker run --rm -it --platform=linux/amd64 \
  -v "$(pwd)/results:/workspace/results" \
  ghcr.io/$USER/euroeval:latest
```

**or non-interactive** (example: OpenAI): 

```bash
export OPENAI_API_KEY=sk-...
docker run --rm --platform=linux/amd64 \
  -v "$(pwd)/results:/workspace/results" \
  ghcr.io/benj3542/euroeval:latest \
  euroeval-runner \
    --api-base "https://api.openai.com/v1" \
    --api-key  "$OPENAI_API_KEY" \
    --model    "gpt-4o-mini" \
    --language "da" \
    --task     "sentiment-classification" \
    --batch-size 1
```

## Local build (optinal)
I recommend remote builds (GitHub Actions) to avoid local disk/mirror issues, but you can build locally if you want.

```bash
# from repo root
docker build -t euroeval-runner:local -f docker/Dockerfile .
# or with build args:
docker build -t euroeval-runner:local -f docker/Dockerfile \
  --build-arg PRELOAD_DATASETS=false \
  --build-arg EUROEVAL_LANGS="da" \
  --build-arg EUROEVAL_TASKS="sentiment-classification" \
  .
```

Run the locally built image: 

```bash
mkdir -p results
docker run --rm -it \
  -v "$(pwd)/results:/workspace/results" \
  euroeval-runner:local
```

## Run the container

### Interactive 
Prompts for API base, key and model: 

```bash 
mkdir -p results
docker run --rm -it --platform=linux/amd64 \
  -v "$(pwd)/results:/workspace/results" \
  ghcr.io/<owner>/<repo>:<tag>
```

### Non-interactive
Pass everything via flags: 

```bash 
docker run --rm --platform=linux/amd64 \
  -v "$(pwd)/results:/workspace/results" \
  ghcr.io/<owner>/<repo>:<tag> \
  euroeval-runner \
    --api-base "https://<your-endpoint>/v1" \
    --api-key  "<YOUR_TOKEN>" \
    --model    "<provider/model-id>" \
    --language "da" \
    --task     "sentiment-classification" \
    --batch-size 1
```

Outputs: `results/euroeval_benchmark_results.jsonl`

### Persist caches between runs
If you didn't bake datasets into the image, the first run may download them. Keep them across runs: 

```bash
docker volume create euroeval_cache
docker volume create euroeval_hf

docker run --rm -it --platform=linux/amd64 \
  -v "$(pwd)/results:/workspace/results" \
  -v euroeval_cache:/opt/euroeval_cache \
  -v euroeval_hf:/opt/hf_home \
  ghcr.io/<owner>/<repo>:<tag>
```
### Apple Silicon (M1, M2, M3) note

If the image was built for `linux/amd64`, pull/run with the platform flag (Docker will emulate transparently): 

```bash 
docker pull  --platform=linux/amd64 ghcr.io/<owner>/<repo>:<tag>
docker run   --platform=linux/amd64 ghcr.io/<owner>/<repo>:<tag> ...
```

## Choose an LLM endpoint 

All of these are OpenAI-compatible (same `/v1/chat/completions`shape). 

### OpenAI**

```bash
export OPENAI_API_KEY=sk-...
docker run --rm --platform=linux/amd64 \
  -v "$(pwd)/results:/workspace/results" \
  ghcr.io/<owner>/<repo>:<tag> \
  euroeval-runner \
    --api-base "https://api.openai.com/v1" \
    --api-key  "$OPENAI_API_KEY" \
    --model    "gpt-4o-mini" \
    --language "da" \
    --task     "sentiment-classification" \
    --batch-size 1
```

## Remote build in GitHub Actions -> GHCR

This repo includes a workflow `.github/workflows/docker-build.yml` that:
- builds the Docker image on every push to `main` (tags `:latest`and `:sha-...`)
- pushes to **GitHub Container Registry (GHCR)** at `ghcr.io/<owner>/<repo>`

**Trigger manual build** (with inputs):
- GutHub -> Actions -> *Build and Publish Docker Image* -> Run workflow 
- You can set: 
  - image tag 
  - whether to preload datasets (see next section)
  - langs/tasks or explicit datasets to preload

### Pull the image (public vs private)

**Public**

```bash 
docker pull ghcr.io/<owner>/<repo>:latest
```

**Private**

```bash
echo <YOUR_GHCR_PAT> | docker login ghcr.io -u <your-username> --password-stdin
docker pull ghcr.io/<owner>/<repo>:latest
```

*Apple Silicon?* add `--platform=linux/amd64`to both `pull` and `run`.

## Build-time dataset preloading (optional)

The Dockerfile supports these build args: 
- `PRELOAD_DATASETS` (`true|false`, default `false`)
- `EUROEVAL_LANGS`(e.g., `"da,en"`)
- `EUROEVAL_TASKS` (e.g., `"sentiment-classification"`)
- `EUROEVAL_DATASETS`(comma-separated explicit dataset ids; overrides tasks if set)

**CI default** is **no preloading** (keeps images small and reliable to build). 
To publish a **prewarmed** image, run the workflow manually with: 
- `PRELOAD_DATASETS=true`
- set `EUROEVAL_DATASETS=<exact_dataset_id>`**or** set `EUROEVAL_LANGS` + `EUROEVAL_TASKS`. 

## ENTRYpoint, commands, and overrides 

The image starts at `scripts/entrypoint.sh`, which runs the CLI. Depending in the CLI version: 
- If `euroeval-runner`has no `run` subcommand, the entrypoint runs `euroeval-runner`. 
- If yours needs direct control, override the entrypoint: 

```bash
docker run --rm -it --entrypoint euroeval-runner ghcr.io/<owner>/<repo>:<tag> --help
```

You can also pass a full command after the image name; entrypoint will `exec "$@"`if provided. 


