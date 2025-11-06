import json
from pathlib import Path

import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, ColumnsAutoSizeMode

# --- Import des chemins robustes (paths.py recommandé) ---
try:
    from dashboard.src.paths import DATA_DIR, STATS_DIR, path_exists_debug
except ModuleNotFoundError:
    from dashboard.src.path import DATA_DIR, STATS_DIR, path_exists_debug  # fallback si besoin

st.set_page_config(
    page_title="Soccer Stats - Liste des événements",
    page_icon="📄",
    layout="wide",
)

st.title("📄 Liste des événements")

# --- FICHIERS DANS dashboard/src/... ---
PASSES_JSON = STATS_DIR / "passes.json"
VIDEO_2D_FULL = DATA_DIR / "full_game_2D_passe.mp4"

with st.expander("🔧 Debug paths (optionnel)"):
    st.json({
        **path_exists_debug(),
        "PASSES_JSON": str(PASSES_JSON),
        "VIDEO_2D_FULL": str(VIDEO_2D_FULL),
        "PASSES_JSON_exists": PASSES_JSON.exists(),
        "VIDEO_2D_FULL_exists": VIDEO_2D_FULL.exists(),
    }, expanded=False)

@st.cache_data(show_spinner="Chargement des données…")
def load_datas(passes_path: Path) -> pd.DataFrame:
    if not passes_path.exists():
        raise FileNotFoundError(f"JSON introuvable: {passes_path}")
    with open(passes_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    df = pd.json_normalize(data, "actions")

    # Habillage équipes (bleu/rouge) + métriques en secondes (FPS=30)
    df["team_passeur"] = df["team_passeur"].apply(lambda x: "🔵" if int(x) == 0 else "🔴")
    df["team_receveur"] = df["team_receveur"].apply(lambda x: "🔵" if int(x) == 0 else "🔴")

    # (Ré)introduire la colonne succeed en icône pour cohérence avec l’affichage plus bas
    # Si ta source est déjà bool/0-1, on mappe explicitement
    def succeed_to_icon(v):
        try:
            return "🗹" if (bool(v) or int(v) == 1) else "☐"
        except Exception:
            return "☐"

    df["succeed"] = df["succeed"].apply(succeed_to_icon)

    # Timecodes en secondes (start/end en index d'image à 30 FPS)
    df["second_start"] = df["start"].apply(lambda x: round(float(x) / 30.0, 2))
    df["second_duration"] = df.apply(lambda r: round((float(r["end"]) - float(r["start"])) / 30.0, 2), axis=1)

    return df

@st.cache_data(show_spinner=False)
def load_video_bytes(path: Path) -> bytes | None:
    if not path.exists():
        return None
    with open(path, "rb") as f:
        return f.read()

# --- Charger les données ---
try:
    datas = load_datas(PASSES_JSON)
except Exception as e:
    import traceback
    st.error("❌ Erreur lors du chargement des événements.")
    st.code("".join(traceback.format_exc()))
    st.stop()

# Filtrer sur les passes seulement
datas = datas[datas["type"] == "passe"].copy()

# --- AgGrid ---
display_cols = [
    "start", "end", "id", "passeur", "receveur", "team_passeur", "team_receveur",
    "longueur", "speed", "nb_player_elimine", "passe_in_last_30m",
    "in_surface_reparation", "succeed", "team", "second_start", "second_duration",
]

gb = GridOptionsBuilder.from_dataframe(datas[display_cols])
gb.configure_selection(selection_mode="single", use_checkbox=True)
gb.configure_side_bar()
gridOptions = gb.build()

grid = AgGrid(
    datas,
    gridOptions=gridOptions,
    height=360,
    columns_auto_size_mode=ColumnsAutoSizeMode.FIT_ALL_COLUMNS_TO_VIEW,
    theme="alpine",
)

selected_row = grid.get("selected_rows", [])

if selected_row:
    row = selected_row[0]
    # start_time pour vidéo (en secondes) –1s de marge, min 0
    start_time = max(int(row.get("second_start", 0)) - 1, 0)

    col1, col2 = st.columns(2, gap="large")

    with col1:
        video_bytes = load_video_bytes(VIDEO_2D_FULL)
        if video_bytes is None:
            st.error(f"Vidéo introuvable: {VIDEO_2D_FULL.name}")
        else:
            st.video(video_bytes, start_time=start_time, format="video/mp4")

    with col2:
        st.subheader("Détails de l'événement")
        st.write(f"Début : {row.get('second_start', '?')} s")
        st.write(f"Durée : {row.get('second_duration', '?')} s")
        st.write(f"Type : {row.get('type', '?')}")
        passeur = row.get("passeur", "?")
        receveur = row.get("receveur", "?")
        tp = row.get("team_passeur", "")
        tr = row.get("team_receveur", "")
        succeed_icon = row.get("succeed", "☐")

        if succeed_icon == "🗹":
            st.write(f"Joueur : n°{passeur} {tp} ⟶ n°{receveur} {tr}")
            st.write(
                "<span style='background:green; color:white; padding:5px; border-radius:10px;'>Réussi</span>",
                unsafe_allow_html=True,
            )
        else:
            st.write(f"Joueur : n°{passeur} {tp}")
            st.write(
                "<span style='background:red; color:white; padding:5px; border-radius:10px;'>Échec</span>",
                unsafe_allow_html=True,
            )
