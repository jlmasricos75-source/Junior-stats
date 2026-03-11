import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Laroche Club Analytics", layout="wide")

# --- CONFIGURACIÓN DE PLANTILLAS ---
# Fijos del A
fijos_a = ["NACHO", "OSCAR", "JOAN", "GABI", "MARC", "FERRER", "PEPE"]
# Los que doblan (el resto de los 17)
doblan = ["LUCAS MÁS", "MIGUEL DOLZ", "JORGE GIL", "HUGO MARQUÉS", "PABLO GADEA", 
          "GONZALO C.", "CARLOS BELTRÁN", "IÑAKI LÓPEZ", "NICO GIMÉNEZ", "ALEX ROMERO"]

if 'log' not in st.session_state: st.session_state.log = []
if 'jugador_activo' not in st.session_state: st.session_state.jugador_activo = None

# --- SIDEBAR: GESTIÓN DE CLUB ---
with st.sidebar:
    st.header("🏢 Control de Equipo")
    equipo_hoy = st.radio("PARTIDO DE HOY:", ["JUNIOR A", "JUNIOR B"], horizontal=True)
    
    # Lógica de visibilidad
    if equipo_hoy == "JUNIOR A":
        pool_jugadores = sorted(fijos_a + doblan)
    else:
        pool_jugadores = sorted(doblan) # En el B solo salen los que doblan
    
    st.divider()
    convocados = st.multiselect("📋 Jugadores Disponibles:", pool_jugadores, default=pool_jugadores[:5])
    
    st.divider()
    quinteto = st.multiselect("⛹️ EN PISTA (Quinteto):", convocados, max_selections=5)
    
    if st.button("🗑️ REINICIAR PARTIDO"):
        st.session_state.log = []
        st.rerun()

# --- INTERFAZ DE CAPTURA ---
st.title(f"🏀 {equipo_hoy} - MODO LIVE")

if len(quinteto) < 5:
    st.warning("Selecciona los 5 jugadores en pista en el menú de la izquierda.")
else:
    # FILA DE BOTONES DE JUGADORES
    cols = st.columns(5)
    for i, j in enumerate(quinteto):
        if cols[i].button(j, key=f"btn_{j}", use_container_width=True, 
                          type="primary" if st.session_state.jugador_activo == j else "secondary"):
            st.session_state.jugador_activo = j

    # ACCIONES RÁPIDAS (Si hay jugador seleccionado)
    if st.session_state.jugador_activo:
        st.info(f"Registrando para: {st.session_state.jugador_activo}")
        
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            if st.button("✅ T2"): acc, pts = "T2A", 2
            if st.button("❌ T2"): acc, pts = "T2F", 0
        with c2:
            if st.button("✅ T3"): acc, pts = "T3A", 3
            if st.button("❌ T3"): acc, pts = "T3F", 0
        with c3:
            if st.button("🛡️ REB"): acc, pts = "REB", 0
            if st.button("🤝 ASIST"): acc, pts = "AST", 0
        with c4:
            if st.button("👟 PERD"): acc, pts = "TOV", 0
            if st.button("🛡️ ROBO"): acc, pts = "STL", 0

        if 'acc' in locals():
            st.session_state.log.append({
                "Fecha": datetime.now().strftime("%d/%m/%Y"),
                "Equipo": equipo_hoy,
                "Jugador": st.session_state.jugador_activo,
                "Acción": acc,
                "Pts": pts,
                "Lineup": "-".join(sorted(quinteto))
            })
            st.session_state.jugador_activo = None
            st.rerun()

# --- BOX SCORE DINÁMICO ---
if st.session_state.log:
    st.divider()
    df = pd.DataFrame(st.session_state.log)
    
    # Filtro opcional para ver historial
    ver_todo = st.toggle("Ver estadísticas de toda la temporada (acumulado)")
    
    df_ver = df if ver_todo else df[df['Equipo'] == equipo_hoy]
    
    st.subheader(f"📊 Estadísticas {equipo_hoy if not ver_todo else 'Club Completo'}")
    box_score = df_ver.groupby("Jugador").agg({'Pts': 'sum', 'Acción': 'count'}).rename(columns={'Acción': 'Acciones Totales'})
    st.dataframe(box_score, use_container_width=True)
