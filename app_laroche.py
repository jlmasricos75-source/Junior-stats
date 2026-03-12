import streamlit as st
import pandas as pd
import time

# ESTA LÍNEA SOLO PUEDE APARECER UNA VEZ Y DEBE SER LA PRIMERA
st.set_page_config(page_title="MVP JUNIOR PRO", layout="wide")

# Inicialización de variables de sesión
if 'log' not in st.session_state: st.session_state.log = []
if 'inicio' not in st.session_state: st.session_state.inicio = None
if 'j_sel' not in st.session_state: st.session_state.j_sel = None
if 'z_sel' not in st.session_state: st.session_state.z_sel = "Pintura"
if 'pista' not in st.session_state: 
    st.session_state.pista = ["3.NACHO", "8.OSCAR", "15.JOAN", "18.GABI", "21.MARC"]
if 'cambio_fase' not in st.session_state: st.session_state.cambio_fase = None

roster_completo = ["3.NACHO", "8.OSCAR", "15.JOAN", "18.GABI", "21.MARC", "50.ADRIAN", "99.PEPE", "2.LUCAS", "5.ADRIAN.O", "9.ANDREU", "11.PELLICER", "12.NAVÍO"]

def registrar(accion, pts, tipo="Local"):
    st.session_state.log.append({
        "Reloj": int(time.time() - st.session_state.inicio) if st.session_state.inicio else 0,
        "Jugador": st.session_state.j_sel, "Zona": st.session_state.z_sel, "Accion": accion, "Pts": pts, "Tipo": tipo, "En_Pista": list(st.session_state.pista)
    })
    st.toast(f"✅ {accion}")

# --- INTERFAZ ---
st.title("🏀 MÉTRICAS JUNIOR")

if not st.session_state.inicio:
    if st.button("🚀 INICIAR PARTIDO", type="primary"):
        st.session_state.inicio = time.time()
        st.rerun()
else:
    # SISTEMA DE CAMBIOS
    if st.session_state.cambio_fase == "SALIENDO":
        st.error("🔄 ¿QUIÉN SALE?")
        cols = st.columns(5)
        for i, j in enumerate(st.session_state.pista):
            if cols[i].button(j, key=f"out_{j}"):
                st.session_state.jugador_fuera = j
                st.session_state.cambio_fase = "ENTRANDO"
                st.rerun()
    elif st.session_state.cambio_fase == "ENTRANDO":
        st.success(f"🔄 ENTRA POR {st.session_state.jugador_fuera}:")
        banquillo = [j for j in roster_completo if j not in st.session_state.pista]
        cols = st.columns(4)
        for i, j in enumerate(banquillo):
            if cols[i%4].button(j, key=f"in_{j}"):
                idx = st.session_state.pista.index(st.session_state.jugador_fuera)
                st.session_state.pista[idx] = j
                st.session_state.cambio_fase = None
                st.rerun()
    else:
        # PANTALLA PRINCIPAL
        c_q = st.columns(6)
        for i, j in enumerate(st.session_state.pista):
            if c_q[i].button(j, type="primary" if st.session_state.j_sel == j else "secondary"):
                st.session_state.j_sel = j
        if c_q[5].button("🔄 CAMBIO"):
            st.session_state.cambio_fase = "SALIENDO"
            st.rerun()

        st.divider()
        col_c, col_a = st.columns([1, 1])
        with col_c:
            st.write("📍 **ZONA**")
            if st.button("🏟️ PINTURA", use_container_width=True, type="primary"): st.session_state.z_sel = "Pintura"
            z1, z2, z3 = st.columns(3)
            if z1.button("T3 Esq"): st.session_state.z_sel = "T3-Esq"
            if z2.button("T3 Fr"): st.session_state.z_sel = "T3-Front"
            if z3.button("T3 45"): st.session_state.z_sel = "T3-45"
            st.info(f"Zona: {st.session_state.z_sel}")

        with col_a:
            st.write("📝 **ACCIÓN**")
            r1, r2 = st.columns(2)
            if r1.button("✅ METIDO", use_container_width=True):
                p = 3 if "T3" in st.session_state.z_sel else 2
                registrar("MET", p)
            if r2.button("❌ FALLO", use_container_width=True): registrar("FAL", 0)
            if st.button("⚠️ RIVAL (+2)", use_container_width=True): registrar("RIVAL", 2, "Rival")

# DESCARGA
if st.session_state.log:
    st.divider()
    df = pd.DataFrame(st.session_state.log)
    st.download_button("📥 DESCARGAR CSV", df.to_csv(index=False), "partido.csv")
