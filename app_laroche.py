import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN VISUAL NCAA D1 (OLIVE EDITION) ---
st.set_page_config(layout="wide", page_title="LAROCHE PERFORMANCE | OLIVE PROGRAM")

st.markdown("""
    <style>
    /* Fondo principal: Gris muy oscuro casi negro para que el oliva resalte */
    .stApp {
        background-color: #0B0E11;
        color: #FFFFFF;
        font-family: 'Inter', sans-serif;
    }
    
    /* Título con estilo de Universidad NCAA */
    h1 {
        color: #808000; /* Verde Oliva */
        font-family: 'Arial Black', sans-serif;
        text-transform: uppercase;
        letter-spacing: -1px;
        border-left: 10px solid #808000;
        padding-left: 20px;
        margin-bottom: 20px;
    }

    /* Estilo de los Botones: Tipografía bloque NCAA */
    div.stButton > button {
        background-color: #808000 !important; /* Verde Oliva del Equipo */
        color: white !important;
        border: 2px solid #556B2F !important;
        border-radius: 4px !important; /* Menos redondeado, más bloque */
        height: 85px !important;
        font-family: 'Oswald', sans-serif; /* Tipografía condensada tipo NCAA */
        font-weight: 800 !important;
        font-size: 22px !important;
        text-transform: uppercase;
        box-shadow: 0 4px #556B2F;
        transition: all 0.1s ease;
    }

    /* Efecto al pulsar el botón */
    div.stButton > button:active {
        box-shadow: 0 0 #556B2F;
        transform: translateY(4px);
    }

    /* Botones de Alerta/Defensa (un tono más oscuro para diferenciar) */
    [data-testid="stVerticalBlock"] > div:nth-child(2) div.stButton > button {
        background-color: #4B5320 !important; /* Army Green */
    }

    /* Selector de Jugador */
    .stSelectbox label {
        color: #808000 !important;
        font-weight: bold;
        font-size: 18px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CABECERA ---
st.markdown("# LAROCHE BASKETBALL")
st.markdown("##### ELITE SCOUTING UNIT | OLIVE PROGRAM")

# --- ROSTER ACTUALIZADO (Con Miguel Dolz) ---
ROSTER = [
    "2-LUCAS MÁS", "3-NACHO SERRA", "5-ADRIAN OJEDA", "8-OSCAR MORANA", 
    "9-ANDREU ESTELLÉS", "11-ALEJANDRO PELLICER", "12-DAVID NAVÍO", 
    "15-JOAN AMER", "18-GABI OFICIAL", "21-MARC ALÓS", 
    "23-ANTONIO PERANDRÉS", "24-CARLOS MÁS", "28-DERIN AKYUZ", 
    "32-GONZALO RODRÍGUEZ", "50-ADRIAN FERRER", "82-MIGUEL DOLZ", "99-PEPE MÁS"
]

if 'session_stats' not in st.session_state:
    st.session_state.session_stats = []

def registrar(p, acc, cat):
    st.session_state.session_stats.append({
        "Hora": datetime.now().strftime("%H:%M:%S"),
        "Jugador": p, "Acción": acc, "Categoría": cat
    })
    st.toast(f"LOGGED: {p} - {acc}", icon="🏀")

# --- INTERFAZ DE CAPTURA ---
st.divider()
jugador_sel = st.selectbox("ATHLETE IN FOCUS:", ROSTER)

col1, col2 = st.columns(2)

with col1:
    st.subheader("⚔️ THE WHEEL OFFENSE")
    st.button("🏀 POINTS SCORE", on_click=registrar, args=(jugador_sel, "Puntos", "Off"), use_container_width=True)
    st.button("🚨 PAINT TOUCH < 8s", on_click=registrar, args=(jugador_sel, "PT_8s", "Off"), use_container_width=True)
    st.button("🔄 STAMPEDE ATTACK", on_click=registrar, args=(jugador_sel, "Stampede", "Off"), use_container_width=True)
    st.button("✂️ 45° / BACKDOOR", on_click=registrar, args=(jugador_sel, "Corte", "Off"), use_container_width=True)

with col2:
    st.subheader("🛡️ IRON WALL DEFENSE")
    st.button("👣 FEET DEFENSE (OK)", on_click=registrar, args=(jugador_sel, "Pies_OK", "Def"), use_container_width=True)
    st.button("❌ HANDS FOUL", on_click=registrar, args=(jugador_sel, "Manos_Error", "Def"), use_container_width=True)
    st.button("🏃 DEFENSIVE SPRINT", on_click=registrar, args=(jugador_sel, "Sprint", "Def"), use_container_width=True)
    st.button("⚠️ TURNOVER", on_click=registrar, args=(jugador_sel, "Perdida", "Error"), use_container_width=True)

# --- ZONA DE EXPORTACIÓN ---
st.divider()
if st.session_state.session_stats:
    df = pd.DataFrame(st.session_state.session_stats)
    st.download_button("📥 DOWNLOAD GAME DATA (CSV)", df.to_csv(index=False), "NCAA_Laroche_Game.csv")
