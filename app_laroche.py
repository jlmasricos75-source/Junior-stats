import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="Laroche Tactical Pro", layout="wide")

# --- DATA ---
fijos_a = ["3.-NACHO SERRA", "8.-OSCAR MORANA", "15.-JOAN AMER", "18.-GABI OFICIAL", "21.-MARC ALÓS", "50.-ADRIAN FERRER", "99.-PEPE MÁS"]
junior_b = ["2.-LUCAS MÁS", "5.-ADRIAN OJEDA", "9.-ANDREU ESTELLÉS", "11.-ALEJANDRO PELLICER", "12.-DAVID NAVÍO", "23.-ANTONIO PERANDRÉS", "24.-CARLOS MÁS", "28.-DERIN AKYUZ", "32.-GONZALO", "82.-MIGUEL DOLZ"]
especiales = ["PT < 8''", "Paint Touch", "Corte", "Transición", "ExtraPass+Tiro", "Tiro Reemplazo", "Stampede"]

if 'log' not in st.session_state: st.session_state.log = []
if 'inicio' not in st.session_state: st.session_state.inicio = None
if 'jugador_sel' not in st.session_state: st.session_state.jugador_sel = None
if 'zona_temp' not in st.session_state: st.session_state.zona_temp = None

def obtener_tiempo():
    if st.session_state.inicio is None: return "00:00"
    t = int(time.time() - st.session_state.inicio)
    return f"{t//60:02d}:{t%60:02d}"

# --- SIDEBAR ---
with st.sidebar:
    st.header("📋 Partido")
    rival = st.text_input("Rival:", value="RIVAL").upper()
    p_riv = st.number_input(f"Puntos {rival}:", min_value=0)
    equipo = st.radio("LAROCHE:", ["JUNIOR A", "JUNIOR B"])
    pool = sorted(fijos_a + junior_b) if equipo == "JUNIOR A" else sorted(junior_b)
    quinteto = st.multiselect("QUINTETO:", pool, max_selections=5)
    if st.button("🚀 INICIAR / RESET"):
        st.session_state.inicio, st.session_state.log = time.time(), []
        st.rerun()

# --- MARCADOR ---
p_lar = sum(d['Pts'] for d in st.session_state.log)
c1, c2, c3 = st.columns(3)
c1.metric("LAROCHE", p_lar)
c2.metric(rival, p_riv)
c3.metric("VÍDEO", obtener_tiempo())
st.divider()

# --- LÓGICA DE CAPTURA ---
if st.session_state.inicio and len(quinteto) == 5:
    # 1. JUGADOR
    st.write("### 1. Selecciona Jugador")
    cols_j = st.columns(5)
    for i, j in enumerate(quinteto):
        if cols_j[i].button(j, key=f"j_{j}", use_container_width=True, type="primary" if st.session_state.jugador_sel == j else "secondary"):
            st.session_state.jugador_sel = j

    if st.session_state.jugador_sel:
        st.write(f"👉 Registrando para: **{st.session_state.jugador_sel}**")
        
        # 2. ZONA (Solo si no hay zona guardada ya)
        st.markdown("---")
        st.write("### 2. ¿Dónde ha ocurrido?")
        z_cols = st.columns(5)
        if z_cols[0].button("Esq IZQ"): st.session_state.zona_temp = "T3-Esq-IZQ"
        if z_cols[1].button("45° IZQ"): st.session_state.zona_temp = "T3-45-IZQ"
        if z_cols[2].button("FRONTAL"): st.session_state.zona_temp = "T3-Front"
        if z_cols[3].button("45° DER"): st.session_state.zona_temp = "T3-45-DER"
        if z_cols[4].button("Esq DER"): st.session_state.zona_temp = "T3-Esq-DER"
        
        m_cols = st.columns([1, 2, 1])
        if m_cols[0].button("Media IZQ"): st.session_state.zona_temp = "Med-IZQ"
        if m_cols[1].button("🏀 PINTURA 🏀", type="primary", use_container_width=True): st.session_state.zona_temp = "Pintura"
        if m_cols[2].button("Media DER"): st.session_state.zona_temp = "Med-DER"
        
        if st.session_state.zona_temp:
            st.success(f"Zona: {st.session_state.zona_temp}")

        # 3. ACCIÓN (Aquí es donde se guarda todo al log)
        st.markdown("---")
        st.write("### 3. ¿Qué ha pasado?")
        col_c, col_e = st.columns(2)
        finalizar = False
        acc, pts = None, 0

        with col_c:
            st.write("**Convencional**")
            c_row1 = st.columns(2)
            if c_row1[0].button("✅ CANASTA 2P", use_container_width=True): acc, pts, finalizar = "T2-A", 2, True
            if c_row1[1].button("🎯 TRIPLE 3P", use_container_width=True): acc, pts, finalizar = "T3-A", 3, True
            c_row2 = st.columns(2)
            if c_row2[0].button("❌ FALLO", use_container_width=True): acc, pts, finalizar = "FALLO", 0, True
            if c_row2[1].button("👟 PÉRDIDA", use_container_width=True): acc, pts, finalizar = "TOV", 0, True
            c_row3 = st.columns(2)
            if c_row3[0].button("🚀 REB-O", use_container_width=True): acc, pts, finalizar = "REB-O", 0, True
            if c_row3[1].button("🛡️ REB-D", use_container_width=True): acc, pts, finalizar = "REB-D", 0, True

        with col_e:
            st.write("**Filosofía Laroche**")
            for m in especiales:
                if st.button(m, use_container_width=True):
                    acc, pts, finalizar = m, 0, True

        # GUARDADO FINAL
        if finalizar:
            st.session_state.log.append({
                "Min": obtener_tiempo(),
                "Jugador": st.session_state.jugador_sel,
                "Zona": st.session_state.zona_temp if st.session_state.zona_temp else "N/A",
                "Acción": acc,
                "Pts": pts
            })
            # Limpiar para el siguiente
            st.session_state.jugador_sel = None
            st.session_state.zona_temp = None
            st.rerun()

# --- LOG ---
if st.session_state.log:
    st.divider()
    st.dataframe(pd.DataFrame(st.session_state.log).iloc[::-1], use_container_width=True)
