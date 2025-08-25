# GPU-enabled base (works fine even if you run CPU-only; CUDA libs just sit there)
FROM nvidia/cuda:12.2.0-runtime-ubuntu22.04

# ---- System deps ----
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.11 python3.11-venv python3.11-dev \
    build-essential git curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# ---- Workdir ----
WORKDIR /workspace

# ---- Python venv ----
RUN python3.11 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --upgrade pip

# ---- Cache locations (baked into image) ----
ENV EUROEVAL_CACHE_DIR=/opt/euroeval_cache
ENV HF_HOME=/opt/hf_home
ENV HF_DATASETS_CACHE=/opt/hf_home/datasets
ENV HF_HUB_CACHE=/opt/hf_home/hub

RUN mkdir -p $EUROEVAL_CACHE_DIR $HF_DATASETS_CACHE $HF_HUB_CACHE \
 && chmod -R 777 /opt  # make writable for non-root runs

# ---- Copy project ----
COPY pyproject.toml README.md /workspace/
COPY src /workspace/src
COPY scripts /workspace/scripts

# ---- Install project (this pulls euroeval[all]) ----
RUN pip install .

# ---- Build-time selection of languages/tasks to pre-cache ----
ARG EUROEVAL_LANGS="da,en"
ARG EUROEVAL_TASKS="sentiment-classification"
ENV EUROEVAL_LANGS=${EUROEVAL_LANGS}
ENV EUROEVAL_TASKS=${EUROEVAL_TASKS}

# ---- Preload datasets to cache (kept in layer) ----
RUN python -m euroeval_runner.preload_datasets

# ---- Runtime defaults ----
ENV PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Results directory inside container (mount this out on run)
RUN mkdir -p /workspace/results && chmod -R 777 /workspace/results

# ---- Entrypoint ----
COPY .dockerignore /workspace/.dockerignore
RUN chmod +x /workspace/scripts/entrypoint.sh
ENTRYPOINT ["/workspace/scripts/entrypoint.sh"]
