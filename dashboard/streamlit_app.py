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
