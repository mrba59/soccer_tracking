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
    page_title="Soccer Stats - Liste des événements",
    page_icon="📄",
    layout="wide",
)

st.title("📄 Liste des événements")

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
def load_datas(passes_path: Path) -> pd.DataFrame:
    if not passes_path.exists():
        raise FileNotFoundError(f"JSON introuvable: {passes_path}")
    with open(passes_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    df = pd.json_normalize(data, "actions")

    # Colonnes attendues
    for col in [
        "team_passeur",
        "team_receveur",
        "succeed",
        "start",
        "end",
        "type",
        "passeur",
        "receveur",
        "longueur",
        "speed",
        "nb_player_elimine",
        "passe_in_last_30m",
        "in_surface_reparation",
        "team",
        "id",
    ]:
        if col not in df.columns:
            df[col] = pd.NA

    # Coercition numérique sûre
    for col in ["team_passeur", "team_receveur", "start", "end", "passeur", "receveur",
                "longueur", "speed", "nb_player_elimine", "team", "id"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Mapping équipes
    def team_to_icon(v):
        if pd.isna(v):
            return "?"
        try:
            return "🔵" if int(v) == 0 else "🔴"
        except Exception:
            return "?"

    df["team_passeur"] = df["team_passeur"].apply(team_to_icon)
    df["team_receveur"] = df["team_receveur"].apply(team_to_icon)

    # succeed -> icône
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

    df["succeed"] = df["succeed"].apply(succeed_to_icon)

    # Timecodes (FPS=30)
    fps = 30.0
    df["second_start"] = df["start"].apply(lambda x: round(float(x) / fps, 2) if pd.notna(x) else pd.NA)
    df["second_duration"] = df.apply(
        lambda r: round((float(r["end"]) - float(r["start"])) / fps, 2)
        if pd.notna(r["start"]) and pd.notna(r["end"])
        else pd.NA,
        axis=1,
    )

    # Normalise 'type'
    df["type"] = df["type"].astype(str).str.strip().str.lower()

    return df


@st.cache_data(show_spinner=False)
def load_video_bytes(path: Path) -> bytes | None:
    if not path.exists():
        return None
    with open(path, "rb") as f:
        return f.read()


# ---- Chargement + filtrage passes ----
try:
    datas = load_datas(PASSES_JSON)
except Exception as e:
    import traceback
    st.error("❌ Erreur lors du chargement des événements.")
    st.code("".join(traceback.format_exc()))
    st.stop()

datas = datas[datas["type"] == "passe"].copy()

# ---- AgGrid ----
display_cols = [
    "start", "end", "id", "passeur", "receveur", "team_passeur", "team_receveur",
    "longueur", "speed", "nb_player_elimine", "passe_in_last_30m",
    "in_surface_reparation", "succeed", "team", "second_start", "second_duration",
]

# Filtre les colonnes qui existent réellement (au cas où)
display_cols = [c for c in display_cols if c in datas.columns]

gb = GridOptionsBuilder.from_dataframe(datas[display_cols])
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

selected_row = grid.get("selected_rows", [])

# ---- Détails + vidéo ----
if selected_row:
    row = selected_row[0]
    start_time_val = row.get("second_start", 0)
    try:
        start_time = max(int(float(start_time_val)) - 1, 0)
    except Exception:
        start_time = 0

    col1, col2 = st.columns(2, gap="large")

    with col1:
        video_bytes = load_video_bytes(VIDEO_2D_FULL)
        if video_bytes is None:
            st.error(f"Vidéo introuvable: {VIDEO_2D_FULL.name}")
        else:
            st.video(video_bytes, start_time=start_time, format="video/mp4")

    with col2:
        st.subheader("Détails de l'événement")
        def _val(k, default="?"):
            v = row.get(k, default)
            return v if (v is not None and v != "") else default

        st.write(f"Début : {_val('second_start')} s")
        st.write(f"Durée : {_val('second_duration')} s")
        st.write(f"Type : {_val('type')}")
        passeur = _val("passeur")
        receveur = _val("receveur")
        tp = _val("team_passeur", "")
        tr = _val("team_receveur", "")
        succeed_icon = _val("succeed", "☐")

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
