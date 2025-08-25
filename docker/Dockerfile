# CUDA base (fine on Mac; we’ll build for linux/amd64 via buildx)
FROM nvidia/cuda:12.2.0-runtime-ubuntu22.04

# ---- Workdir ----
WORKDIR /workspace

# ---- Install Miniforge (no apt needed) ----
# Use Docker's ADD to fetch the installer directly
ADD https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh /tmp/Miniforge.sh
RUN bash /tmp/Miniforge.sh -b -p /opt/conda && rm -f /tmp/Miniforge.sh
ENV PATH="/opt/conda/bin:${PATH}"

# Create a clean env with Python 3.11 and pip
ARG PYTHON_VERSION=3.11
RUN conda update -n base -c conda-forge --yes conda \
 && conda create -n eval --yes python=${PYTHON_VERSION} pip \
 && conda clean -afy
# From here on, use the env's python/pip
ENV PATH="/opt/conda/envs/eval/bin:${PATH}"

# ---- Cache locations (baked into image) ----
ENV EUROEVAL_CACHE_DIR=/opt/euroeval_cache \
    HF_HOME=/opt/hf_home \
    HF_DATASETS_CACHE=/opt/hf_home/datasets \
    HF_HUB_CACHE=/opt/hf_home/hub \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1
RUN mkdir -p "$EUROEVAL_CACHE_DIR" "$HF_DATASETS_CACHE" "$HF_HUB_CACHE" \
 && chmod -R 777 /opt  # writable in container

# ---- Copy project ----
COPY pyproject.toml README.md /workspace/
COPY src /workspace/src
COPY scripts /workspace/scripts

# ---- Install project (pulls euroeval[all]) ----
RUN pip install --upgrade pip && pip install .

# ---- Build-time selection of languages/tasks to pre-cache ----
ARG EUROEVAL_LANGS="da,en"
ARG EUROEVAL_TASKS="sentiment-classification"
ENV EUROEVAL_LANGS=${EUROEVAL_LANGS}
ENV EUROEVAL_TASKS=${EUROEVAL_TASKS}

# ---- Preload datasets to cache (kept in layer) ----
RUN python -m euroeval_runner.preload_datasets

# ---- Results dir ----
RUN mkdir -p /workspace/results && chmod -R 777 /workspace/results

# ---- Entrypoint ----
COPY .dockerignore /workspace/.dockerignore
RUN chmod +x /workspace/scripts/entrypoint.sh
ENTRYPOINT ["/workspace/scripts/entrypoint.sh"]
