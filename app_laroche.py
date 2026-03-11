import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="Laroche Tactical Pro", layout="wide")

# --- DATA ---
fijos_a = ["3.-NACHO SERRA", "8.-OSCAR MORANA", "15.-JOAN AMER", "18.-GABI OFICIAL", "21.-MARC ALÓS", "50.-ADRIAN FERRER", "99.-PEPE MÁS"]
junior_b = ["2.-LUCAS MÁS", "5.-ADRIAN OJEDA", "9.-ANDREU ESTELLÉS", "11.-ALEJANDRO PELLICER", "12.-DAVID NAVÍO", "23.-ANTONIO PERANDRÉS", "24.-CARLOS MÁS", "28.-DERIN AKYUZ", "32.-GONZALO", "82.-MIGUEL DOLZ"]
especiales = ["PT < 8''", "Paint Touch", "Corte", "Transición", "ExtraPass+Tiro", "Tiro Reemplazo", "Stampede"]

# --- ESTADO DE SESIÓN ---
if 'log' not in st.session_state: st.session_state.log = []
if 'inicio' not in st.session_state: st.session_state.inicio = None
if 'jugador_sel' not in st.session_state: st.session_state.jugador_sel = None
if 'rival_nombre' not in st.session_state: st.session_state.rival_nombre = "RIVAL"

def obtener_tiempo():
    if st.session_state.inicio is None: return "00:00"
    t = int(time.time() - st.session_state.inicio)
    return f"{t//60:02d}:{t%60:02d}"

# --- SIDEBAR: CONFIGURACIÓN INICIAL ---
with st.sidebar:
    st.header("📋 Datos del Encuentro")
    st.session_state.rival_nombre = st.text_input("Nombre del Rival:", value=st.session_state.rival_nombre).upper()
    st.session_state.puntos_rival = st.number_input(f"Puntos {st.session_state.rival_nombre}:", min_value=0, step=1)
    
    st.divider()
    equipo = st.radio("EQUIPO
