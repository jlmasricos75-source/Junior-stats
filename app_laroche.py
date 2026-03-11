import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Laroche Analytics Pro", layout="wide")

# --- 1. BASE DE DATOS OFICIAL (Dorsales + Nombres) ---
fijos_a = [
    "3.-NACHO SERRA", "8.-OSCAR MORANA", "15.-JOAN AMER", 
    "18.-GABI OFICIAL", "21.-MARC ALÓS", "50.-ADRIAN FERRER", "99.-PEPE MÁS"
]

junior_b = [
    "2.-LUCAS MÁS", "5.-ADRIAN OJEDA", "9.-ANDREU ESTELLÉS", 
    "11.-ALEJANDRO PELLICER", "12.-DAVID NAVÍO", "23.-ANTONIO PERANDRÉS", 
    "24.-CARLOS MÁS", "28.-DERIN AKYUZ", "32.-GONZALO", "82.-MIGUEL DOLZ"
]

zonas = ["Pintura", "Media", "T3 IZQ", "T3 DER", "T3 FRONTAL"]

if 'log' not in st.session_state: st.session_state.log = []
if 'jugador_activo' not in st.session_state: st.session_state.jugador_activo = None

# --- SIDEBAR: GESTIÓN DE EQUIPO ---
with st.sidebar:
    st.header("🏢 Control de Club")
    equipo_hoy = st.radio("PARTIDO DE:", ["JUNIOR A", "JUNIOR B"], horizontal=True)
    
    # Definir quién puede jugar hoy
    if equipo_hoy == "JUNIOR A":
        pool = sorted(fijos_a + junior_b) # Los 17 disponibles
    else:
        pool = sorted(junior_b) # Solo los 10 del B
    
    st.divider()
    convocados = st.multiselect("📋 Convocatoria (12 máx):", pool, default=pool[:min(12, len(pool))])
    
    st.divider()
    quinteto = st.multiselect("⛹️ EN PISTA:", convocados, max_selections=5)
    
    if st.button("🗑️ REINICIAR PARTIDO"):
        st.session_state.log = []
        st.rerun()

# --- INTERFAZ DE ANOTACIÓN ---
st.title(f"🏀 {equipo_hoy} vs RIVAL")

if len(quinteto) < 5:
    st.info("👈 Selecciona los 5 jugadores en pista en el menú lateral.")
else:
    # FILA DE JUGADORES (QUINTETO)
    cols = st.columns(5)
    for i, j in enumerate(quinteto):
        if cols[i].button(j, key=f"btn_{j}", use_container_width=True, 
                          type="primary" if st.session_state.jugador_activo == j else "secondary"):
            st.session_state.jugador_activo = j

    # PANEL DE ACCIONES
    if st.session_state.jugador_activo:
        st.markdown(f"### Anotando para: **{st.session_state.jugador_activo}**")
        c1, c2, c3, c4 = st.columns(4)
        
        with c1:
            if st.button("✅ T2", use_container_width=True): acc, pts, z_req = "T2A", 2, True
            if st.button("❌ T2", use_container_width=True): acc, pts, z_req = "T2F", 0, True
        with c2:
            if st.button("✅ T3", use_container_width=True): acc, pts, z_req = "T3A", 3, True
            if st.button("❌ T3", use_container_width=True): acc, pts, z_req = "T3F", 0, True
        with c3:
            if st.button("🛡️ REB", use_container_width=True): acc, pts, z_req = "REB", 0, False
            if st.button("🤝 AST", use_container_width=True): acc, pts, z_req = "AST", 0, False
        with c4:
            if st.button("👟 TOV", use_container_width=True): acc, pts, z_req = "TOV", 0, False
            if st.button("🛡️ STL", use_container_width=True): acc, pts, z_req = "STL", 0, False

        # REGISTRO CON ZONA
        if 'acc' in locals():
            if z_req:
                st.write(f"📍 ¿Desde dónde el {acc}?")
                cz = st.columns(5)
                for i, z in enumerate(zonas):
                    if cz[i].button(z):
                        st.session_state.log.append({
                            "Equipo": equipo_hoy, "Jugador": st.session_state.jugador_activo, 
                            "Acción": acc, "Pts": pts, "Zona": z, "Lineup": "-".join(sorted(quinteto))
                        })
                        st.session_state.jugador_activo = None
                        st.rerun()
            else:
                st.session_state.log.append({
                    "Equipo": equipo_hoy, "Jugador": st.session_state.jugador_activo, 
                    "Acción": acc, "Pts": pts, "Zona": "N/A", "Lineup": "-".join(sorted(quinteto))
                })
                st.session_state.jugador_activo = None
                st.rerun()

# --- BOX SCORE ACUMULADO ---
if st.session_state.log:
    st.divider()
    df = pd.DataFrame(st.session_state.log)
    st.subheader("📊 Box Score del Partido")
    resumen = df.groupby("Jugador").agg({'Pts': 'sum', 'Acción': 'count'}).rename(columns={'Acción': 'Eventos'})
    st.dataframe(resumen, use_container_width=True)
