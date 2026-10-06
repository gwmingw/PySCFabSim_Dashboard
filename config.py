import os
from pathlib import Path


APP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIR.parent
configured_results_dir = os.environ.get("PYSCFABSIM_RESULTS_DIR", "").strip()
workspace_results_dir = PROJECT_ROOT / "outputs" / "PySCFabSim_baseline"
demo_results_dir = APP_DIR / "examples"
is_vercel = os.environ.get("VERCEL") == "1"

if configured_results_dir:
    DEFAULT_RESULTS_DIR = Path(configured_results_dir).expanduser().resolve()
elif not is_vercel and workspace_results_dir.is_dir() and any(workspace_results_dir.glob("*.json")):
    DEFAULT_RESULTS_DIR = workspace_results_dir.resolve()
else:
    DEFAULT_RESULTS_DIR = demo_results_dir.resolve()

HOST = "127.0.0.1"
PORT = 8050

