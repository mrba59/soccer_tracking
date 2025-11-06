import streamlit as st
from pathlib import Path

# --- import DATA_DIR (compatible avec paths.py OU path.py) ---
try:
    from dashboard.src.paths import DATA_DIR, path_exists_debug  # shim recommandé
except ModuleNotFoundError:
    from dashboard.src.path import DATA_DIR, path_exists_debug   # fallback si tu n'as pas encore le shim

st.set_page_config(
    page_title="Soccer Stats - Conversion en coordonnées de terrain",
    page_icon="⚽",
    layout="wide",
)

st.title("⚽ Conversion en coordonnées de terrain")

# --- FICHIERS DANS dashboard/src/top_view/ ---
PITCH_CSV = DATA_DIR / "pitch_coordinate_D_20220220_1_0000_0030.csv"
VIDEO_ANNOT = DATA_DIR / "D_20220220_1_0000_0030.mp4"
VIDEO_2D = DATA_DIR / "2D_short_video.mp4"

# (optionnel) Debug des chemins pour le cloud
with st.expander("🔧 Debug paths (optionnel)"):
    st.json({
        **path_exists_debug(),
        "PITCH_CSV": str(PITCH_CSV),
        "VIDEO_ANNOT": str(VIDEO_ANNOT),
        "VIDEO_2D": str(VIDEO_2D),
    }, expanded=False)

# --- Helper: charger la vidéo en binaire (évite MediaFileStorageError) ---
@st.cache_data(show_spinner=False)
def load_video_bytes(path: Path) -> bytes | None:
    if not path.exists():
        return None
    # Lecture binaire -> on passe les bytes à st.video()
    with open(path, "rb") as f:
        return f.read()

col1, col2 = st.columns(2)

with col1:
    st.subheader("Vidéo annotée")
    data = load_video_bytes(VIDEO_ANNOT)
    if data is None:
        st.error(f"Vidéo introuvable: {VIDEO_ANNOT.name}")
    else:
        st.video(data, format="video/mp4", start_time=0)

with col2:
    st.subheader("Vidéo 2D")
    data2 = load_video_bytes(VIDEO_2D)
    if data2 is None:
        st.error(f"Vidéo introuvable: {VIDEO_2D.name}")
    else:
        st.video(data2, format="video/mp4", start_time=0)

st.subheader("Explication")
st.markdown('''
Pour obtenir les coordonnées de terrain, nous avons besoin de connaître
les coordonnées de la caméra et les coordonnées du terrain, ce qui permet de
calculer la matrice d’homographie (3×3). Celle-ci transforme un plan (8 d.o.f.).
''')

# Utiliser des URLs absolues (https://...) pour éviter les soucis de schéma // en cloud
st.markdown('''
<center> 
    <span class="mw-default-size" typeof="mw:File">
        <img src="https://upload.wikimedia.org/wikipedia/commons/a/a2/France1.gif"
             decoding="async" width="212" height="231" class="mw-file-element">
    </span> 
    ➪ 
    <span class="mw-default-size" typeof="mw:File">
        <img src="https://upload.wikimedia.org/wikipedia/commons/0/02/France_homographie_%281%29.gif"
             decoding="async" width="285" height="202" class="mw-file-element">
    </span>
</center>
''', unsafe_allow_html=True)

st.text("Source de l'image : https://fr.wikipedia.org/wiki/Application_projective")
st.link_button("Plus d'informations", "https://docs.opencv.org/4.x/d9/dab/tutorial_homography.html")
