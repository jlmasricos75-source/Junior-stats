import streamlit as st
import pandas as pd
import datetime

st.set_page_config(page_title="MVP ANALYTICS v45", layout="wide", initial_sidebar_state="collapsed")

# --- ESTILOS ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; height: 3.2em; font-weight: bold; border-radius: 10px; }
    .pos-header { background-color: #2e7d32; color: white; padding: 10px; border-radius: 10px; text-align: center; margin-bottom: 5px; }
    .stat-box { background-color: #f0f2f6; padding: 5px; border-radius: 5px; text-align: center; border: 1px solid #d1d1d1; }
    .bonus-flag { background-color: #ff4b4b; color: white; padding: 10px; border-radius: 5px; text-align: center; animation: blinker 1.5s linear infinite; }
    @keyframes blinker { 50% { opacity: 0.5; } }
    </style>
    """, unsafe_allow_html=True)

# --- ROSTERS ---
JUNIOR_A = ["3.NACHO SERRA", "8.OSCAR MORANA", "15.JOAN AMER", "18.GABI OFICIAL", "21.MARC ALÓS", "50.ADRIAN FERRER", "99.PEPE MÁS"]
JUNIOR_B = ["2.LUCAS MÁS", "5.ADRIÁN OJEDA", "9.ANDREU ESTELLÉS", "11.ALEJANDRO PELLICER", "12.DAVID NAVÍO", "23.ANTONIO PERANDRÉS", "24.CARLOS MÁS", "28.DERIN AKYUZ", "32.GONZALO R.", "82.MIGUEL DOLZ"]

# --- INICIALIZACIÓN ---
if 'log' not in st.session_state: st.session_state.log = []
if 'fase' not in st.session_state: st.session_state.fase = "CONFIG"
if 'pos_n' not in st.session_state: st.session_state.pos_n = 1
if 'inv_en_pos' not in st.session_state: st.session_state.inv_en_pos = 0 # Inversiones en posesión actual
if 'pt_en_pos' not in st.session_state: st.session_state.pt_en_pos = 0   # PT en posesión actual
if 'j_sel' not in st.session_state: st.session_state.j_sel = None
if 'z_sel' not in st.session_state: st.session_state.z_sel = "PINTURA"
if 'estado_cuarto' not in st.session_state: st.session_state.estado_cuarto = "PAUSA"

def registrar(accion, pts, tipo="Local", extra=""):
    if st.session_state.estado_cuarto == "PAUSA":
        st.error("⚠️ El reloj está parado"); return
    
    jugador = st.session_state.j_sel if tipo == "Local" else "RIVAL"
    st.session_state.log.append({
        "Pos#": st.session_state.pos_n,
        "Invs_Pos": st.session_state.inv_en_pos,
        "PT_Pos": st.session_state.pt_en_pos,
        "Q": st.session_state.periodo, "Jugador": jugador, "Accion": accion,
        "Zona": st.session_state.z_sel, "Pts": pts, "Tipo": tipo,
        "Detalle": extra, "Hora": datetime.datetime.now().strftime("%M:%S")
    })
    st.toast(f"✅ Registrado: {accion}")
    if pts > 0 or "FALTA" in accion: st.session_state.j_sel = None

# --- FASE 1: CONFIG ---
if st.session_state.fase == "CONFIG":
    st.title("🏀 SCRATCH JUNIOR - CONFIG")
    cat = st.radio("Equipo:", ["JUNIOR A", "JUNIOR B"], horizontal=True)
    pool = JUNIOR_A + JUNIOR_B if cat == "JUNIOR A" else JUNIOR_B
    conv = st.multiselect("Acta:", pool, default=pool[:7])
    st.session_state.pista = st.multiselect("Quinteto:", conv, max_selections=5)
    st.session_state.riv_raw = st.text_input("Dorsales Rival:", "4, 5, 6")
    if st.button("🚀 EMPEZAR PARTIDO") and len(st.session_state.pista) == 5:
        st.session_state.rivales = [r.strip() for r in st.session_state.riv_raw.split(",")]
        st.session_state.fase = "PARTIDO"; st.rerun()

# --- FASE 2: PARTIDO ---
else:
    # 1. MARCADOR Y STATUS DE POSESIÓN
    loc_pts = sum(d['Pts'] for d in st.session_state.log if d['Tipo'] == "Local")
    riv_pts = sum(d['Pts'] for d in st.session_state.log if d['Tipo'] == "Rival")
    
    st.markdown(f'<div class="pos-header">POSESIÓN #{st.session_state.pos_n} | {loc_pts} - {riv_pts}</div>', unsafe_allow_html=True)
    
    # 2. TRACKING EN VIVO DE LA POSESIÓN ACTUAL
    c_inv, c_pt, c_new = st.columns([1, 1, 2])
    with c_inv: st.markdown(f'<div class="stat-box">🔄 Inversiones: <b>{st.session_state.inv_en_pos}</b></div>', unsafe_allow_html=True)
    with c_pt: st.markdown(f'<div class="stat-box">🎨 PT: <b>{st.session_state.pt_en_pos}</b></div>', unsafe_allow_html=True)
    with c_new:
        if st.button("🆕 SIGUIENTE POSESIÓN", type="primary"):
            st.session_state.pos_n += 1
            st.session_state.inv_en_pos = 0
            st.session_state.pt_en_pos = 0
            st.rerun()

    # 3. TIEMPO Y BONUS
    t1, t2, t3 = st.columns(3)
    with t1: 
        f_loc = sum(1 for d in st.session_state.log if d['Tipo'] == "Local" and "FALTA" in d['Accion'] and d['Q'] == st.session_state.periodo)
        if f_loc >= 4: st.markdown('<div class="bonus-flag">🚩 BONUS LOCAL</div>', unsafe_allow_html=True)
        else: st.metric("Faltas L", f_loc)
    with t2:
        st.session_state.periodo = st.selectbox("Q", ["1Q","2Q","3Q","4Q","OT"], label_visibility="collapsed")
        lab = "▶️ JUGANDO" if st.session_state.estado_cuarto == "PAUSA" else "⏸️ PAUSA"
        if st.button(lab): st.session_state.estado_cuarto = "JUGANDO" if st.session_state.estado_cuarto == "PAUSA" else "PAUSA"; st.rerun()
    with t3:
        f_riv = sum(
