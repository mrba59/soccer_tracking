import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- Imports internes (scripts + chemins robustes) ---
# soccer_graph est ton module interne qui fournit get_performance_chart, get_pass_graph, get_pass_network
from dashboard.scripts.soccer_graph import *
try:
    from dashboard.src.paths import STATS_DIR, path_exists_debug
except ModuleNotFoundError:
    from dashboard.src.path import STATS_DIR, path_exists_debug   # fallback si besoin

st.set_page_config(
    page_title="Soccer Stats - Statistiques",
    page_icon="📈",
    layout="wide",
)

# FICHIERS (dans dashboard/src/stats/)
PASSES_URL         = STATS_DIR / "all_passe_with_coordinates.csv"
POSITIONS_URL      = STATS_DIR / "mean_position.csv"
PASSES_RELATION_URL= STATS_DIR / "pass_relation.csv"
TEAM_STATS_URL     = STATS_DIR / "stats_team.json"

with st.expander("🔧 Debug paths (optionnel)"):
    st.json({
        **path_exists_debug(),
        "PASSES_URL": str(PASSES_URL),
        "POSITIONS_URL": str(POSITIONS_URL),
        "PASSES_RELATION_URL": str(PASSES_RELATION_URL),
        "TEAM_STATS_URL": str(TEAM_STATS_URL),
    }, expanded=False)

@st.cache_data(show_spinner="Chargement des données")
def load_pass():
    if not PASSES_URL.exists():
        raise FileNotFoundError(f"CSV introuvable: {PASSES_URL}")
    return pd.read_csv(PASSES_URL, index_col=0)

@st.cache_data(show_spinner="Chargement des données")
def load_position():
    if not POSITIONS_URL.exists():
        raise FileNotFoundError(f"CSV introuvable: {POSITIONS_URL}")
    data = pd.read_csv(POSITIONS_URL, index_col=0)
    data = data.rename({'pass_count': 'count'}, axis=1)
    return data

@st.cache_data(show_spinner="Chargement des données")
def load_pass_relation():
    if not PASSES_RELATION_URL.exists():
        raise FileNotFoundError(f"CSV introuvable: {PASSES_RELATION_URL}")
    return pd.read_csv(PASSES_RELATION_URL, index_col=0)

@st.cache_data(show_spinner="Chargement des données")
def load_team_stats():
    if not TEAM_STATS_URL.exists():
        raise FileNotFoundError(f"JSON introuvable: {TEAM_STATS_URL}")
    data = pd.read_json(TEAM_STATS_URL)
    data = data.transpose()
    stats_key = data.columns
    for key in stats_key:
        data[key + "_per"] = data[key] / data[key].sum()
    return data, stats_key, [key + "_per" for key in stats_key], [key.replace('_', ' ').title() for key in stats_key]

# ===== UI =====
st.title("📈 Statistiques")

try:
    team_stats, stats, stats_per, stats_label = load_team_stats()
except Exception as e:
    import traceback
    st.error("❌ Erreur chargement des stats équipe.")
    st.code("".join(traceback.format_exc()))
    st.stop()

team_list = ["Équipe 1", "Équipe 2"]
team_color = ['rgba(0, 0, 255, 0.8)', 'rgba(255, 0, 0, 0.8)']

# Radar / barres de performance
fig = get_performance_chart(team_stats, stats, stats_per, stats_label, team_list, team_color)
st.plotly_chart(fig, use_container_width=True)

# Choix de l'équipe
team = st.radio("Choix de l'équipe", team_list, horizontal=True)
team_id = 0 if team == "Équipe 1" else 1

col1, col2 = st.columns(2)

# Toutes les passes
with col1:
    try:
        pass_df = load_pass()
        fig_pass = get_pass_graph(
            pass_df.loc[pass_df['team_start'] == team_id],
            pass_df["successful"] == True,  # conserve ta logique d'origine
            f"Passes de l'{team.lower()}",
        )
        st.pyplot(fig_pass)
    except Exception as e:
        import traceback
        st.error("❌ Erreur chargement/affichage des passes.")
        st.code("".join(traceback.format_exc()))

# Réseau de passes
with col2:
    try:
        positions = load_position()
        pass_relation = load_pass_relation()
        network_fig = get_pass_network(
            positions.loc[positions['TeamID'] == team_id],
            pass_relation.loc[pass_relation['team'] == team_id],
            f"Réseau de passes de l'{team.lower()}",
        )
        st.pyplot(network_fig)
    except Exception as e:
        import traceback
        st.error("❌ Erreur chargement/affichage du réseau de passes.")
        st.code("".join(traceback.format_exc()))
