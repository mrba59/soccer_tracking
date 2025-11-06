import sys, os
from pathlib import Path
import streamlit as st

REPO_ROOT = Path(__file__).resolve().parents[2]   
DASH_DIR  = REPO_ROOT / "dashboard"
SRC_DIR   = DASH_DIR / "src"

for p in (str(REPO_ROOT), str(DASH_DIR), str(SRC_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)
# Try the canonical import first
try:
    from dashboard.src.paths import DATA_DIR, path_exists_debug
except ModuleNotFoundError:
    # fallback: show helpful debug & try legacy filename if it exists
    st.warning("ModuleNotFoundError: tentative de debug des chemins…")
    st.code({
        "cwd": os.getcwd(),
        "REPO_ROOT": str(REPO_ROOT),
        "DASH_DIR": str(DASH_DIR),
        "SRC_DIR": str(SRC_DIR),
        "sys.path_head": sys.path[:3],
        "src_list": [p.name for p in SRC_DIR.glob('*.py')] if SRC_DIR.exists() else "src/ absent",
    })
    try:
        # au cas où le fichier serait encore nommé path.py
        from dashboard.src.path import DATA_DIR, path_exists_debug  # noqa
        st.info("Import réussi depuis dashboard.src.path (ancien nom).")
    except ModuleNotFoundError as e:
        st.error("Impossible d'importer paths.py ni path.py. Vérifie la casse, le chemin et le commit.")
        raise

st.set_page_config(
    page_title="Soccer Stats - Home",
    page_icon="⚽",
    layout="centered"
)

# Title
st.title("Obtention de statistiques via la retransmission d'un match")

st.markdown('''
        Ce projet a pour but de récupérer des statistiques sur un match de football à partir de la retransmission de celui-ci.

        A partir de la position des joueurs et du ballon, nous allons calculer des statistiques sur le match.

        A ce stade, nous nous sommes concentrés sur les passes.
''')

st.divider()

st.markdown('''
    Les données proviennent d'un projet d'étudiant à l'université de Tsukuba au Japon :
''')

st.markdown('''
    <div style="border: 1px solid grey; padding: 10px; border-radius: 5px; margin: 10px 0;">      
        <p>
            <b>SoccerTrack:</b><br>
            A Dataset and Tracking Algorithm for Soccer with Fish-eye and Drone Videos
        </p>
        <p>
            Atom Scott*, Ikuma Uchida*, Masaki Onishi, Yoshinari Kameda, Kazuhiro Fukui, Keisuke Fujii
        </p>
        <p>
            <i> Presented at CVPR Workshop on Computer Vision for Sports (CVSports'22). *Authors contributed equally. </i>
        </p>
        <div style="margin: 15px 0;">
            <a rel="noreferrer nofollow" href="https://openaccess.thecvf.com/content/CVPR2022W/CVSports/papers/Scott_SoccerTrack_A_Dataset_and_Tracking_Algorithm_for_Soccer_With_Fish-Eye_CVPRW_2022_paper.pdf" target="_blank">
                <img src="https://img.shields.io/badge/Paper-PDF-red?style=for-the-badge&logo=adobe-acrobat-reader" alt="Paper PDF">
            </a>
            <a rel="noreferrer nofollow" href="https://github.com/AtomScott/SoccerTrack" target="_blank">
                <img src="https://img.shields.io/badge/Code-Page-blue?style=for-the-badge&logo=github" alt="Code Page">
            </a>
            <a rel="noreferrer nofollow" href="https://soccertrack.readthedocs.io/" target="_blank">
                <img src="https://img.shields.io/badge/Documentation-Page-blue?style=for-the-badge&logo=read-the-docs" alt="Documentation">
            </a>
        </div>

        <p style="margin-top:20px; font-style: italic; color: grey; font-size: 0.9em;">
            All data in SoccerTrack was obtained from 11-vs-11 soccer games between college-aged athletes. 
            Measurements were conducted after we received the approval of Tsukuba university's ethics committee, 
            and all participants provided signed informed permission. After recording several soccer matches, 
            the videos were semi-automatically annotated based on the GNSS coordinates of each player.
        </p>
    </div>
''', unsafe_allow_html=True)
