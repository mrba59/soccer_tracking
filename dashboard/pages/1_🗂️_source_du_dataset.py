# --- robust path bootstrap (works for both /dashboard and /dashboard/pages) ---
import sys, os
from pathlib import Path
import streamlit as st  # ok to import st early here

THIS_FILE = Path(__file__).resolve()

def find_repo_root(start: Path) -> Path:
    """Ascend until we find a folder that contains 'dashboard/src'."""
    for anc in [start] + list(start.parents):
        if (anc / "dashboard" / "src").exists():
            return anc
    # Fallbacks: handle both cases
    if start.parent.name == "dashboard":       # .../soccer_tracking/dashboard/streamlit_app.py
        return start.parents[1]                # .../soccer_tracking
    if start.parent.name == "pages":           # .../dashboard/pages/1_*.py
        return start.parents[2]                # .../soccer_tracking
    return start.parents[1]                    # safest default

REPO_ROOT = find_repo_root(THIS_FILE)
DASH_DIR  = REPO_ROOT / "dashboard"
SRC_DIR   = DASH_DIR / "src"

# prepend to sys.path if needed
for p in (REPO_ROOT, DASH_DIR, SRC_DIR):
    p_str = str(p)
    if p_str not in sys.path:
        sys.path.insert(0, p_str)

# quick debug so we see what's happening on Streamlit Cloud
with st.expander("🔧 Import debug (bootstrap)"):
    st.write({
        "THIS_FILE": str(THIS_FILE),
        "REPO_ROOT": str(REPO_ROOT),
        "DASH_DIR": str(DASH_DIR),
        "SRC_DIR_exists": SRC_DIR.exists(),
        "SRC_DIR_list": [x.name for x in SRC_DIR.glob("*.py")] if SRC_DIR.exists() else "absent",
        "sys.path[:3]": sys.path[:3],
    })

# now the canonical import
from dashboard.src.paths import DATA_DIR, path_exists_debug


st.set_page_config(
    page_title="Soccer Stats - Source du dataset",
    page_icon="⚽",
    layout="centered",
)

st.title("🗂️ Source du dataset")

# --- Définition des fichiers (dans dashboard/src/top_view/) ---
ORIGINAL_CSV = DATA_DIR / "original_D_20220220_1_0000_0030.csv"
GNSS_CSV     = DATA_DIR / "gnss_G_20200220_1_0000_0030.csv"
KPT_JSON     = DATA_DIR / "drone_keypoints.json"

# (optionnel) un petit switch pour voir les chemins sur le cloud
with st.expander("🔧 Debug paths (optionnel)"):
    st.json(path_exists_debug(), expanded=False)

@st.cache_data(show_spinner="Chargement des données…")
def load_datas(original_csv: Path, gnss_csv: Path, kpt_json: Path):
    # Vérifs explicites pour des messages d’erreur lisibles dans le cloud
    if not original_csv.exists():
        raise FileNotFoundError(f"CSV introuvable: {original_csv}")
    if not gnss_csv.exists():
        raise FileNotFoundError(f"CSV introuvable: {gnss_csv}")
    if not kpt_json.exists():
        raise FileNotFoundError(f"JSON introuvable: {kpt_json}")

    original_data = pd.read_csv(original_csv, nrows=10, header=None)
    gnss_data     = pd.read_csv(gnss_csv,   nrows=10, header=None)
    with open(kpt_json, "r", encoding="utf-8") as f:
        key_point_data = json.load(f)

    return original_data, gnss_data, key_point_data

try:
    original_data, gnss_data, key_point_data = load_datas(ORIGINAL_CSV, GNSS_CSV, KPT_JSON)
except Exception as e:
    import traceback
    st.error("❌ Erreur lors du chargement des données.")
    st.code("".join(traceback.format_exc()))
    st.stop()

st.header("Dataset originel")
st.dataframe(original_data, hide_index=True)

st.header("GNSS Dataset")
st.dataframe(gnss_data, hide_index=True)

st.header("Drone Keypoint")
st.json(key_point_data, expanded=True)
