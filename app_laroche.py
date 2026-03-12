import streamlit as st
import pandas as pd
import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="ADN Junior Pro v53", layout="wide", initial_sidebar_state="collapsed")

# --- ESTILOS ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 12px; font-weight: bold; height: 4.5em; margin-bottom: 8px; }
    .main-header { background-color: #1e293b; color: white; padding: 15px; border-radius: 12px; text-align: center; margin-bottom: 10px; }
    .adn-box { background-color: #fff7ed; border: 2px solid #f97316; padding: 10px; border-radius: 10px; text-align: center; color: #9a3412; }
    .court-bg { background-color: #fef3c7; border: 2px solid #92400e; border-radius: 15px; padding: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- ROSTER ---
PLAYERS_DB = {
    "JUNIOR A": ["3.SERRA", "8.MORANA", "15.AMER", "18.GABI", "21.ALÓS", "50.FERRER", "99.PEPE"],
    "JUNIOR B": ["2.LUCAS", "5.ADRIÁN", "9.ANDREU", "11.ALEJ.", "12.DAVID", "23.ANT.", "24.CARLOS", "28.DERIN", "32.GONZALO", "82.MIGUEL"]
}

# --- ESTADO ---
if 'log' not in st.session_state: st.session_state.log = []
if 'fase' not in st.session_state: st.session_state.fase = "CONFIG"
if 'pista' not in st.session_state: st.session_state.pista = []
if 'convocados' not in st.session_state: st.session_state.convocados = []
if 'pos_n' not in st.session_state: st.session_state.pos_n = 1
if 'j_sel' not in st.session_state: st.session_state.j_sel = None
if 'z_sel' not in st.session_state: st.session_state.z_sel = "PINTURA"
if 'periodo' not in st.session_state: st.session_state.periodo = "1Q"
if 'adn_pos' not in st.session_state: 
    st.session_state.adn_pos = {"PT": 0, "PT8": 0, "INV": 0, "ESC": 0, "EXTRA": 0}

# --- LOGICA ---
def get_stats(nombre):
    pts = sum(d.get('Pts', 0) for d in st.session_state.log if d.get('Jugador') == nombre and d.get('Tipo') == "Local")
    fls = sum(1 for d in st.session_state.log if d.get('Jugador') == nombre and d.get('Accion') == "FALTA")
    return pts, fls

def registrar(accion, pts=0, tipo="Local", calidad="N/A"):
    jugador = st.session_state.j_sel if tipo == "Local" else "RIVAL"
    l_pts = sum(d.get('Pts', 0) for d in st.session_state.log if d.get('Tipo') == "Local")
    r_pts = sum(d.get('Pts', 0) for d in st.session_state.log if d.get('Tipo') == "Rival")
    
    st.session_state.log.append({
        "Pos#": st.session_state.pos_n, "Q": st.session_state.periodo, "Jugador": jugador,
        "Accion": accion, "Zona": st.session_state.z_sel, "Pts": pts, "Calidad": calidad,
        "PT": st.session_state.adn_pos["PT"], "PT8": st.session_state.adn_pos["PT8"],
        "INV": st.session_state.
