import streamlit as st
import pandas as pd
import time
from datetime import datetime

st.set_page_config(page_title="Laroche Video-Stats", layout="wide")

# --- 1. CONFIGURACIÓN DE ROSTER ---
fijos_a = ["3.-NACHO SERRA", "8.-OSCAR MORANA", "15.-JOAN AMER", "18.-GABI OFICIAL", "21.-MARC ALÓS", "50.-ADRIAN FERRER", "99.-PEPE MÁS"]
junior_b = ["2.-LUCAS MÁS", "5.-ADRIAN OJEDA", "9.-ANDREU ESTELLÉS", "11.-ALEJANDRO PELLICER", "12.-DAVID NAVÍO", "23.-ANTONIO PERANDRÉS", "24.-CARLOS MÁS", "28.-DERIN AKYUZ", "32.-GONZALO", "82.-MIGUEL DOLZ"]
zonas = ["Pintura", "Media", "T3 IZQ", "T3 DER", "T3 FRONTAL"]

if 'log' not in st.session_state: st.session_state.log = []
if 'inicio_partido' not in st.session_state: st.session_state.inicio_partido = None
if 'jugador_activo' not in st.session_state: st.session_state.jugador_activo = None

# --- SIDEBAR: RELOJ Y GESTIÓN ---
with st.sidebar:
    st.header("⏱️ Reloj de Partido")
    if st.button("🚀 INICIAR / RESET RELOJ"):
        st.session_state.inicio_partido = time.time()
    
    # Cálculo del tiempo transcurrido
    if st.session_state.inicio_partido:
        transcurrido = int(time.time() - st.session_state.inicio_partido)
        mins, segs = divmod(transcurrido, 60)
        st.metric("Tiempo de Juego", f"{mins:02d}:{segs:02d}")
    else:
        st.info("Pulsa Iniciar al saltar el balón.")

    st.divider()
    equipo_hoy = st.radio("EQUIPO:", ["JUNIOR A", "JUNIOR B"], horizontal=True)
    pool = sorted(fijos_a + junior_b) if equipo_hoy == "JUNIOR A" else sorted(junior_b)
    convocados = st.multiselect("Convocatoria:", pool, default=pool[:12])
    quinteto = st.multiselect("EN PISTA:", convocados, max_selections=5)

# --- INTERFAZ DE CAPTURA ---
st.title(f"🏀 {equipo_hoy} vs RIVAL")

if len(quinteto) < 5:
    st.warning("Selecciona el quinteto para empezar.")
else:
    cols = st.columns(5)
    for i, j in enumerate(quinteto):
        if cols[i].button(j, key=f"b_{j}", use_container_width=True, type="primary" if st.session_state.jugador_activo == j else "secondary"):
            st.session_state.jugador_activo = j

    if st.session_state.jugador_activo:
        # Obtenemos el tiempo exacto de la acción
        t_accion = "00:00"
        if st.session_state.inicio_partido:
            ahora = int(time.time() - st.session_state.inicio_partido)
            m, s = divmod(ahora, 60)
            t_accion = f"{m:02d}:{s:02d}"

        st.markdown(f"### Acción para {st.session_state.jugador_activo} a los **{t_accion}**")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            if st.button("✅ T2"): acc, pts, z_req = "T2A", 2, True
            if st.button("❌ T2"): acc, pts, z_req = "T2F", 0, True
        with c2:
            if st.button("✅ T3"): acc, pts, z_req = "T3A", 3, True
            if st.button("❌ T3"): acc, pts, z_req = "T3F", 0, True
        with c3:
            if st.button("🤝 AST"): acc, pts, z_req = "AST", 0, False
            if st.button("🚀 REB.O"): acc, pts, z_req = "REBO", 0, False
        with c4:
            if st.button("👟 TOV (Pérdida)"): acc, pts, z_req = "TOV", 0, False
            if st.button("🛡️ STL (Robo)"): acc, pts, z_req = "STL", 0, False

        if 'acc' in locals():
            zona_final = "N/A"
            if z_req:
                st.write("📍 ¿Zona?")
                cz = st.columns(5)
                for i, z in enumerate(zonas):
                    if cz[i].button(z):
                        st.session_state.log.append({"Minuto": t_accion, "Jugador": st.session_state.jugador_activo, "Acción": acc, "Pts": pts, "Zona": z})
                        st.session_state.jugador_activo = None
                        st.rerun()
            else:
                st.session_state.log.append({"Minuto": t_accion, "Jugador": st.session_state.jugador_activo, "Acción": acc, "Pts": pts, "Zona": "N/A"})
                st.session_state.jugador_activo = None
                st.rerun()

# --- REVISIÓN DE VÍDEO (Punto 5 del plan) ---
if st.session_state.log:
    st.divider()
    df = pd.DataFrame(st.session_state.log)
    
    t_box, t_video = st.tabs(["📊 Box Score", "🎥 Marcadores para Vídeo"])
    
    with t_box:
        st.dataframe(df.groupby("Jugador").agg({'Pts': 'sum', 'Acción': 'count'}))
    
    with t_video:
        st.subheader("Guía para Sesión de Vídeo")
        accion_filtro = st.selectbox("Filtrar por acción para ver clips:", ["TODAS", "TOV", "T3F", "AST", "T2A"])
        df_vid = df if accion_filtro == "TODAS" else df[df['Acción'] == accion_filtro]
        st.table(df_vid[["Minuto", "Jugador", "Acción", "Zona"]])

    # Botón para descargar CSV y subirlo a Excel o Hoopsalytics
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Descargar Datos para Análisis Profundo", csv, "laroche_stats.csv", "text/csv")
