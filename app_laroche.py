import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="MVP JUNIOR - FULL CONTROL", layout="wide", initial_sidebar_state="collapsed")

# --- VARIABLES DE ESTADO ---
if 'log' not in st.session_state: st.session_state.log = []
if 'pos_n' not in st.session_state: st.session_state.pos_n = 1
if 'inicio' not in st.session_state: st.session_state.inicio = None
if 'j_sel' not in st.session_state: st.session_state.j_sel = None
if 'z_sel' not in st.session_state: st.session_state.z_sel = "Pintura"
if 'pista' not in st.session_state: 
    st.session_state.pista = ["3.NACHO", "8.OSCAR", "15.JOAN", "18.GABI", "21.MARC"]
if 'cambio_fase' not in st.session_state: st.session_state.cambio_fase = None

# ROSTER COMPLETO (12 JUGADORES)
roster_completo = [
    "3.NACHO", "8.OSCAR", "15.JOAN", "18.GABI", "21.MARC", 
    "50.ADRIAN", "99.PEPE", "2.LUCAS", "5.ADRIAN.O", 
    "9.ANDREU", "11.PELLICER", "12.NAVÍO"
]

def registrar(accion, pts, tipo="Local"):
    st.session_state.log.append({
        "Pos": st.session_state.pos_n,
        "Reloj": int(time.time() - st.session_state.inicio) if st.session_state.inicio else 0,
        "Jugador": st.session_state.j_sel,
        "Zona": st.session_state.z_sel,
        "Accion": accion,
        "Pts": pts,
        "Tipo": tipo,
        "Quinteto": list(st.session_state.pista)
    })
    st.toast(f"✅ {accion}")

# --- HEADER: MARCADOR Y POSESIÓN ---
p_l = sum(d['Pts'] for d in st.session_state.log if d['Tipo'] == "Local")
p_r = sum(d['Pts'] for d in st.session_state.log if d['Tipo'] == "Rival")

c_h1, c_h2, c_h3 = st.columns(3)
with c_h1: st.metric("🏀 POSESIÓN", f"#{st.session_state.pos_n}")
with c_h2: st.subheader(f"L: {p_l} | R: {p_r}")
with c_h3: 
    if not st.session_state.inicio:
        if st.button("🚀 INICIAR PARTIDO", type="primary"): st.session_state.inicio = time.time(); st.rerun()
    else:
        st.write(f"⏱️ {int((time.time()-st.session_state.inicio)//60):02d}:{int((time.time()-st.session_state.inicio)%60):02d}")

if st.session_state.inicio:
    # --- GESTIÓN DE CAMBIOS (BLOQUEANTE) ---
    if st.session_state.cambio_fase == "SALIENDO":
        st.error("🔄 ¿QUIÉN SALE A BANQUILLO?")
        cols = st.columns(5)
        for i, j in enumerate(st.session_state.pista):
            if cols[i].button(j, key=f"out_{j}"):
                st.session_state.jugador_fuera = j
                st.session_state.cambio_fase = "ENTRANDO"; st.rerun()
        if st.button("Cancelar"): st.session_state.cambio_fase = None; st.rerun()

    elif st.session_state.cambio_fase == "ENTRANDO":
        st.success(f"🔄 ENTRA POR {st.session_state.jugador_fuera}:")
        banquillo = [j for j in roster_completo if j not in st.session_state.pista]
        cols = st.columns(4)
        for i, j in enumerate(banquillo):
            if cols[i%4].button(j, key=f"in_{j}"):
                idx = st.session_state.pista.index(st.session_state.jugador_fuera)
                st.session_state.pista[idx] = j
                st.session_state.cambio_fase = None; st.rerun()

    # --- INTERFAZ PRINCIPAL ---
    else:
        # 1. QUINTETO + BOTÓN CAMBIO
        st.write("🏃 **EN PISTA:**")
        cols_q = st.columns(6)
        for i, j in enumerate(st.session_state.pista):
            if cols_q[i].button(j, type="primary" if st.session_state.j_sel == j else "secondary", use_container_width=True):
                st.session_state.j_sel = j
        if cols_q[5].button("🔄 CAMBIO", type="primary", use_container_width=True):
            st.session_state.cambio_fase = "SALIENDO"; st.rerun()

        st.divider()

        col_izq, col_der = st.columns([1.3, 1])

        with col_izq: # CAMPO VISUAL
            st.write("📍 **ZONA DEL CAMPO**")
            t_row = st.columns(5)
            z_t3 = ["T3-Esq-L", "T3-45-L", "T3-Front", "T3-45-R", "T3-Esq-R"]
            for i, z in enumerate(z_t3):
                if t_row[i].button(z): st.session_state.z_sel = z
            
            st.write("")
            m_l, pintura, m_r = st.columns([1, 2, 1])
            if m_l.button("Med L"): st.session_state.z_sel = "Med-L"
            if pintura.button("🏟️ PINTURA / POSTE 🏟️", type="primary", use_container_width=True): st.session_state.z_sel = "Pintura"
            if m_r.button("Med R"): st.session_state.z_sel = "Med-R"
            st.info(f"Seleccionado: **{st.session_state.j_sel}** en **{st.session_state.z_sel}**")

        with col_der: # ACCIONES COMPLETAS
            st.write("📝 **ACCIÓN**")
            # Tiros Metidos / Fallados
            c1, c2 = st.columns(2)
            if c1.button("✅ METIDO", use_container_width=True):
                p = 3 if "T3" in st.session_state.z_sel else 2
                registrar("MET", p)
            if c2.button("❌ FALLO", use_container_width=True): registrar("FAL", 0)
            
            # Estadísticas de Juego
            st.write("**STATS**")
            s1, s2, s3 = st.columns(3)
            if s1.button("AST"): registrar("AST", 0)
            if s2.button("REB"): registrar("REB", 0)
            if s3.button("ROBO"): registrar("ROBO", 0)
            
            st.write("**FILOSOFÍA**")
            f1, f2, f3 = st.columns(3)
            if f1.button("PT"): registrar("PT", 0)
            if f2.button("ExtraP"): registrar("ExtraP", 0)
            if f3.button("TOV"): registrar("TOV", 0)

            st.divider()
            # Rival y Posesión
            if st.button("⚠️ CANASTA RIVAL", use_container_width=True): registrar("RIVAL", 2, "Rival")
            if st.button("🏁 SIGUIENTE POSESIÓN", type="primary", use_container_width=True):
                st.session_state.pos_n += 1
                st.session_state.j_sel = None
                st.rerun()

# --- HISTORIAL Y DESCARGA ---
if st.session_state.log:
    with st.expander("📋 Ver Log y Descargar"):
        df = pd.DataFrame(st.session_state.log)
        st.dataframe(df.iloc[::-1])
        st.download_button("📥 DESCARGAR CSV", df.to_csv(index=False), "partido.csv")
