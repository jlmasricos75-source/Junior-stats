import streamlit as st
import pandas as pd
import datetime
import time

# 1. CONFIGURACIÓN iPAD / MAC (Touch Targets > 44px)
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

# 2. ROSTERS OFICIALES (Ordenados por Dorsal)
ROSTERS = {
    "JUNIOR A":,
    "JUNIOR B":
}

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
if 'rivales' not in st.session_state: st.session_state.rivales = ["4", "7", "10", "15"]

def registrar(accion, pts, tipo="Local", detalle=""):
    if st.session_state.estado_cuarto == "PAUSA":
        st.error("⚠️ Pulsa INICIAR CUARTO"); return
    
    jugador = st.session_state.j_sel if tipo == "Local" else "RIVAL"
    st.session_state.log.append({
        "Pos#": st.session_state.pos_n,
        "Invs": st.session_state.inv_en_pos,
        "PT": st.session_state.pt_en_pos,
        "Q": st.session_state.periodo,
        "Jugador": jugador, "Accion": accion, "Zona": st.session_state.z_sel,
        "Pts": pts, "Tipo": tipo, "Detalle": detalle,
        "Hora": datetime.datetime.now().strftime("%M:%S")
    })
    st.toast(f"✅ {accion} (+{pts})")
    if pts > 0 or "FALTA" in accion or "FALLO" in accion:
        st.session_state.j_sel = None

def get_faltas(periodo, tipo):
    contar = [periodo] if periodo!= "OT" else
    return sum(1 for d in st.session_state.log if d == tipo and "FALTA" in d['Accion'] and d['Q'] in contar)

# --- FASE 1: CONFIGURACIÓN ---
if st.session_state.fase == "CONFIG":
    st.title("📋 CARGA DE PARTIDO")
    eq_sel = st.radio("Equipo:",, horizontal=True)
    conv = st.multiselect("Convocados:", sorted(ROSTERS[eq_sel], key=lambda x: int(x.split('.'))), default=ROSTERS[eq_sel][:12])
    st.session_state.pista = st.multiselect("Quinteto Inicial (5):", conv, max_selections=5)
    st.session_state.riv_raw = st.text_input("Dorsales Rival (comas):", "4, 5, 10, 12")
    vid = st.file_uploader("Vídeo (Opcional):", type=["mp4"])
    if vid: st.session_state.video_data = vid

    if len(st.session_state.pista) == 5:
        if st.button("🚀 INICIAR PARTIDO", type="primary"):
            st.session_state.convocados = conv
            st.session_state.rivales = [r.strip() for r in st.session_state.riv_raw.split(",")]
            st.session_state.fase = "PARTIDO"; st.rerun()

# --- FASE 2: PARTIDO ---
elif st.session_state.fase == "PARTIDO":
    # Marcador y Bonus
    l_pts = sum(d['Pts'] for d in st.session_state.log if d == "Local")
    r_pts = sum(d['Pts'] for d in st.session_state.log if d == "Rival")
    f_loc = get_faltas(st.session_state.periodo, "Local")
    f_riv = get_faltas(st.session_state.periodo, "Rival")

    st.markdown(f'<div class="pos-header">POS #{st.session_state.pos_n} | LOCAL {l_pts} - {r_pts} RIVAL</div>', unsafe_allow_html=True)
    
    c_st1, c_st2, c_st3 = st.columns([1, 1, 2])
    with c_st1: st.markdown(f'<div class="stat-box">🔄 INVS: {st.session_state.inv_en_pos}</div>', unsafe_allow_html=True)
    with c_st2: st.markdown(f'<div class="stat-box">🎨 PT: {st.session_state.pt_en_pos}</div>', unsafe_allow_html=True)
    with c_st3:
        if st.button("🆕 NUEVA POSESIÓN (Cambio Balón)", type="primary"):
            st.session_state.pos_n += 1; st.session_state.inv_en_pos = 0; st.session_state.pt_en_pos = 0; st.rerun()

    t1, t2, t3 = st.columns(3)
    with t1:
        if f_loc >= 4: st.markdown('<div class="bonus-flag">🚩 BONUS LOCAL</div>', unsafe_allow_html=True)
        else: st.metric("Faltas L", f_loc)
    with t2:
        st.session_state.periodo = st.selectbox("Cuarto",, label_visibility="collapsed")
        lab = "▶️ START" if st.session_state.estado_cuarto == "PAUSA" else "⏸️ PAUSA"
        if st.button(lab, use_container_width=True):
            st.session_state.estado_cuarto = "JUGANDO" if st.session_state.estado_cuarto == "PAUSA" else "PAUSA"; st.rerun()
    with t3:
        if f_riv >= 4: st.markdown('<div class="bonus-flag">🚩 BONUS RIVAL</div>', unsafe_allow_html=True)
        else: st.metric("Faltas R", f_riv)

    if 'video_data' in st.session_state: st.video(st.session_state.video_data)

    st.divider()
    col_j, col_c, col_a = st.columns([1, 2, 1])

    with col_j: # PISTA
        st.caption("🏃 EN PISTA")
        for j in st.session_state.pista:
            p_j = sum(d['Pts'] for d in st.session_state.log if d['Jugador'] == j)
            f_j = sum(1 for d in st.session_state.log if d['Jugador'] == j and "FALTA" in d['Accion'])
            color = "primary" if st.session_state.j_sel == j else "secondary"
            if st.button(f"{j.split('.')} ({p_j}p|{f_j}F)", key=f"j_{j}", type=color):
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
        p1, p2, p3 = st.columns(3)
        if p1.button("✅ 1P"): registrar("METIDO", 1)
        if p2.button("✅ 2P"): registrar("METIDO", 2)
        if p3.button("✅ 3P"): registrar("METIDO", 3)
        
        f_lib, f_for = st.columns(2)
        if f_lib.button("⭕ FALLO (LIBRE)"): registrar("FALLO_LIBRE", 0)
        if f_for.button("❌ FALLO (FORZADO)"): registrar("FALLO_FORZADO", 0)

        st.caption("🏀 REBOTES")
        if st.button("📥 REB DEF"): registrar("REB_DEF", 0)
        if st.button("🚀 REB OFF"): registrar("REB_OFF", 0)

    with col_a: # ADN Y RIVAL
        st.caption("🧠 ADN")
        if st.button("🔄 INVERSIÓN", type="primary"): st.session_state.inv_en_pos += 1; registrar("INVERSION", 0)
        if st.button("🎨 PT"): st.session_state.pt_en_pos += 1; registrar("PT", 0)
        
        c_a1, c_a2 = st.columns(2)
        if c_a1.button("🧤 ROBO"): registrar("ROBO", 0)
        if c_a2.button("🟥 FALTA"): registrar("FALTA", 0)
        if c_a1.button("🤝 AST"): registrar("ASISTENCIA", 0)
        if c_a2.button("📉 PERD"): registrar("PERDIDA", 0)
        
        st.write("---")
        st.caption("🚫 RIVAL")
        riv_sel = st.selectbox("Dorsal:", st.session_state.rivales, label_visibility="collapsed")
        r1, r2 = st.columns(2)
        if r1.button("R2 ✅"): registrar("RIVAL-2", 2, "Rival")
        if r2.button("R3 ✅"): registrar("RIVAL-3", 3, "Rival")
        if r1.button("R-FAL"): registrar("F_RIV", 0, "Rival")
        if r2.button("R-TOV"): registrar("P_RIV", 0, "Rival")

# --- PANTALLA 3: CAMBIOS ---
elif st.session_state.fase == "CAMBIOS":
    st.title("🔄 CAMBIO EN BLOQUE")
    pool_cambio = sorted(st.session_state.convocados, key=lambda x: int(x.split('.')))
    nueva_pista = st.multiselect("Quinteto en pista:", pool_cambio, default=list(st.session_state.pista), max_selections=5)
    if st.button("✅ CONFIRMAR", type="primary") and len(nueva_pista) == 5:
        st.session_state.pista = nueva_pista
        st.session_state.fase = "PARTIDO"; st.rerun()
    if st.button("❌ CANCELAR"): st.session_state.fase = "PARTIDO"; st.rerun()

# --- SIDEBAR: LOG ---
if st.session_state.log:
    with st.sidebar:
        df = pd.DataFrame(st.session_state.log)
        st.download_button("📥 DESCARGAR CSV", df.to_csv(index=False), "partido.csv")
        st.dataframe(df.iloc[::-1], use_container_width=True)
