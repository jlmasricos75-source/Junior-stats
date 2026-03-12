import streamlit as st
import pandas as pd
import datetime
import time

# 1. OPTIMIZACIÓN DE RENDIMIENTO Y UI (Touch targets > 44px)
st.set_page_config(page_title="METRICAS JUNIOR PRO", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
   .stButton>button { width: 100%; height: 4.5em; font-weight: bold; border-radius: 12px; margin-bottom: 5px; touch-action: manipulation; }
   .pos-header { background-color: #1e3a8a; color: white; padding: 15px; border-radius: 15px; text-align: center; font-size: 24px; font-weight: bold; }
   .stat-box { background-color: #f8f9fa; padding: 10px; border-radius: 10px; text-align: center; border: 2px solid #1e3a8a; }
   .bonus-flag { background-color: #ff4b4b; color: white; padding: 10px; border-radius: 5px; text-align: center; font-weight: bold; animation: blinker 1.5s linear infinite; }
    @keyframes blinker { 50% { opacity: 0.5; } }
   .court-container { background-color: #f4d0a0; padding: 20px; border-radius: 15px; border: 3px solid #333; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# 2. ROSTERS OFICIALES
JUNIOR_A_FIJOS =
JUNIOR_B_FIJOS =

# 3. INICIALIZACIÓN DE ESTADOS
if 'log' not in st.session_state: st.session_state.log =
if 'fase' not in st.session_state: st.session_state.fase = "CONFIG"
if 'pos_n' not in st.session_state: st.session_state.pos_n = 1
if 'inv_en_pos' not in st.session_state: st.session_state.inv_en_pos = 0
if 'pt_en_pos' not in st.session_state: st.session_state.pt_en_pos = 0
if 'j_sel' not in st.session_state: st.session_state.j_sel = None
if 'z_sel' not in st.session_state: st.session_state.z_sel = "PINTURA"
if 'periodo' not in st.session_state: st.session_state.periodo = "1Q"
if 'estado_cuarto' not in st.session_state: st.session_state.estado_cuarto = "PAUSA"
if 'pista' not in st.session_state: st.session_state.pista =
if 'convocados' not in st.session_state: st.session_state.convocados =

def registrar(accion, pts, tipo="Local", detalle=""):
    if st.session_state.estado_cuarto == "PAUSA":
        st.error("⚠️ El cuarto está en PAUSA. Pulsa INICIAR."); return
    
    jugador = st.session_state.j_sel if tipo == "Local" else "RIVAL"
    st.session_state.log.append({
        "Pos#": st.session_state.pos_n, "Invs": st.session_state.inv_en_pos, "PT": st.session_state.pt_en_pos,
        "Q": st.session_state.periodo, "Jugador": jugador, "Accion": accion, "Zona": st.session_state.z_sel,
        "Pts": pts, "Tipo": tipo, "Detalle": detalle, "Hora": datetime.datetime.now().strftime("%M:%S")
    })
    st.toast(f"✅ Registrado: {accion}")
    if pts > 0 or "FALTA" in accion or "FALLO" in accion: st.session_state.j_sel = None

def get_faltas_periodo(tipo_eq):
    periodos = [st.session_state.periodo] if st.session_state.periodo!= "OT" else
    return sum(1 for d in st.session_state.log if d == tipo_eq and "FALTA" in d['Accion'] and d['Q'] in periodos)

# --- FASE 1: CONFIGURACIÓN ---
if st.session_state.fase == "CONFIG":
    st.title("📋 CARGA DE PARTIDO")
    eq_tipo = st.radio("Equipo:",, horizontal=True)
    pool = JUNIOR_A_FIJOS + JUNIOR_B_FIJOS if eq_tipo == "JUNIOR A" else JUNIOR_B_FIJOS
    
    col1, col2 = st.columns(2)
    with col1:
        conv = st.multiselect("Convocados hoy (12 máx):", sorted(pool, key=lambda x: int(x.split('.'))), default=pool[:min(12, len(pool))])
        st.session_state.pista = st.multiselect("Quinteto Inicial (5):", conv, max_selections=5)
    with col2:
        st.session_state.riv_raw = st.text_input("Dorsales Rival (separar por comas):", "4, 7, 10, 11")
        vid = st.file_uploader("Vídeo para Scouting (Opcional):", type=["mp4"])
        if vid: st.session_state.video_data = vid

    if len(st.session_state.pista) == 5:
        if st.button("🚀 INICIAR PARTIDO", type="primary", use_container_width=True):
            st.session_state.convocados = conv
            st.session_state.rivales = [r.strip() for r in st.session_state.riv_raw.split(",")]
            st.session_state.fase = "PARTIDO"; st.rerun()

# --- FASE 2: PARTIDO ---
elif st.session_state.fase == "PARTIDO":
    pts_l = sum(d['Pts'] for d in st.session_state.log if d == "Local")
    pts_r = sum(d['Pts'] for d in st.session_state.log if d == "Rival")
    f_l = get_faltas_periodo("Local")
    f_r = get_faltas_periodo("Rival")

    st.markdown(f'<div class="pos-header">POS #{st.session_state.pos_n} | LOCAL {pts_l} - {pts_r} RIVAL</div>', unsafe_allow_html=True)
    
    c_m1, c_m2, c_m3 = st.columns([1, 1, 2])
    with c_m1: st.markdown(f'<div class="stat-box">🔄 INVS: {st.session_state.inv_en_pos}</div>', unsafe_allow_html=True)
    with c_m2: st.markdown(f'<div class="stat-box">🎨 PT: {st.session_state.pt_en_pos}</div>', unsafe_allow_html=True)
    with c_m3:
        if st.button("🆕 SIGUIENTE POSESIÓN / CAMBIO BALÓN", type="primary"):
            st.session_state.pos_n += 1; st.session_state.inv_en_pos = 0; st.session_state.pt_en_pos = 0; st.rerun()

    t1, t2, t3 = st.columns(3)
    with t1:
        if f_l >= 4: st.markdown('<div class="bonus-flag">🚩 BONUS LOCAL</div>', unsafe_allow_html=True)
        else: st.metric("Faltas L", f_l)
    with t2:
        st.session_state.periodo = st.selectbox("Cuarto:",, label_visibility="collapsed")
        label_reloj = "▶️ INICIAR CUARTO" if st.session_state.estado_cuarto == "PAUSA" else "⏸️ FINALIZAR CUARTO"
        if st.button(label_reloj, use_container_width=True):
            st.session_state.estado_cuarto = "JUGANDO" if st.session_state.estado_cuarto == "PAUSA" else "PAUSA"; st.rerun()
    with t3:
        if f_r >= 4: st.markdown('<div class="bonus-flag">🚩 BONUS RIVAL</div>', unsafe_allow_html=True)
        else: st.metric("Faltas R", f_r)

    if 'video_data' in st.session_state: st.video(st.session_state.video_data)

    st.divider()
    col_j, col_c, col_a = st.columns([1, 2, 1])

    with col_j: # PISTA Y JUGADORES
        st.caption("🏃 PISTA (+/- TRACK)")
        for j in st.session_state.pista:
            pj = sum(d['Pts'] for d in st.session_state.log if d['Jugador'] == j)
            fj = sum(1 for d in st.session_state.log if d['Jugador'] == j and "FALTA" in d['Accion'])
            color = "primary" if st.session_state.j_sel == j else "secondary"
            if st.button(f"{j.split('.')} ({pj}p | {fj}F)", key=f"j_{j}", type=color):
                st.session_state.j_sel = j; st.rerun()
        if st.button("🔄 CAMBIOS (BLOQUE)", type="primary"): st.session_state.fase = "CAMBIOS"; st.rerun()

    with col_c: # CAMPO Y TIRO
        st.markdown('<div class="court-container">', unsafe_allow_html=True)
        z1, z2, z3 = st.columns(3)
        if z1.button("ESQ IZQ"): st.session_state.z_sel = "ESQ_IZQ"
        if z2.button("TRIPLE F"): st.session_state.z_sel = "TRIPLE_F"
        if z3.button("ESQ DER"): st.session_state.z_sel = "ESQ_DER"
        m1, m2, m3 = st.columns([1, 1.5, 1])
        if m1.button("45º IZQ"): st.session_state.z_sel = "45_IZQ"
        if m2.button("🟦 PINTURA", type="primary"): st.session_state.z_sel = "PINTURA"
        if m3.button("45º DER"): st.session_state.z_sel = "45_DER"
        st.markdown('</div>', unsafe_allow_html=True)

        st.caption("🎯 FINALIZAR TIRO")
        p1, p2, p3, pf = st.columns(4)
        if p1.button("✅ 1P"): registrar("CANASTA", 1)
        if p2.button("✅ 2P"): registrar("CANASTA", 2)
        if p3.button("✅ 3P"): registrar("CANASTA", 3)
        if pf.button("⭕ FALLO"): registrar("FALLO",
