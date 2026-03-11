import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="Laroche Visual Stats", layout="wide")

# --- CONFIGURACIÓN DE ROSTER ---
fijos_a = ["3.-NACHO SERRA", "8.-OSCAR MORANA", "15.-JOAN AMER", "18.-GABI OFICIAL", "21.-MARC ALÓS", "50.-ADRIAN FERRER", "99.-PEPE MÁS"]
junior_b = ["2.-LUCAS MÁS", "5.-ADRIAN OJEDA", "9.-ANDREU ESTELLÉS", "11.-ALEJANDRO PELLICER", "12.-DAVID NAVÍO", "23.-ANTONIO PERANDRÉS", "24.-CARLOS MÁS", "28.-DERIN AKYUZ", "32.-GONZALO", "82.-MIGUEL DOLZ"]
especiales = ["PT < 8''", "Paint Touch", "Corte", "Transición", "ExtraPass+Tiro", "Tiro Reemplazo", "Stampede"]

if 'log' not in st.session_state: st.session_state.log = []
if 'inicio' not in st.session_state: st.session_state.inicio = None
if 'jugador_sel' not in st.session_state: st.session_state.jugador_sel = None
if 'zona_sel' not in st.session_state: st.session_state.zona_sel = None

def obtener_tiempo():
    if st.session_state.inicio is None: return "00:00"
    t = int(time.time() - st.session_state.inicio)
    return f"{t//60:02d}:{t%60:02d}"

# --- SIDEBAR ---
with st.sidebar:
    st.header("🆚 RIVAL")
    p_rival = st.number_input("Puntos:", min_value=0, step=1)
    st.divider()
    equipo = st.radio("EQUIPO:", ["JUNIOR A", "JUNIOR B"])
    pool = sorted(fijos_a + junior_b) if equipo == "JUNIOR A" else sorted(junior_b)
    quinteto = st.multiselect("EN PISTA:", pool, max_selections=5)
    if st.button("🚀 INICIAR / RESET"):
        st.session_state.inicio = time.time()
        st.session_state.log = []
        st.rerun()

# --- MARCADOR ---
p_laroche = sum(d['Pts'] for d in st.session_state.log)
c1, c2, c3 = st.columns(3)
c1.metric("LAROCHE", p_laroche)
c2.metric("RIVAL", p_rival)
c3.metric("RELOJ", obtener_tiempo())

# --- FLUJO TÁCTICO ---
if st.session_state.inicio and len(quinteto) == 5:
    # PASO 1: JUGADOR
    st.write("### 1. Jugador")
    cols_j = st.columns(5)
    for i, j in enumerate(quinteto):
        if cols_j[i].button(j, key=f"j_{j}", use_container_width=True, type="primary" if st.session_state.jugador_sel == j else "secondary"):
            st.session_state.jugador_sel = j

    if st.session_state.jugador_sel:
        # PASO 2: MAPA VISUAL DEL CAMPO
        st.write(f"### 2. Zona de la acción ({st.session_state.jugador_sel})")
        
        # Simulación visual del campo con columnas
        map_c1, map_c2, map_c3, map_c4, map_c5 = st.columns(5)
        
        # Fila de Triple
        if map_c1.button("Corner IZQ", use_container_width=True): st.session_state.zona_sel = "T3-Esq-IZQ"
        if map_c2.button("45° IZQ", use_container_width=True): st.session_state.zona_sel = "T3-45-IZQ"
        if map_c3.button("FRONTAL", use_container_width=True): st.session_state.zona_sel = "T3-Frontal"
        if map_c4.button("45° DER", use_container_width=True): st.session_state.zona_sel = "T3-45-DER"
        if map_c5.button("Corner DER", use_container_width=True): st.session_state.zona_sel = "T3-Esq-DER"
        
        # Fila de Media Distancia / Pintura
        mid_c1, mid_c2, mid_c3 = st.columns([1, 2, 1])
        if mid_c1.button("Media IZQ", use_container_width=True): st.session_state.zona_sel = "Media-IZQ"
        with mid_c2:
            if st.button("⬇️ PINTURA / ARO ⬇️", use_container_width=True, type="primary"): 
                st.session_state.zona_sel = "Pintura"
        if mid_c3.button("Media DER", use_container_width=True): st.session_state.zona_sel = "Media-DER"

        if st.session_state.zona_sel:
            # PASO 3: ACCIÓN
            st.divider()
            st.write(f"### 3. Acción en {st.session_state.zona_sel}")
            col_conv, col_esp = st.columns(2)
            
            with col_conv:
                st.markdown("#### 📊 Convencional")
                sub1, sub2 = st.columns(2)
                if sub1.button("✅ CANASTA 2P", use_container_width=True): acc, pts = "T2-A", 2
                if sub2.button("🎯 TRIPLE 3P", use_container_width=True): acc, pts = "T3-A", 3
                if sub1.button("❌ FALLO 2P", use_container_width=True): acc, pts = "T2-F", 0
                if sub2.button("⭕ FALLO 3P", use_container_width=True): acc, pts = "T3-F", 0
                if sub1.button("🚀 REB. OFF", use_container_width=True): acc, pts = "REB-O", 0
                if sub2.button("🛡️ REB. DEF", use_container_width=True): acc, pts = "REB-D", 0
                if sub1.button("👟 PÉRDIDA", use_container_width=True): acc, pts = "TOV", 0
                if sub2.button("🤝 ASIST", use_container_width=True): acc, pts = "AST", 0

            with col_esp:
                st.markdown("#### ✨ Especiales")
                grid = st.columns(2)
                for idx, m in enumerate(especiales):
                    if grid[idx % 2].button(f"⚡ {m}", key=f"m_{m}", use_container_width=True):
                        st.session_state.medida_temp = m
                
                if 'medida_temp' in st.session_state:
                    st.info(f"Final de {st.session_state.medida_temp}:")
                    r_c = st.columns(3)
                    if r_c[0].button("✅ T2", key="res1"): acc, pts = f"{st.session_state.medida_temp}-2A", 2
                    if r_c[0].button("🎯 T3", key="res2"): acc, pts = f"{st.session_state.medida_temp}-3A", 3
                    if r_c[1].button("❌ Fallo", key="res3"): acc, pts = f"{st.session_state.medida_temp}-F", 0
                    if r_c[2].button("👟 TOV", key="res4"): acc, pts = f"{st.session_state.medida_temp}-TOV", 0

            if 'acc' in locals():
                st.session_state.log.append({
                    "Min": obtener_tiempo(), "Jugador": st.session_state.jugador_sel,
                    "Zona": st.session_state.zona_sel, "Acción": acc, "Pts": pts
                })
                st.session_state.jugador_sel = None
                st.session_state.zona_sel = None
                if 'medida_temp' in st.session_state: del st.session_state.medida_temp
                st.rerun()

# --- LOG ---
if st.session_state.log:
    st.divider()
    st.dataframe(pd.DataFrame(st.session_state.log).iloc[::-1], use_container_width=True)
