import json
from pathlib import Path

import pandas as pd
import streamlit as st

from dashboard.src.path import DATA_DIR, path_exists_debug

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
