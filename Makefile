IMAGE ?= euroeval-runner
TAG ?= latest
DOCKERFILE ?= docker/Dockerfile

# Default languages/tasks (can override via `make build LANGS=... TASKS=...`)
LANGS ?= da,en
TASKS ?= sentiment-classification

# Build the Docker image
build:
	docker build \
		--build-arg EUROEVAL_LANGS="$(LANGS)" \
		--build-arg EUROEVAL_TASKS="$(TASKS)" \
		-t $(IMAGE):$(TAG) \
		-f $(DOCKERFILE) .

# Run interactively (mount ./results)
run:
	docker run --rm -it \
		--gpus all \
		-v "$(PWD)/results:/workspace/results" \
		$(IMAGE):$(TAG)

# Run non-interactive example (needs env vars)
run-ci:
	docker run --rm \
		-v "$(PWD)/results:/workspace/results" \
		-e EUROEVAL_LANGS="$(LANGS)" \
		-e EUROEVAL_TASKS="$(TASKS)" \
		$(IMAGE):$(TAG) \
		euroeval-runner run \
			--api-base "$$API_BASE" \
			--api-key "$$API_KEY" \
			--model "$$MODEL"

# Clean cached build layers
clean:
	docker system prune -f

.PHONY: build run run-ci clean
