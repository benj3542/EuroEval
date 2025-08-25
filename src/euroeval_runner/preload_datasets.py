"""
Pre-cache EuroEval datasets for selected languages/tasks
using only the public API (Benchmarker).
"""

import os
import termcolor

# --- Patch EuroEval color issue ---
# EuroEval sometimes asks for "light_blue", which isn't in termcolor.
if "light_blue" not in termcolor.COLORS:
    termcolor.COLORS["light_blue"] = termcolor.COLORS["cyan"]

from rich import print
from euroeval import Benchmarker


def _env_csv(name: str):
    val = os.getenv(name, "").strip()
    if not val:
        return None
    return [x.strip() for x in val.split(",") if x.strip()]


def get_cache_dir() -> str:
    """Pick a cache dir that works both inside Docker and locally."""
    default_dir = os.getenv("EUROEVAL_CACHE_DIR", "/opt/euroeval_cache")

    try:
        os.makedirs(default_dir, exist_ok=True)
        test_file = os.path.join(default_dir, ".write_test")
        with open(test_file, "w") as f:
            f.write("ok")
        os.remove(test_file)
        return default_dir
    except Exception:
        # Fall back to local cache dir
        fallback = "./cache"
        os.makedirs(fallback, exist_ok=True)
        print(f"[yellow]Permission denied for {default_dir}, using {fallback} instead[/yellow]")
        return fallback


def main() -> None:
    langs = _env_csv("EUROEVAL_LANGS") or "all"
    tasks = _env_csv("EUROEVAL_TASKS")

    cache_dir = get_cache_dir()
    print(f"[cyan]Priming datasets[/cyan] langs={langs}, tasks={tasks or 'all'}, cache_dir={cache_dir}")

    bm = Benchmarker(
        language=langs,
        cache_dir=cache_dir,
        progress_bar=True,
        save_results=False,  # don’t save result files during preload
        api_base="http://localhost:9999",  # dummy
        api_key="dummy",                   # dummy
    )

    try:
        bm.benchmark(
            model="dummy-model",
            task=tasks if tasks else None,
        )
    except Exception as e:
        # The dataset downloads happen before model calls,
        # so this error is expected and harmless.
        print(f"[yellow]Preload finished with expected error[/yellow]: {e}")

    print("[bold green]Datasets cached successfully![/bold green]")


if __name__ == "__main__":
    main()
