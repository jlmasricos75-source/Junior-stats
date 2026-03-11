import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="Laroche Tactical Board", layout="wide")

# --- CONFIGURACIÓN DE MÉTRICAS ---
fijos_a = ["3.-NACHO SERRA", "8.-OSCAR MORANA", "15.-JOAN AMER", "18.-GABI OFICIAL", "21.-MARC ALÓS", "50.-ADRIAN FERRER", "99.-PEPE MÁS"]
junior_b = ["2.-LUCAS MÁS", "5.-ADRIAN OJEDA", "9.-ANDREU ESTELLÉS", "11.-ALEJANDRO PELLICER", "12.-DAVID NAVÍO", "23.-ANTONIO PERANDRÉS", "24.-CARLOS MÁS", "28.-DERIN AKYUZ", "32.-GONZALO", "82.-MIGUEL DOLZ"]

# Tus 7 medidas especiales (Añadida Paint Touch < 8")
especiales = ["PT < 8''", "Paint Touch", "Corte", "Transición", "ExtraPass+Tiro", "Tiro Reemplazo", "Stampede"]
zonas = ["Bajo Aro", "Pintura", "Media IZQ", "Media DER", "T3 Esq IZQ", "T3 Esq DER", "T3 Frontal"]

# --- ESTADO DE SESIÓN ---
if 'log' not in st.session_state: st.session_state.log = []
if 'inicio' not in st.session_state: st.session_state.inicio = None
if 'jugador_sel' not in st.session_state: st.session_state.jugador_sel = None
if 'zona_sel' not in st.session_state: st.session_state.zona_sel = None
if 'puntos_rival' not in st.session_state: st.session_state.puntos_rival = 0

def obtener_tiempo():
    if st.session_state.inicio is None: return "00:00"
    t = int(time.time() - st.session_state.inicio)
    return f"{t//60:02d}:{t%60:02d}"

# --- SIDEBAR: GESTIÓN ---
with st.sidebar:
    st.header("🆚 MARCADOR")
    st.session_state.puntos_rival = st.number_input("Rival:", min_value=0, value=st.session_state.puntos_rival)
    st.divider()
    equipo = st.radio("EQUIPO LAROCHE:", ["JUNIOR A", "JUNIOR B"])
    pool = sorted(fijos_a + junior_b) if equipo == "JUNIOR A" else sorted(junior_b)
    quinteto = st.multiselect("EN PISTA:", pool, max_selections=5)
    if st.button("🚀 INICIAR / RESET"):
        st.session_state.inicio = time.time()
        st.session_state.log = []
        st.rerun()

# --- MARCADOR Y RELOJ ---
puntos_laroche = sum(d['Pts'] for d in st.session_state.log if 'Pts' in d)
c1, c2, c3 = st.columns(3)
c1.metric("LAROCHE", puntos_laroche)
c2.metric("RIVAL", st.session_state.puntos_rival)
c3.metric("RELOJ VÍDEO", obtener_tiempo())
st.divider()

if st.session_state.inicio is None:
    st.warning("⚠️ Pulsa 'INICIAR' en el lateral.")
elif len(quinteto) < 5:
    st.info("👈 Selecciona los 5 jugadores.")
else:
    # PASO 1: JUGADOR
    st.write("### 1. Jugador")
    cols_j = st.columns(5)
    for i, j in enumerate(quinteto):
        if cols_j[i].button(j, key=f"j_{j}", use_container_width=True, type="primary" if st.session_state.jugador_sel == j else "secondary"):
            st.session_state.jugador_sel = j

    if st.session_state.jugador_sel:
        # PASO 2: ZONA
        st.write("### 2. Zona")
        cols_z = st.columns(len(zonas))
        for i, z in enumerate(zonas):
            if cols_z[i].button(z, key=f"z_{z}", use_container_width=True, type="primary" if st.session_state.zona_sel == z else "secondary"):
                st.session_state.zona_sel = z

        if st.session_state.zona_sel:
            # PASO 3: ACCIÓN Y RESULTADO
            st.write(f"### 3. Acción de {st.session_state.jugador_sel}")
            col_l, col_r = st.columns(2)
            
            with col_l:
                st.markdown("#### 📊 Convencional")
                sub1, sub2 = st.columns(2)
                if sub1.button("✅ CANASTA 2P", use_container_width=True): acc, pts = "T2-Acierto", 2
                if sub2.button("🎯 TRIPLE 3P", use_container_width=True): acc, pts = "T3-Acierto", 3
                if sub1.button("❌ FALLO 2P", use_container_width=True): acc, pts = "T2-Fallo", 0
                if sub2.button("⭕ FALLO 3P", use_container_width=True): acc, pts = "T3-Fallo", 0
                if sub1.button("🚀 REB. OFF", use_container_width=True): acc, pts = "REB-O", 0
                if sub2.button("🛡️ REB. DEF", use_container_width=True): acc, pts = "REB-D", 0
                if sub1.button("🏀 TL ACERT", use_container_width=True): acc, pts = "TL-A", 1
                if sub2.button("🚫 TL FALLO", use_container_width=True): acc, pts = "TL-F", 0
                if sub1.button("👟 PÉRDIDA", use_container_width=True): acc, pts = "TOV", 0
                if sub2.button("🤝 ASIST", use_container_width=True): acc, pts = "AST", 0

            with col_r:
                st.markdown("#### ✨ Especiales (Filosofía)")
                grid = st.columns(2)
                for idx, m in enumerate(especiales):
                    if grid[idx % 2].button(f"⚡ {m}", key=f"m_{m}", use_container_width=True):
                        # Al pulsar especial, pedimos desenlace
                        st.session_state.medida_temp = m
                
                if 'medida_temp' in st.session_state:
                    st.write(f"¿Cómo acabó el **{st.session_state.medida_temp}**?")
                    res_cols = st.columns(3)
                    if res_cols[0].button("✅ Metió 2P", key="res1"): acc, pts = f"{st.session_state.medida_temp}-T2A", 2
                    if res_cols[0].button("🎯 Metió 3P", key="res2"): acc, pts = f"{st.session_state.medida_temp}-T3A", 3
                    if res_cols[1].button("❌ Falló", key="res3"): acc, pts = f"{st.session_state.medida_temp}-Fallo", 0
                    if res_cols[2].button("👟 Pérdida", key="res4"): acc, pts = f"{st.session_state.medida_temp}-Pérdida", 0
                    if res_cols[2].button("🤝 Solo Pase", key="res5"): acc, pts = f"{st.session_state.medida_temp}-Pase", 0

            if 'acc' in locals():
                st.session_state.log.append({
                    "Min": obtener_tiempo(), "Jugador": st.session_state.jugador_sel,
                    "Zona": st.session_state.zona_sel, "Acción": acc, "Pts": pts
                })
                # Limpiar estados
                st.session_state.jugador_sel = None
                st.session_state.zona_sel = None
                if 'medida_temp' in st.session_state: del st.session_state.medida_temp
                st.rerun()

# --- VISUALIZACIÓN ---
if st.session_state.log:
    df = pd.DataFrame(st.session_state.log)
    st.divider()
    st.subheader("📝 Historial de Jugadas")
    st.dataframe(df.iloc[::-1], use_container_width=True)
