import streamlit as st
import pandas as pd
import time

# 1. CONFIGURACIÓN ULTRA-LIGERA PARA MALA CONEXIÓN
st.set_page_config(page_title="MVP JUNIOR PRO", layout="wide", initial_sidebar_state="collapsed")

# 2. ESTADO DE LA SESIÓN (Base de datos temporal)
if 'log' not in st.session_state: st.session_state.log = []
if 'inicio' not in st.session_state: st.session_state.inicio = None
if 'j_sel' not in st.session_state: st.session_state.j_sel = None
if 'z_sel' not in st.session_state: st.session_state.z_sel = "Pintura"
if 'pista' not in st.session_state: 
    st.session_state.pista = ["3.NACHO", "8.OSCAR", "15.JOAN", "18.GABI", "21.MARC"]
if 'cambio_fase' not in st.session_state: st.session_state.cambio_fase = None

# ROSTER ACTUALIZADO
roster_completo = [
    "3.NACHO", "8.OSCAR", "15.JOAN", "18.GABI", "21.MARC", 
    "50.ADRIAN", "99.PEPE", "2.LUCAS", "5.ADRIAN.O", 
    "9.ANDREU", "11.PELLICER", "12.NAVÍO"
]

# 3. FUNCIÓN DE REGISTRO (Guarda todo, incluido el quinteto para el +/-)
def registrar(accion, pts, tipo="Local"):
    st.session_state.log.append({
        "Reloj": int(time.time() - st.session_state.inicio) if st.session_state.inicio else 0,
        "Jugador": st.session_state.j_sel,
        "Zona": st.session_state.z_sel,
        "Accion": accion,
        "Pts": pts,
        "Tipo": tipo,
        "En_Pista": list(st.session_state.pista)
    })
    st.toast(
