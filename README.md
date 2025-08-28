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
  - [OpenRouter](#openrouter)  
  - [Groq](#groq)  
  - [LM Studio (local)](#lm-studio-local)  
- [Remote build in GitHub Actions → GHCR](#remote-build-in-github-actions--ghcr)  
  - [Pull the image (public vs private)](#pull-the-image-public-vs-private)  
- [Build-time dataset preloading (optional)](#buildtime-dataset-preloading-optional)  
- [Entrypoint, commands, and overrides](#entrypoint-commands-and-overrides)  
- [Troubleshooting](#troubleshooting)  

---

## Prerequisites

- **Docker Desktop** installed and running.  
- (For private images) a **GitHub Personal Access Token** (PAT) with `read:packages`.  
- An **OpenAI-compatible API** to call (see [Choose an LLM endpoint](#choose-an-llm-endpoint)).  

Repo layout (relevant bits):

docker/Dockerfile
scripts/entrypoint.sh
src/euroeval_runner/...
pyproject.toml

The contatiner exposes the CLI `euroeval-runner`. 

---

## Quick start (TL;DR)

**Pull the image built by CI** (example: repo `$USER/euroeval`):

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
  ghcr.io/benj3542/euroeval:latest
````
