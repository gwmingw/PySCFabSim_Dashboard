import os
from pathlib import Path


APP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIR.parent
DEFAULT_RESULTS_DIR = Path(
    os.environ.get(
        "PYSCFABSIM_RESULTS_DIR",
        str(PROJECT_ROOT / "outputs" / "PySCFabSim_baseline"),
    )
).expanduser().resolve()
HOST = "127.0.0.1"
PORT = 8050

