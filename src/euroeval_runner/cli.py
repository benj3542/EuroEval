from __future__ import annotations
import os
import sys
import json
import urllib.request
import urllib.error
from typing import Optional, List
import typer
from prompt_toolkit import prompt
from rich import print
from rich.prompt import Confirm

from euroeval import Benchmarker

app = typer.Typer(add_completion=False)

def _split_csv(value: Optional[str]) -> Optional[List[str]]:
    if value is None or value.strip() == "":
        return None
    return [v.strip() for v in value.split(",") if v.strip()]

def _normalize_base_url(url: str) -> str:
    """Ensure URL includes /v1 exactly once; accept raw host or host/v1."""
    url = url.strip()
    if not url:
        return url
    # remove trailing slashes
    while url.endswith('/'):
        url = url[:-1]
    # append /v1 if missing
    if not url.endswith("/v1"):
        url = url + "/v1"
    return url

def _probe_models(api_base: str, api_key: Optional[str], timeout: float = 6.0) -> Optional[list]:
    """
    Optional: call GET {api_base}/models to sanity-check endpoint.
    Returns a list of model ids if available, else None.
    Never raises: converts errors to None.
    """
    url = api_base.rstrip("/") + "/models"
    req = urllib.request.Request(url, method="GET")
    if api_key:
        req.add_header("Authorization", f"Bearer {api_key}")
    req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status != 200:
                return None
            data = json.loads(resp.read().decode("utf-8"))
            # OpenAI format can be {"data":[{"id":...},...]} or similar
            if isinstance(data, dict) and isinstance(data.get("data"), list):
                return [m.get("id") for m in data["data"] if isinstance(m, dict) and "id" in m]
            return None
    except Exception:
        return None

@app.command()
def run(
    api_base: Optional[str] = typer.Option(None, help="Base URL to an OpenAI-compatible API (e.g., https://my-llm.example.com[/v1])"),
    api_key: Optional[str] = typer.Option(None, help="Bearer token for the endpoint (leave empty if not required)"),
    model: Optional[str] = typer.Option(None, help="Model id as your endpoint expects (e.g., my-model-13b)"),
    api_version: Optional[str] = typer.Option(None, help="Optional API version (if your server requires it)"),
    language: Optional[str] = typer.Option(None, help="Languages (comma-separated)"),
    task: Optional[str] = typer.Option(None, help="Tasks (comma-separated). Mutually exclusive with --dataset."),
    dataset: Optional[str] = typer.Option(None, help="Datasets (comma-separated). Mutually exclusive with --task."),
    batch_size: int = typer.Option(int(os.getenv("EUROEVAL_BATCH_SIZE", "32")), help="Batch size (default 32)"),
    results_dir: str = typer.Option("/workspace/results", help="Directory to write results JSONL"),
    force: bool = typer.Option(False, help="Re-evaluate even if results exist"),
    evaluate_test_split: bool = typer.Option(False, help="Evaluate test split"),
    verbose: bool = typer.Option(False, help="Verbose logging"),
    no_probe: bool = typer.Option(False, help="Skip the connectivity probe to /models"),
):
    """Run EuroEval against ANY OpenAI-compatible endpoint (self-hosted or personal)."""
    print("[bold cyan]EuroEval Runner[/bold cyan]")

    # -------- prompts kept intentionally generic --------
    if not api_base:
        api_base = prompt("API base URL (your personal endpoint, e.g., https://my-llm.example.com[/v1]): ")
    if api_key is None:
        api_key = prompt("API key/token (leave empty if not required): ", is_password=True) or None
    if not model:
        model = prompt("Model id (exact name your endpoint expects): ")

    # normalize /v1
    api_base = _normalize_base_url(api_base)

    # pick languages/tasks from env if not supplied
    if language is None:
        language = os.getenv("EUROEVAL_LANGS", "all")
    if task is None and dataset is None:
        task = os.getenv("EUROEVAL_TASKS", None)

    if task and dataset:
        print("[red]Error: --task and --dataset are mutually exclusive.[/red]")
        raise typer.Exit(code=2)

    os.makedirs(results_dir, exist_ok=True)
    os.chdir(results_dir)

    langs = None if language in (None, "", "all") else [s.strip() for s in language.split(",")]
    tasks = _split_csv(task)
    datasets = _split_csv(dataset)

    print(f"[green]Using[/green] api_base={api_base!r}, model={model!r}, languages={langs or 'all'}, tasks={tasks}, datasets={datasets}")

    # -------- optional connectivity probe (safe no-op if unsupported) --------
    if not no_probe:
        models = _probe_models(api_base, api_key)
        if models is not None:
            if model not in models:
                print(f"[yellow]Heads-up:[/yellow] /models responded but did not list {model!r}. "
                      "This may still be fine if your server hides models or uses another route.")
        else:
            print("[dim]Skipping model discovery (no /models or not reachable).[/dim]")

    cache_dir = os.getenv("EUROEVAL_CACHE_DIR", "/opt/euroeval_cache")

    bm = Benchmarker(
        progress_bar=True,
        save_results=True,
        language=langs or "all",
        batch_size=batch_size,
        api_key=api_key,
        api_base=api_base,
        api_version=api_version,
        cache_dir=cache_dir,
        force=force,
        verbose=verbose,
        evaluate_test_split=evaluate_test_split,
    )

    if not Confirm.ask("Start evaluation now?"):
        print("[yellow]Aborted by user.[/yellow]")
        raise typer.Exit(code=0)

    try:
        bm.benchmark(
            model=model,
            task=tasks if tasks else None,
            dataset=datasets if datasets else None,
        )
        print("[bold green]Done![/bold green] See results in:", os.getcwd())
    except Exception as e:
        print(f"[bold red]EuroEval failed:[/bold red] {e}")
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()
