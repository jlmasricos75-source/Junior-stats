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
    equipo = st.radio("EQUIPO LAROCHE:", ["JUNIOR A", "JUNIOR B"])
    pool = sorted(fijos_a + junior_b) if equipo == "JUNIOR A" else sorted(junior_b)
    quinteto = st.multiselect("QUINTETO EN PISTA:", pool, max_selections=5)
    
    if st.button("🚀 EMPEZAR / RESET PARTIDO"):
        st.session_state.inicio, st.session_state.log = time.time(), []
        st.rerun()

# --- MARCADOR EN TIEMPO REAL ---
p_lar = sum(d['Pts'] for d in st.session_state.log)
c1, c2, c3 = st.columns(3)
c1.metric("LAROCHE", p_lar)
c2.metric(st.session_state.rival_nombre, st.session_state.puntos_rival)
c3.metric("TIEMPO VÍDEO", obtener_tiempo())
st.divider()

# --- INTERFAZ TÁCTIL ---
if st.session_state.inicio and len(quinteto) == 5:
    # 1. JUGADOR
    st.write("### 1. Jugador")
    cols_j = st.columns(5)
    for i, j in enumerate(quinteto):
        if cols_j[i].button(j, key=f"j_{j}", use_container_width=True, type="primary" if st.session_state.jugador_sel == j else "secondary"):
            st.session_state.jugador_sel = j

    if st.session_state.jugador_sel:
        # 2. ACCIONES RÁPIDAS (Zonas + Especiales + Convencional)
        t_now = obtener_tiempo()
        st.write(f"### 2. Acción de {st.session_state.jugador_sel}")
        
        # ZONAS (Mapa Visual)
        st.markdown("<div style='text-align:center; border:1px solid #ccc; border-radius:50px 50px 0 0; padding:5px; font-size:10px;'>TRIPLE</div>", unsafe_allow_html=True)
        z_cols = st.columns(5)
        zona, acc, pts = None, None, 0
        if z_cols[0].button("Esq IZQ"): zona = "T3-Esq-IZQ"
        if z_cols[1].button("45° IZQ"): zona = "T3-45-IZQ"
        if z_cols[2].button("FRON"): zona = "T3-Front"
        if z_cols[3].button("45° DER"): zona = "T3-45-DER"
        if z_cols[4].button("Esq DER"): zona = "T3-Esq-DER"
        
        m_cols = st.columns([1, 2, 1])
        if m_cols[0].button("Med IZQ"): zona = "Med-IZQ"
        if m_cols[1].button("🏀 PINTURA 🏀", type="primary", use_container_width=True): zona = "Pintura"
        if m_cols[2].button("Med DER"): zona = "Med-DER"

        # ESTADÍSTICA
        st.markdown("#### 📊 Convencional")
        c_c1 = st.columns(4)
        if c_c1[0].button("✅ T2", use_container_width=True): acc, pts = "T2-A", 2
        if c_c1[1].button("🎯 T3", use_container_width=True): acc, pts = "T3-A", 3
        if c_c1[2].button("❌ TIRO", use_container_width=True): acc, pts = "FALLO", 0
        if c_c1[3].button("👟 PERD", use_container_width=True): acc, pts = "TOV", 0
        
        c_c2 = st.columns(4)
        if c_c2[0].button("🚀 REB-O", use_container_width=True): acc, pts = "REB-O", 0
        if c_c2[1].button("🛡️ REB-D", use_container_width=True): acc, pts = "REB-D", 0
        if c_c2[2].button("🤝 AST", use_container_width=True): acc, pts = "AST", 0
        if c_c2[3].button("🏀 TL", use_container_width=True): acc, pts = "TL-A", 1

        # FILOSOFÍA
        st.markdown("#### ✨ Especiales Laroche")
        c_esp = st.columns(4)
        for idx, m in enumerate(especiales):
            if c_esp[idx % 4].button(m, use_container_width=True):
                acc, pts = m, 0

        # REGISTRO
        if acc or zona:
            st.session_state.log.append({
                "Rival": st.session_state.rival_nombre,
                "Min": t_now, 
                "Jugador": st.session_state.jugador_sel,
                "Zona": zona if zona else "N/A", 
                "Acción": acc if acc else "POSICIÓN",
                "Pts": pts
            })
            st.session_state.jugador_sel = None # Reset para siguiente acción
            st.rerun()

# --- HISTORIAL ---
if st.session_state.log:
    st.divider()
    st.write(f"📝 Log del partido vs **{st.session_state.rival_nombre}**")
    st.dataframe(pd.DataFrame(st.session_state.log).iloc[::-1], use_container_width=True)
    
    # Botón Descarga
    csv = pd.DataFrame(st.session_state.log).to_csv(index=False).encode('utf-8')
    st.download_button("📥 Descargar Datos del Partido", csv, f"laroche_vs_{st.session_state.rival_nombre}.csv", "text/csv")
