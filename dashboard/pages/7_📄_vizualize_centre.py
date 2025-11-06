# dashboard/pages/7_📄_liste_des_centres.py
from pathlib import Path
import json
import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, ColumnsAutoSizeMode

# ==== Chemins robustes (paths.py recommandé, path.py en fallback) ====
try:
    from dashboard.src.paths import DATA_DIR, STATS_DIR, path_exists_debug
except ModuleNotFoundError:
    from dashboard.src.path import DATA_DIR, STATS_DIR, path_exists_debug  # fallback temporaire

st.set_page_config(
    page_title="Soccer Stats - Liste des centres",
    page_icon="📄",
    layout="wide",
)

st.title("📄 Liste des centres")

# ---- FICHIERS ----
PASSES_JSON = STATS_DIR / "passes.json"
VIDEO_2D_FULL = DATA_DIR / "full_game_2D_passe.mp4"

with st.expander("🔧 Debug paths (optionnel)"):
    st.json(
        {
            **path_exists_debug(),
            "PASSES_JSON": str(PASSES_JSON),
            "PASSES_JSON_exists": PASSES_JSON.exists(),
            "VIDEO_2D_FULL": str(VIDEO_2D_FULL),
            "VIDEO_2D_FULL_exists": VIDEO_2D_FULL.exists(),
        },
        expanded=False,
    )

# ---- Helpers ----
@st.cache_data(show_spinner="Chargement des événements…")
def load_events(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"JSON introuvable: {path}")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    df = pd.json_normalize(data, "actions")

    # Colonnes attendues (créées si manquantes)
    expected_cols = [
        "type", "start", "end", "team", "id",
        "team_passeur", "team_receveur", "passeur", "receveur", "succeed",
        "longueur", "speed", "nb_player_elimine",
        "passe_in_last_30m", "in_surface_reparation",
    ]
    for col in expected_cols:
        if col not in df.columns:
            df[col] = pd.NA

    # Coercitions sûres
    num_cols = ["start", "end", "team", "id", "passeur", "receveur",
                "speed", "longueur", "nb_player_elimine", "team_passeur", "team_receveur"]
    for col in num_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Normalise type
    df["type"] = df["type"].astype(str).str.strip().str.lower()

    # Map équipes -> icône
    def team_to_icon(v):
        if pd.isna(v):
            return "?"
        try:
            return "🔵" if int(v) == 0 else "🔴"
        except Exception:
            return "?"

    if "team_passeur" in df.columns:
        df["team_passeur"] = df["team_passeur"].apply(team_to_icon)
    if "team_receveur" in df.columns:
        df["team_receveur"] = df["team_receveur"].apply(team_to_icon)

    # succeed → icône (NaN-safe)
    def succeed_to_icon(v):
        if pd.isna(v):
            return "☐"
        if isinstance(v, str):
            val = v.strip().lower()
            if val in {"1", "true", "vrai", "yes", "oui"}:
                return "🗹"
            if val in {"0", "false", "faux", "no", "non"}:
                return "☐"
        try:
            return "🗹" if bool(int(v)) else "☐"
        except Exception:
            return "☐"

    if "succeed" in df.columns:
        df["succeed"] = df["succeed"].apply(succeed_to_icon)

    # Timecodes (FPS=30)
    fps = 30.0
    df["second_start"] = df["start"].apply(lambda x: round(float(x) / fps, 2) if pd.notna(x) else pd.NA)
    df["second_duration"] = df.apply(
        lambda r: round((float(r["end"]) - float(r["start"])) / fps, 2)
        if pd.notna(r["start"]) and pd.notna(r["end"]) else pd.NA,
        axis=1,
    )

    return df


@st.cache_data(show_spinner=False)
def load_video_bytes(path: Path) -> bytes | None:
    if not path.exists():
        return None
    with open(path, "rb") as f:
        return f.read()

# ---- Chargement + filtrage 'centre' ----
try:
    events = load_events(PASSES_JSON)
except Exception as e:
    import traceback
    st.error("❌ Erreur lors du chargement des événements.")
    st.code("".join(traceback.format_exc()))
    st.stop()

datas = events[events["type"] == "centre"].copy()

# ---- AgGrid ----
# On montre tout le DataFrame filtré (tu peux restreindre si besoin)
gb = GridOptionsBuilder.from_dataframe(datas)
gb.configure_selection(selection_mode="single", use_checkbox=True)
gb.configure_side_bar()
gridOptions = gb.build()

grid = AgGrid(
    datas,
    gridOptions=gridOptions,
    height=380,
    columns_auto_size_mode=ColumnsAutoSizeMode.FIT_ALL_COLUMNS_TO_VIEW,
    theme="alpine",
)

# ---- Sélection + vidéo robuste ----
selected_raw = grid.get("selected_rows", None)

# Normaliser la sélection -> liste de dicts
if isinstance(selected_raw, list):
    selected_rows = selected_raw
elif hasattr(selected_raw, "to_dict"):
    try:
        selected_rows = selected_raw.to_dict(orient="records")
    except Exception:
        selected_rows = []
else:
    selected_rows = []

if len(selected_rows) == 0:
    st.info("Sélectionne un centre dans le tableau pour afficher la vidéo et les détails.")
else:
    row = selected_rows[0]

    fps = 30.0
    start_val = pd.to_numeric(row.get("start", None), errors="coerce")
    end_val   = pd.to_numeric(row.get("end", None), errors="coerce")

    # start_time pour st.video (en secondes) avec -1s de marge
    if pd.isna(start_val):
        start_time = 0
    else:
        start_time = max(int(float(start_val) / fps) - 1, 0)

    # Durée informative (st.video ne coupe pas automatiquement à end)
    duration_sec = (
        round(float(end_val - start_val) / fps, 2)
        if (pd.notna(start_val) and pd.notna(end_val)) else None
    )

    col1, col2 = st.columns(2, gap="large")

    with col1:
        video_bytes = load_video_bytes(VIDEO_2D_FULL)
        if video_bytes is None:
            st.error(f"Vidéo introuvable: {VIDEO_2D_FULL.name}")
        else:
            st.video(video_bytes, start_time=start_time, format="video/mp4")
            if duration_sec is not None:
                st.caption(
                    f"Aperçu lancé à ~{start_time}s • Événement ≈ {duration_sec}s "
                    "(Streamlit ne coupe pas la vidéo automatiquement à la fin de l'événement)"
                )

    with col2:
        st.subheader("Détails du centre")

        def _val(k, default="?"):
            v = row.get(k, default)
            return v if (v is not None and v != "") else default

        sec_start = row.get("second_start", None)
        sec_dur   = row.get("second_duration", None)
        if isinstance(sec_start, (float, int)) and pd.isna(sec_start):
            sec_start = None
        if isinstance(sec_dur, (float, int)) and pd.isna(sec_dur):
            sec_dur = None

        st.write(f"Début : {sec_start if sec_start is not None else round(start_time, 2)} s")
        st.write(f"Durée : {sec_dur if sec_dur is not None else (duration_sec if duration_sec is not None else '?')} s")
        st.write(f"Type : {_val('type')}")
        st.write(f"Passeur : n°{_val('passeur')} → Receveur : n°{_val('receveur')}")
        st.write(f"Équipe : {_val('team')}")
