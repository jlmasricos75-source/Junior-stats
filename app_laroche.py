import streamlit as st
import pandas as pd
import datetime

# Configuración de página
st.set_page_config(page_title="MVP ANALYTICS v46", layout="wide", initial_sidebar_state="collapsed")

# --- CSS MEJORADO PARA LAPTOP/IPAD ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; height: 3.5em; font-weight: bold; border-radius: 10px; }
    .pos-header { background-color: #1e3a8a; color: white; padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 10px; font-size: 24px; }
    .stat-box { background-color: #f0f2f6; padding: 10px; border-radius: 10px; text-align: center; border: 2px solid #1e3a8a; }
    .bonus-flag { background-color: #ff4b4b; color: white; padding: 10px; border-radius: 5px; text-align: center; font-weight: bold; animation: blinker 1.5s linear infinite; }
    @keyframes blinker { 50% { opacity: 0.5; } }
    .court-container { background-color: #f4d0a0; padding: 20px; border-radius: 15px; border: 3px solid #333; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- ROSTERS ---
JUNIOR_A = ["3.NACHO SERRA", "8.OSCAR MORANA", "15.JOAN AMER", "18.GABI OFICIAL", "21.MARC ALÓS", "50.ADRIAN FERRER", "99.PEPE MÁS"]
JUNIOR_B = ["2.LUCAS MÁS", "5.ADRIÁN OJEDA", "9.ANDREU ESTELLÉS", "11.ALEJANDRO PELLICER", "12.DAVID NAVÍO", "23.ANTONIO PERANDRÉS", "24.CARLOS MÁS", "28.DERIN AKYUZ", "32.GONZALO R.", "82.MIGUEL DOLZ"]

# --- INICIALIZACIÓN DE VARIABLES (Evita errores de carga) ---
if 'log' not in st.session_state: st.session_state.log = []
if 'fase' not in st.session_state: st.session_state.fase = "CONFIG"
if 'pos_n' not in st.session_state: st.session_state.pos_n = 1
if 'inv_en_pos' not in st.session_state: st.session_state.inv_en_pos = 0
if 'pt_en_pos' not in st.session_state: st.session_state.pt_en_pos = 0
if 'j_sel' not in st.session_state: st.session_state.j_sel = None
if 'z_sel' not in st.session_state: st.session_state.z_sel = "PINTURA"
if 'periodo' not in st.session_state: st.session_state.periodo = "1Q"
if 'estado_cuarto' not in st.session_state: st.session_state.estado_cuarto = "PAUSA"
if 'pista' not in st.session_state: st.session_state.pista = []
if 'rivales' not in st.session_state: st.session_state.rivales = []

# --- MOTOR DE REGISTRO ---
def registrar(accion, pts, tipo="Local", detalle=""):
    if st.session_state.estado_cuarto == "PAUSA":
        st.error("⚠️ El reloj está en PAUSA. Pulsa INICIAR."); return
    
    jugador = st.session_state.j_sel if tipo == "Local" else "RIVAL"
    
    st.session_state.log.append({
        "Pos#": st.session_state.pos_n,
        "Invs_en_Ataque": st.session_state.inv_en_pos,
        "PT_en_Ataque": st.session_state.pt_en_pos,
        "Q": st.session_state.periodo,
        "Jugador": jugador,
        "Accion": accion,
        "Zona": st.session_state.z_sel,
        "Pts": pts,
        "Tipo": tipo,
        "Detalle": detalle,
        "Reloj": datetime.datetime.now().strftime("%M:%S")
    })
    st.toast(f"✅ Registrado: {accion} (+{pts} pts)")
    # Reset de jugador tras puntos o falta
    if pts > 0 or "FALTA" in accion or "FALLO" in accion:
        st.session_state.j_sel = None

# --- PANTALLA 1: CONFIGURACIÓN ---
if st.session_state.fase == "CONFIG":
    st.title("📋 CONFIGURACIÓN DE PARTIDO")
    cat = st.radio("Categoría:", ["JUNIOR A", "JUNIOR B"], horizontal=True)
    pool = JUNIOR_A + JUNIOR_B if cat == "JUNIOR A" else JUNIOR_B
    
    col1, col2 = st.columns(2)
    with col1:
        conv = st.multiselect("Jugadores convocados:", pool, default=pool[:7])
        st.session_state.pista = st.multiselect("Quinteto Inicial (5):", conv, max_selections=5)
    with col2:
        st.session_state.riv_raw = st.text_input("Dorsales Rival (ej: 4, 10, 11):", "4, 5, 6")
    
    if st.button("🏟️ EMPEZAR PARTIDO", type="primary", use_container_width=True):
        if len(st.session_state.pista) == 5:
            st.session_state.rivales = [r.strip() for r in st.session_state.riv_raw.split(",")]
            st.session_state.fase = "PARTIDO"
            st.rerun()
        else:
            st.warning("Debes seleccionar exactamente 5 titulares.")

# --- PANTALLA 2: PARTIDO (SCRATCH) ---
else:
    # MARCADOR Y POSESIÓN
    pts_l = sum(d['Pts'] for d in st.session_state.log if d['Tipo'] == "Local")
    pts_r = sum(d['Pts'] for d in st.session_state.log if d['Tipo'] == "Rival")
    
    st.markdown(f'<div class="pos-header">POSESIÓN #{st.session_state.pos_n} | LOCAL {pts_l} - {pts_r} RIVAL</div>', unsafe_allow_html=True)
    
    # INDICADORES DE ÉXITO EN LA POSESIÓN ACTUAL
    c_m1, c_m2, c_m3 = st.columns([1, 1, 2])
    with c_m1: st.markdown(f'<div class="stat-box">🔄 Inversiones: <b>{st.session_state.inv_en_pos}</b></div>', unsafe_allow_html=True)
    with c_m2: st.markdown(f'<div class="stat-box">🎨 PT: <b>{st.session_state.pt_en_pos}</b></div>', unsafe_allow_html=True)
    with c_m3:
        if st.button("🆕 NUEVA POSESIÓN (Cambio Balón)", type="primary"):
            st.session_state.pos_n += 1
            st.session_state.inv_en_pos = 0
            st.session_state.pt_en_pos = 0
            st.rerun()

    # CONTROL DE TIEMPO Y FALTAS (BONUS)
    t1, t2, t3 = st.columns(3)
    with t1:
        f_l = sum(1 for d in st.session_state.log if d['Tipo'] == "Local" and "FALTA" in d['Accion'] and d['Q'] == st.session_state.periodo)
        if f_l >= 4: st.markdown('<div class="bonus-flag">🚩 BONUS LOCAL</div>', unsafe_allow_html=True)
        else: st.metric("Faltas L", f_l)
    with t2:
        st.session_state.periodo = st.selectbox("Cuarto:", ["1Q","2Q","3Q","4Q","OT"], label_visibility="collapsed")
        btn_reloj = "▶️ JUGANDO" if st.session_state.estado_cuarto == "PAUSA" else "⏸️ PAUSA"
        if st.button(btn_reloj, use_container_width=True):
            st.session_state.estado_cuarto = "JUGANDO" if st.session_state.estado_cuarto == "PAUSA" else "PAUSA"
            st.rerun()
    with t3:
        f_r = sum(1 for d in st.session_state.log if d['Tipo'] == "Rival" and "FALTA" in d['Accion'] and d['Q'] == st.session_state.periodo)
        if f_r >= 4: st.markdown('<div class="bonus-flag">🚩 BONUS RIVAL</div>', unsafe_allow_html=True)
        else: st.metric("Faltas R", f_r
