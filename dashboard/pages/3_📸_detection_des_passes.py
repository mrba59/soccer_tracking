import streamlit as st
from pathlib import Path

# --- Import DATA_DIR (compatible paths.py OU path.py) ---
try:
    from dashboard.src.paths import DATA_DIR, path_exists_debug  # recommandé
except ModuleNotFoundError:
    from dashboard.src.path import DATA_DIR, path_exists_debug   # fallback temporaire

st.set_page_config(
    page_title="Soccer Stats - Détection des passes",
    page_icon="📸",
    layout="centered",
)

st.title("📸 Détections des passes")

VIDEO_2D_FULL = DATA_DIR / "full_game_2D_passe.mp4"

with st.expander("🔧 Debug paths (optionnel)"):
    st.json({
        **path_exists_debug(),
        "VIDEO_2D_FULL": str(VIDEO_2D_FULL),
        "VIDEO_2D_FULL_exists": VIDEO_2D_FULL.exists(),
    }, expanded=False)

@st.cache_data(show_spinner=False)
def load_video_bytes(path: Path) -> bytes | None:
    if not path.exists():
        return None
    with open(path, "rb") as f:
        return f.read()

data = load_video_bytes(VIDEO_2D_FULL)
if data is None:
    st.error(f"Vidéo introuvable: {VIDEO_2D_FULL.name}")
else:
    st.video(data, format="video/mp4", start_time=0)
