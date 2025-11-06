# dashboard/src/paths.py
from pathlib import Path

# Ce fichier est dans .../dashboard/src/
APP_DIR  = Path(__file__).resolve().parents[1]        # .../dashboard
REPO_DIR = APP_DIR.parent                              # .../soccer_tracking

DATA_DIR  = APP_DIR / "src" / "top_view"              # .../dashboard/src/top_view
STATS_DIR = APP_DIR / "src" / "stats"                 # .../dashboard/src/stats

def path_exists_debug():
    return {
        "REPO_DIR": str(REPO_DIR),
        "APP_DIR": str(APP_DIR),
        "DATA_DIR": str(DATA_DIR),
        "DATA_LIST": [p.name for p in DATA_DIR.glob("*")],
    }
